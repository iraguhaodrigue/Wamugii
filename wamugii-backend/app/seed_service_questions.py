"""
SAMPLE per-service quote questions, so a fresh install has something to look at.

    python -m app.seed_service_questions

This is sample data, not reference data. Real questions are admin-created
through the Services admin screen, and the wording here is a plausible starting
point rather than WAMUGII's actual intake criteria -- review and edit it rather
than treating it as settled.

Idempotent on two axes, so it is safe to re-run and safe to run on a database
that is already in use:

* a question is matched by (service, question_text) and skipped if present,
  so re-running never duplicates;
* a question an admin has since edited or soft-deleted is left alone, so this
  script cannot resurrect something that was deliberately removed.

It does not touch `long_description` or `features` on any service -- that copy
is marketing text and belongs to whoever writes it.
"""

from app.core.database import SessionLocal
from app.crud import service as service_crud
from app.crud import service_question as question_crud
from app.models.service_question import QuestionType
from app.schemas.service_question import ServiceQuestionCreate

# Keyed by service slug. Only the one service the brief named, kept deliberately
# small -- three questions is enough to see the form adapt.
SAMPLE_QUESTIONS: dict[str, list[ServiceQuestionCreate]] = {
    "web-design-development": [
        ServiceQuestionCreate(
            question_text="Roughly how many pages do you need?",
            question_type=QuestionType.NUMBER,
            is_required=True,
            display_order=1,
        ),
        ServiceQuestionCreate(
            question_text="Which features do you need?",
            question_type=QuestionType.MULTISELECT,
            options=[
                "Contact form",
                "Blog or news",
                "Online shop",
                "Online booking",
                "Multi-language",
                "Client login area",
            ],
            is_required=False,
            display_order=2,
        ),
        ServiceQuestionCreate(
            question_text="Do you already have a logo and brand colours?",
            question_type=QuestionType.YES_NO,
            is_required=True,
            display_order=3,
        ),
    ],
}


def main() -> None:
    db = SessionLocal()
    try:
        for slug, questions in SAMPLE_QUESTIONS.items():
            service = service_crud.get_by_slug(db, slug)
            if service is None:
                print(f"Service not found, skipping: {slug} (run app.seed_services first)")
                continue

            # include_inactive: a question an admin soft-deleted still counts as
            # "already handled" -- re-creating it would undo their decision.
            existing = {
                q.question_text
                for q in question_crud.list_for_service(db, service.id, include_inactive=True)
            }

            for question in questions:
                if question.question_text in existing:
                    print(f"  already present: {question.question_text}")
                    continue
                created = question_crud.create(db, service.id, question)
                print(f"  created sample question {created.id}: {created.question_text}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
