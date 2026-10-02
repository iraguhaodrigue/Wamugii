"""
SAMPLE starter content for every WAMUGII service: long description, features,
and a set of per-service quote questions.

    python -m app.seed_all_service_content

Content-seeding only -- the models, schemas and endpoints Phase A built are not
touched. The wording here is a plausible starting point for a fresh install so
no service looks empty; it is not WAMUGII's finalised copy. Review and edit it
through the admin Services screen rather than treating it as settled.

Safety, exactly as `seed_service_questions.py` already does it:

* Services are matched by name. If a name isn't found we skip it and say so,
  rather than guessing or creating a new row.
* `long_description` and `features` are set ONLY when they are currently NULL.
  An admin edit to either (even to the empty string, which would read as "set")
  is never overwritten.
* A question is matched by (service, question_text) across both active AND
  soft-deleted rows, so re-running never duplicates and a question an admin
  has deliberately removed is never resurrected.
* `name`, `slug`, `category` and `price_from` are never touched -- those are
  the seed script's domain, not this one's.

Running it a second time reports every line as "already present".
"""

from app.core.database import SessionLocal
from app.crud import service as service_crud
from app.crud import service_question as question_crud
from app.models.service_question import QuestionType
from app.schemas.service import ServiceUpdate
from app.schemas.service_question import ServiceQuestionCreate


# Keyed by service NAME, per the brief. These are the names seed_services.py
# creates; if any of them are later renamed through a migration or by hand,
# that service drops out of this seed until the entry here is updated too.
SERVICE_CONTENT: dict[str, dict] = {
    # Web Design & Development: the sample questions are already seeded by
    # `seed_service_questions.py`. We only fill in the detail-page copy here,
    # and skip adding questions so we don't duplicate the earlier seed.
    "Web Design & Development": {
        "long_description": (
            "From a single landing page to a full business website, we design and build "
            "sites that are fast, accessible on mobile, and straightforward to edit after "
            "launch. Each project starts with your goals and audience, and the build is "
            "handed over with the documentation you need to run it. If you also need "
            "hosting or a domain, we can set those up alongside the site."
        ),
        "features": [
            "Responsive design that works on phones, tablets and desktops",
            "Content you can edit yourself where that makes sense",
            "Clear site structure built for search engines",
            "Standard accessibility practices (readable contrast, keyboard navigation)",
            "A handover with documentation and basic training",
        ],
        "questions": [],  # already seeded elsewhere
    },

    "Software Development": {
        "long_description": (
            "Custom software built around how your organisation actually works -- web "
            "applications, mobile apps, desktop tools, and internal systems. We start by "
            "understanding the problem, agree on the smallest version that is useful, and "
            "iterate from there. Where it helps, the software plugs into tools you already "
            "use rather than replacing them."
        ),
        "features": [
            "Scoping and planning before any code is written",
            "Iterative delivery so you can try it early and shape it",
            "Testing as part of the build, not an afterthought",
            "Documentation for the people who'll run it after handover",
            "Support options after launch if you want them",
        ],
        "questions": [
            ServiceQuestionCreate(
                question_text="What kind of software do you need?",
                question_type=QuestionType.SELECT,
                options=["Web application", "Mobile app", "Desktop application",
                         "Internal system / tool", "Not sure yet"],
                is_required=True,
                display_order=1,
            ),
            ServiceQuestionCreate(
                question_text="What are the key features it needs to have?",
                question_type=QuestionType.TEXTAREA,
                is_required=True,
                display_order=2,
            ),
            ServiceQuestionCreate(
                question_text="Roughly how many people will use it?",
                question_type=QuestionType.SELECT,
                options=["Under 10", "10 to 100", "100 to 1,000",
                         "Over 1,000", "Not sure yet"],
                is_required=False,
                display_order=3,
            ),
            ServiceQuestionCreate(
                question_text="Does it need to integrate with existing systems?",
                question_type=QuestionType.YES_NO,
                is_required=False,
                display_order=4,
            ),
        ],
    },

    "Project Development": {
        "long_description": (
            "End-to-end delivery of a defined project with clear goals, milestones and a "
            "handover. Useful when you know what you want to achieve but need a partner to "
            "plan the work, coordinate the pieces and get it over the line. We work with "
            "your constraints -- budget, timeline, people already involved -- rather than "
            "around them."
        ),
        "features": [
            "A written scope you sign off before work starts",
            "Milestones you can see progress against",
            "Regular check-ins so there are no surprises",
            "A single point of contact throughout",
            "A clean handover at the end",
        ],
        "questions": [
            ServiceQuestionCreate(
                question_text="What type of project is it, and in what field?",
                question_type=QuestionType.TEXT,
                is_required=True,
                display_order=1,
            ),
            ServiceQuestionCreate(
                question_text="What is the project's scope and what are its goals?",
                question_type=QuestionType.TEXTAREA,
                is_required=True,
                display_order=2,
            ),
            ServiceQuestionCreate(
                question_text="What timeline do you have in mind?",
                question_type=QuestionType.SELECT,
                options=["Under 1 month", "1 to 3 months", "3 to 6 months",
                         "Over 6 months", "Open / not sure"],
                is_required=False,
                display_order=3,
            ),
            ServiceQuestionCreate(
                question_text="Do you have the requirements documented already?",
                question_type=QuestionType.YES_NO,
                is_required=False,
                display_order=4,
            ),
        ],
    },

    "IT Consultancy": {
        "long_description": (
            "An outside pair of eyes for the IT decisions you're facing: strategy, "
            "security, infrastructure, digitisation. We look at where you are, what's "
            "working, what isn't, and what the right next step actually is -- without "
            "trying to sell you a bigger project than you need. Deliverables are concrete: "
            "a written assessment, specific recommendations and, when it helps, a plan "
            "for how to carry them out."
        ),
        "features": [
            "An honest assessment of where you are today",
            "Prioritised recommendations rather than a long wish-list",
            "Options at different budget levels where relevant",
            "A written report you can share with your team",
            "Follow-up help with execution if you want it",
        ],
        "questions": [
            ServiceQuestionCreate(
                question_text="Which areas are you looking for help with?",
                question_type=QuestionType.MULTISELECT,
                options=["IT strategy", "Security", "Infrastructure",
                         "Digitisation / going paperless", "Software selection", "Other"],
                is_required=True,
                display_order=1,
            ),
            ServiceQuestionCreate(
                question_text="Roughly how large is your organisation?",
                question_type=QuestionType.SELECT,
                options=["Just me / under 5 people", "5 to 25 people",
                         "25 to 100 people", "Over 100 people"],
                is_required=False,
                display_order=2,
            ),
            ServiceQuestionCreate(
                question_text="What problem are you trying to solve?",
                question_type=QuestionType.TEXTAREA,
                is_required=True,
                display_order=3,
            ),
            ServiceQuestionCreate(
                question_text="Is this a one-off piece of work, or ongoing support?",
                question_type=QuestionType.SELECT,
                options=["One-off", "Ongoing / retainer", "Not sure yet"],
                is_required=False,
                display_order=4,
            ),
        ],
    },

    "Hosting & Domains": {
        "long_description": (
            "Hosting that we set up, keep running and renew for you, with the domain "
            "name registered under the same arrangement so there's one point of contact "
            "for both. Plans scale from a simple brochure site up to a production "
            "application, and we're happy to help work out which fits before you commit. "
            "If you already have hosting elsewhere, we can migrate it rather than start "
            "from scratch."
        ),
        "features": [
            "Plan sizing matched to what you actually need, not oversold",
            "Domain registration and renewal handled for you",
            "SSL certificates set up as a matter of course",
            "Email forwarding or mailboxes on your own domain",
            "Someone to call when something isn't working",
        ],
        "questions": [
            ServiceQuestionCreate(
                question_text="Which hosting plan interests you?",
                question_type=QuestionType.SELECT,
                options=["Starter", "Business", "Professional",
                         "Enterprise", "Not sure yet -- advise me"],
                is_required=True,
                display_order=1,
            ),
            ServiceQuestionCreate(
                question_text="Do you also need a domain registered?",
                question_type=QuestionType.YES_NO,
                is_required=True,
                display_order=2,
            ),
            ServiceQuestionCreate(
                question_text="Do you already have a website to host, or is this new?",
                question_type=QuestionType.YES_NO,
                is_required=False,
                display_order=3,
            ),
            ServiceQuestionCreate(
                question_text="What level of traffic do you expect?",
                question_type=QuestionType.SELECT,
                options=["Light (brochure site)", "Moderate (regular visitors)",
                         "Heavy (ecommerce / app)", "Not sure yet"],
                is_required=False,
                display_order=4,
            ),
        ],
    },

    "Installation & IT Solutions": {
        "long_description": (
            "On-site setup of IT equipment and the networks that connect it -- new "
            "offices, growing teams, replacing or extending what you already have. We "
            "plan the layout, do the installation, label everything, and leave you with "
            "a short written record of what's where. If something isn't working on an "
            "existing setup, we can diagnose and fix it rather than always replace."
        ),
        "features": [
            "Site visit and plan before anything is bought or installed",
            "Workstations, printers, networking and cabling",
            "Wi-Fi coverage sized to the space",
            "Clear labelling and a written as-built record",
            "Basic staff orientation once it's live",
        ],
        "questions": [
            ServiceQuestionCreate(
                question_text="What needs to be installed or set up?",
                question_type=QuestionType.TEXTAREA,
                is_required=True,
                display_order=1,
            ),
            ServiceQuestionCreate(
                question_text="Roughly how many devices or machines are involved?",
                question_type=QuestionType.NUMBER,
                is_required=False,
                display_order=2,
            ),
            ServiceQuestionCreate(
                question_text="Where is the site? (city, district or address)",
                question_type=QuestionType.TEXT,
                is_required=True,
                display_order=3,
            ),
            ServiceQuestionCreate(
                question_text="Is this a new setup, or fixing / extending an existing one?",
                question_type=QuestionType.SELECT,
                options=["New setup", "Fixing an existing problem",
                         "Extending an existing setup", "A mix of these"],
                is_required=False,
                display_order=4,
            ),
        ],
    },

    "Research & Technical Support": {
        "long_description": (
            "Mentoring and technical guidance for people learning a technology or working "
            "on a research or professional project of their own. Think of it as a tutor "
            "and sparring partner: we help you understand the material, work through "
            "problems alongside you, and point you at the right next step. This service "
            "is about helping you build the skills, not producing work that will be "
            "submitted as yours when it is not."
        ),
        "features": [
            "One-to-one sessions pitched at your level",
            "Guidance on where to focus and what to read",
            "Help getting unstuck on specific technical problems",
            "Feedback on work you've done yourself",
            "A clear plan if you need one, so sessions build on each other",
        ],
        "questions": [
            ServiceQuestionCreate(
                question_text="What area do you need research or technical support in?",
                question_type=QuestionType.TEXT,
                is_required=True,
                display_order=1,
            ),
            ServiceQuestionCreate(
                question_text="Describe what you're working on and where you're stuck",
                question_type=QuestionType.TEXTAREA,
                is_required=True,
                display_order=2,
            ),
            ServiceQuestionCreate(
                question_text="Is there a deadline you're working to?",
                question_type=QuestionType.TEXT,
                is_required=False,
                display_order=3,
            ),
            ServiceQuestionCreate(
                question_text="What level is this at?",
                question_type=QuestionType.SELECT,
                options=["Undergraduate study", "Masters / postgraduate",
                         "Professional / at work", "Personal learning", "Other"],
                is_required=False,
                display_order=4,
            ),
        ],
    },

    "Electronics & Technology": {
        "long_description": (
            "Sourcing of electronics and technology products -- for individuals, offices "
            "and projects. If you know what you need, send us the spec; if you don't, we "
            "help you narrow it down against what you're actually going to use it for. "
            "Where it matters we recommend better-value alternatives rather than default "
            "to the most expensive option."
        ),
        "features": [
            "Help choosing the right spec for the job",
            "Quotes against several options where it makes sense",
            "Delivery arranged with the order",
            "Setup and basic configuration if you want it",
            "A record of what was supplied, for your own files",
        ],
        "questions": [
            ServiceQuestionCreate(
                question_text="What product or category are you looking for?",
                question_type=QuestionType.TEXT,
                is_required=True,
                display_order=1,
            ),
            ServiceQuestionCreate(
                question_text="How many do you need?",
                question_type=QuestionType.NUMBER,
                is_required=False,
                display_order=2,
            ),
            ServiceQuestionCreate(
                question_text="Any specific brand, model or spec preference?",
                question_type=QuestionType.TEXTAREA,
                is_required=False,
                display_order=3,
            ),
            ServiceQuestionCreate(
                question_text="Rough budget range?",
                question_type=QuestionType.SELECT,
                options=["Under RWF 500,000", "RWF 500,000 - 2,000,000",
                         "RWF 2,000,000 - 10,000,000", "Over RWF 10,000,000",
                         "Open / advise me"],
                is_required=False,
                display_order=4,
            ),
        ],
    },

    "Beauty Gadgets & Tools": {
        "long_description": (
            "Beauty equipment and tools for salons, individuals, and small businesses "
            "setting up or restocking. We can advise on what's suitable for the use case "
            "you have in mind, help compare options, and arrange delivery. For salon "
            "setups we can quote on a package rather than piece by piece."
        ),
        "features": [
            "Advice on what's suitable for the intended use",
            "Options at different price points",
            "Delivery arranged with the order",
            "Package quotes for salon setups",
            "A record of what was supplied, for your own files",
        ],
        "questions": [
            ServiceQuestionCreate(
                question_text="Which type of product are you looking for?",
                question_type=QuestionType.TEXT,
                is_required=True,
                display_order=1,
            ),
            ServiceQuestionCreate(
                question_text="How many do you need?",
                question_type=QuestionType.NUMBER,
                is_required=False,
                display_order=2,
            ),
            ServiceQuestionCreate(
                question_text="Is this for personal use or for a business?",
                question_type=QuestionType.SELECT,
                options=["Personal / individual use", "Salon or business",
                         "Gift or resale", "Other"],
                is_required=False,
                display_order=3,
            ),
            ServiceQuestionCreate(
                question_text="Any specific preference or requirement?",
                question_type=QuestionType.TEXTAREA,
                is_required=False,
                display_order=4,
            ),
        ],
    },
}


def main() -> None:
    db = SessionLocal()
    try:
        # One pass of list_services keeps the lookups to a single query and
        # also surfaces services this script doesn't know about (which the
        # final summary reports).
        all_services = {
            s.name: s
            for s in service_crud.list_services(db, limit=100, include_inactive=True)
        }

        covered: list[str] = []
        skipped_missing: list[str] = []
        unknown_services = sorted(set(all_services) - set(SERVICE_CONTENT))

        for name, content in SERVICE_CONTENT.items():
            service = all_services.get(name)
            if service is None:
                print(f"SKIP (name not found): {name}")
                skipped_missing.append(name)
                continue

            print(f"\n{name}")
            _apply_detail_copy(db, service, content)
            _apply_questions(db, service, content.get("questions", []))
            covered.append(name)

        print("\n--- summary ---")
        print(f"services with content applied: {len(covered)}")
        for name in covered:
            print(f"  {name}")
        if skipped_missing:
            print(f"services skipped (name not matched): {len(skipped_missing)}")
            for name in skipped_missing:
                print(f"  {name}")
        if unknown_services:
            print(
                f"services in the database this seed does NOT cover: {len(unknown_services)}"
            )
            for name in unknown_services:
                print(f"  {name}")
    finally:
        db.close()


def _apply_detail_copy(db, service, content) -> None:
    """
    Fill in `long_description` and `features` only when they are NULL today.

    Any admin edit -- including setting the field to the empty string, which
    reads as "set" -- blocks the overwrite. That is deliberate: once the admin
    has touched the field it is theirs, and a re-seed must not undo their work.
    """
    long_desc = content.get("long_description")
    features = content.get("features") or []

    update: dict = {}
    if long_desc and service.long_description is None:
        update["long_description"] = long_desc
    if features and service.features is None:
        update["features"] = features

    if not update:
        if service.long_description is not None:
            print("  already present: long_description")
        if service.features is not None:
            print("  already present: features")
        if not long_desc and not features:
            print("  no detail copy configured for this service")
        return

    service_crud.update(db, service, ServiceUpdate(**update))
    for field in update:
        print(f"  set: {field}")


def _apply_questions(db, service, questions) -> None:
    """
    Create each question only when a question with the same text isn't already
    on this service -- including soft-deleted ones, so a question an admin has
    removed is never resurrected.
    """
    if not questions:
        print("  (no questions configured here)")
        return

    existing_texts = {
        q.question_text
        for q in question_crud.list_for_service(db, service.id, include_inactive=True)
    }

    for question in questions:
        if question.question_text in existing_texts:
            print(f"  already present: {question.question_text}")
            continue
        created = question_crud.create(db, service.id, question)
        print(f"  created question {created.id}: {created.question_text}")


if __name__ == "__main__":
    main()
