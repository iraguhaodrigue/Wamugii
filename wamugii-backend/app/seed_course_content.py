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
  file name.

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
from app.models.course import CourseStatus, Lesson
from app.models.user import Role, User
from app.schemas.course import CourseCreate, CourseUpdate, LessonCreate, LessonUpdate, QuizQuestionWrite
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
    for existing in course_crud.list_materials(db, lesson.id):
        if existing.original_filename == nice_name:
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
            fields = dict(
                content=item["content"].strip() + "\n",
                video_url=item.get("video"),
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
