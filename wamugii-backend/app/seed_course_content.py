"""
Load (or update) a full course from a content pack in `app/course_content/`.

    docker exec wamugii-backend python -m app.seed_course_content ai_career_essentials

A content pack is a Python module with a COURSE dict: course details plus
modules -> lessons, each lesson with notes (markdown), study minutes, an
optional video URL and a quiz. PDFs in `app/course_content/pdfs/<slug>/` named
`<NN>.pdf` (NN = lesson number in the course, 01, 02, ...) are attached to the
matching lesson as downloadable materials.

Safe to run again and again -- that is how you publish edits:

* lessons are matched by TITLE, so an existing lesson is updated in place and
  students keep their progress on it;
* lessons that are no longer in the pack are hidden (soft-deleted), never
  hard-deleted;
* each lesson's quiz is replaced with the pack's version;
* a PDF is attached only if the lesson doesn't already have one with the same
  file name (and refreshed when the pack's PDF changed);
* a lesson's "lectures" become its full-lecture videos (extra_videos);
* the final-exam bank is the pack's EXAM list plus every lesson quiz question
  (as a single-answer question tagged with its week). Questions removed from
  the pack are deactivated, never deleted, so past exam results stay readable.

Add `--dry-run` to see what would change without writing anything.
"""

import importlib
import random
import sys
import zlib
from pathlib import Path

from sqlalchemy import select

from app.core.database import SessionLocal
from app.crud import course as course_crud
from app.crud import exam as exam_crud
from app.models.course import CourseStatus, ExamQuestionKind, Lesson
from app.models.user import Role, User
from app.schemas.course import CourseCreate, CourseUpdate, LessonCreate, LessonUpdate, QuizQuestionWrite
from app.schemas.exam import ExamQuestionWrite
from app.services import storage

PDF_ROOT = Path(__file__).parent / "course_content" / "pdfs"
MAX_PDF_BYTES = 25 * 1024 * 1024


def _flatten(course: dict) -> list[dict]:
    """Modules -> one ordered list of lessons, each tagged with its module."""
    out = []
    for module in course["modules"]:
        for lesson in module["lessons"]:
            out.append({**lesson, "module_title": module["title"]})
    for number, lesson in enumerate(out, start=1):
        lesson["number"] = number
    return out


def exam_bank(course: dict, lessons: list[dict]) -> list[ExamQuestionWrite]:
    """
    The pack's EXAM questions plus every lesson quiz question as SINGLE.

    EXAM items are dicts: {"kind", "q", "options", "correct", "why", "topic"}
    where "correct" is option indexes (or accepted answers for FILL_BLANK).
    """
    bank: list[ExamQuestionWrite] = []
    for item in course.get("exam", []):
        bank.append(ExamQuestionWrite(
            kind=ExamQuestionKind(item["kind"]),
            question=item["q"],
            options=item.get("options", []),
            correct=item["correct"],
            explanation=item.get("why", ""),
            topic=item.get("topic"),
        ))
    if course.get("exam_include_quizzes", True):
        for lesson in lessons:
            for question, options, correct, explanation in lesson.get("quiz", []):
                bank.append(ExamQuestionWrite(
                    kind=ExamQuestionKind.SINGLE,
                    question=question,
                    options=options,
                    correct=[correct],
                    explanation=explanation,
                    topic=lesson["module_title"],
                ))
    return bank


def _shuffled(question: str, options: list[str], correct: int) -> tuple[list[str], int]:
    """
    Shuffle a question's options so the right answer isn't always in the same
    place. Seeded from the question text, so every run gives the same order
    (re-running the seed never re-shuffles a quiz a student has seen).
    """
    order = list(range(len(options)))
    random.Random(zlib.crc32(question.encode("utf-8"))).shuffle(order)
    return [options[i] for i in order], order.index(correct)


def _attach_pdf(db, lesson: Lesson, pdf: Path, uploader_id: int) -> bool:
    nice_name = f"{lesson.title}.pdf".replace("/", "-")
    new_bytes = pdf.read_bytes()
    for existing in course_crud.list_materials(db, lesson.id):
        if existing.original_filename == nice_name:
            # Same handout already attached: refresh the file in place when the
            # pack's PDF changed (new video link, edited notes), else skip.
            try:
                target = storage.get_file(existing.storage_path)
                current = target.read_bytes() if target.is_file() else b""
            except (storage.StorageError, OSError):
                return False
            if current == new_bytes:
                return False
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(new_bytes)
            existing.file_size = len(new_bytes)
            db.commit()
            print(f"    ~ PDF refreshed {pdf.name}")
            return False
    with open(pdf, "rb") as fh:
        stored, path, size = storage.save_lesson_material(fh, lesson.id, ".pdf", MAX_PDF_BYTES)
    course_crud.create_material(
        db,
        lesson_id=lesson.id,
        uploaded_by=uploader_id,
        original_filename=nice_name,
        stored_filename=stored,
        storage_path=path,
        content_type="application/pdf",
        file_size=size,
    )
    return True


def load(pack_name: str, dry_run: bool = False) -> None:
    pack = importlib.import_module(f"app.course_content.{pack_name}")
    data = pack.COURSE
    lessons = _flatten(data)
    slug = data["slug"]

    db = SessionLocal()
    try:
        course = course_crud.get_course_by_slug(db, slug)
        meta = dict(
            title=data["title"],
            description=data["description"],
            category=data.get("category"),
            display_order=data.get("display_order", 0),
        )
        if course is None:
            print(f"create course: {data['title']}")
            if dry_run:
                return
            course = course_crud.create_course(
                db,
                CourseCreate(
                    slug=slug,
                    is_free=data.get("is_free", True),
                    price=data.get("price"),
                    status=CourseStatus.PUBLISHED,
                    **meta,
                ),
            )
        else:
            print(f"update course: {course.title}")
            if not dry_run:
                course_crud.update_course(db, course, CourseUpdate(**meta))

        existing = {
            l.title: l for l in course_crud.list_lessons(db, course.id, include_inactive=True)
        }
        wanted = {l["title"] for l in lessons}

        # Hide lessons that left the pack.
        for title, old in existing.items():
            if old.is_active and title not in wanted:
                print(f"  hide lesson: {title}")
                if not dry_run:
                    course_crud.deactivate_lesson(db, old)

        uploader = db.scalar(select(User).where(User.role == Role.ADMIN).order_by(User.id))
        pdf_dir = PDF_ROOT / slug

        for item in lessons:
            lectures = [
                {"title": t, "url": u, "minutes": m} for (t, u, m) in item.get("lectures", [])
            ] or None
            fields = dict(
                content=item["content"].strip() + "\n",
                video_url=item.get("video"),
                extra_videos=lectures,
                module_title=item["module_title"],
                duration_minutes=item.get("minutes"),
                display_order=item["number"],
            )
            lesson = existing.get(item["title"])
            if lesson is None:
                print(f"  add  {item['number']:02d} {item['title']}")
                if dry_run:
                    continue
                lesson = course_crud.create_lesson(
                    db, course.id, LessonCreate(title=item["title"], **fields)
                )
            else:
                print(f"  sync {item['number']:02d} {item['title']}")
                if dry_run:
                    continue
                course_crud.update_lesson(db, lesson, LessonUpdate(is_active=True, **fields))

            quiz = []
            for question, options, correct, explanation in item.get("quiz", []):
                opts, idx = _shuffled(question, options, correct)
                quiz.append(
                    QuizQuestionWrite(question=question, options=opts, correct_index=idx, explanation=explanation)
                )
            course_crud.replace_quiz_questions(db, lesson.id, quiz)

            pdf = pdf_dir / f"{item['number']:02d}.pdf"
            if pdf.is_file():
                if uploader is None:
                    print("    (no ADMIN user yet -- PDF not attached)")
                elif _attach_pdf(db, lesson, pdf, uploader.id):
                    print(f"    + PDF {pdf.name}")

        if not dry_run and data.get("exam") is not None:
            bank = exam_bank(data, lessons)
            n = exam_crud.replace_exam_bank(db, course.id, bank)
            kinds = {}
            for q in bank:
                kinds[q.kind.value] = kinds.get(q.kind.value, 0) + 1
            print(f"exam bank: {n} questions {kinds}")

        total = course_crud.count_active_lessons(db, course.id)
        minutes = course_crud.total_minutes(db, course.id)
        print(f"done: {total} lessons, about {round(minutes / 60)} hours of study")
    finally:
        db.close()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    for name in args:
        load(name, dry_run="--dry-run" in sys.argv)
