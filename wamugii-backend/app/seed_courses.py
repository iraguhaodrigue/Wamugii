"""
Seed the flagship free course: "AI Career Essentials".

Original WAMUGII content -- written in-house, not copied from any external
provider. Safe to run more than once (it skips if the course already exists):

    python -m app.seed_courses

Runs the same way as app.seed / app.seed_services. On the droplet, exec it
inside the running backend container, e.g.:

    docker exec -it <backend-container> python -m app.seed_courses
"""

from app.core.database import SessionLocal
from app.crud import course as course_crud
from app.models.course import CourseStatus
from app.schemas.course import CourseCreate, LessonCreate

COURSE_SLUG = "ai-career-essentials"

COURSE = CourseCreate(
    title="AI Career Essentials",
    slug=COURSE_SLUG,
    category="Career & AI",
    is_free=True,
    status=CourseStatus.PUBLISHED,
    display_order=1,
    description=(
        "A practical, no-jargon introduction to using artificial intelligence "
        "to grow your career. In seven short lessons you'll learn what AI "
        "actually is, how to use everyday AI tools well, how to write prompts "
        "that get real results, and how to apply AI responsibly in your own "
        "field — whether you're a student, a business owner, or a working "
        "professional. Built by WAMUGII TECH SOLUTIONS for people who want to "
        "work smarter and stay ahead, not be left behind."
    ),
)

LESSONS = [
    {
        "title": "What AI Really Is (and Isn't)",
        "content": """\
## The one idea to start with

Artificial intelligence is software that learns patterns from examples instead
of following rules a person wrote by hand. That single idea explains almost
everything you'll meet. A spam filter was once a list of banned words; today it
has *learned* from millions of real emails what spam tends to look like. It was
never taught a rule — it found the pattern.

## Three words you'll keep hearing

- **AI (artificial intelligence)** — the broad goal: machines doing things that
  normally need human thinking.
- **ML (machine learning)** — the main method behind today's AI: learning
  patterns from data.
- **LLM (large language model)** — the kind of AI behind tools like ChatGPT and
  Claude. It learned from a huge amount of text, and it predicts likely words to
  produce useful answers.

## What it is *not*

AI does not "understand" the way you do, and it does not know the truth. An LLM
produces the most *likely* answer, which is usually helpful — but it can sound
completely confident while being wrong. This is called a *hallucination*, and
it's why you always verify anything that matters.

It is also not magic and not conscious. It has no goals of its own and no memory
of you unless a tool is built to keep one.

## Why this matters for your career

You don't need to build AI to benefit from it — just as you didn't need to build
Excel to use a spreadsheet. The people who get ahead in the next few years won't
be "AI experts." They'll be ordinary professionals who know how to *use* these
tools well and where to be careful. That's exactly what the rest of this course
teaches.

**Takeaway:** AI learns patterns from examples, it predicts rather than knows,
and your job is to use it well and check its work.

## Try it yourself

Open any AI assistant and ask it to explain one topic from your field in simple
words. Then find one thing in its answer you should double-check — and check it.
In two minutes you'll have felt both the power and the limit of the tool.
""",
    },
    {
        "title": "The AI-Ready Mindset",
        "content": """\
## Augment, don't abdicate

The most useful way to think about AI is as a *very fast, very well-read
assistant who sometimes gets things wrong*. You stay the professional. It drafts,
summarises, explains, and suggests — you decide, judge, and take responsibility.

People who hand over their thinking entirely get burned: they ship the mistake
the AI made. People who refuse to touch it fall behind. The sweet spot is in the
middle — let it do the heavy lifting, keep your hand on the wheel.

## Where AI genuinely helps

- **Starting** — beating the blank page: a first draft, an outline, a list of
  options.
- **Speeding up** — summarising long documents, reformatting data, writing
  repetitive text.
- **Explaining** — turning something confusing into plain language at your level.
- **Checking** — a second pair of eyes on your writing, logic, or code.

## Where to stay in charge

- Anything where being wrong has real consequences — money, health, legal,
  someone's reputation.
- Anything needing real-world facts that might have changed — verify them.
- Your final judgement and your voice. The AI gives you raw material; the
  decision is yours.

## A simple habit

Before using AI for a task, ask: *"What would 'good' look like, and how will I
check it?"* If you can't tell a good answer from a bad one, you're not ready to
rely on it for that task yet — learn the basics first, then let AI speed you up.

**Takeaway:** treat AI as an assistant that augments your work, never a
replacement for your judgement.

## Try it yourself

Pick one task you do often. In two columns, list the parts AI could help with and
the parts where *you* must stay in charge. Keep this list — it's your own rule
for using AI safely on that task.
""",
    },
    {
        "title": "Core AI Tools for Everyday Work",
        "content": """\
## You already have more than you think

You don't need expensive software to start. Most useful AI today falls into a few
simple categories, and free versions cover most everyday needs.

## The main categories

- **General assistants (chatbots)** — tools like ChatGPT, Claude, and Gemini.
  These are your all-purpose helpers: writing, explaining, planning, coding,
  brainstorming. If you learn one tool well, learn one of these.
- **Search assistants** — tools that answer questions *and* show you sources
  (for example Perplexity, or the AI answers now built into search engines).
  Better than a plain chatbot when you need current, checkable facts.
- **Writing & document helpers** — built into tools you already use (email,
  word processors) to draft, rewrite, and summarise.
- **Image tools** — generate or edit images from a description. Useful for
  mock-ups and simple graphics, less so for anything requiring real photos.
- **Transcription & notes** — turn a recorded meeting or voice note into text
  you can search and summarise.

## How to choose

Don't collect tools. Pick **one general assistant** and get genuinely good at it
first — that one skill transfers everywhere. Add a search assistant when you need
sourced facts, and specialised tools only when a real task demands them.

## A note on free vs paid

Free tiers are enough to learn on and to do a lot of real work. Pay only once a
tool is clearly saving you time you'd otherwise sell — then it pays for itself.

**Takeaway:** master one general assistant first; add other tools only when a
specific job calls for them.

## Try it yourself

Create a free account on one general assistant (ChatGPT, Claude, or Gemini). Ask
it three real questions from your studies or work, and save the most useful
answer somewhere you'll find it again.
""",
    },
    {
        "title": "Prompting Like a Pro",
        "content": """\
## A prompt is just clear instructions

A "prompt" is what you type to an AI tool. The quality of what you get back
depends almost entirely on the quality of what you put in. Vague question, vague
answer. Clear request, useful answer.

## The four parts of a good prompt

1. **Role / context** — tell it who to be and what the situation is.
   *"You are a career coach helping a university student in Rwanda..."*
2. **Task** — say exactly what you want done.
   *"...write a 150-word LinkedIn summary..."*
3. **Details** — give the specifics only you know.
   *"...I study IT, I've built two websites, and I want an internship."*
4. **Format** — say how you want the answer.
   *"...in three short paragraphs, friendly but professional."*

Put together, that one prompt will beat "write me a LinkedIn summary" every time.

## Iterate — don't expect perfection first try

The first answer is a draft, not a verdict. Keep going:
- *"Make it shorter and less formal."*
- *"Give me three different versions."*
- *"That second one — expand the middle part."*

Talking to the tool like a colleague you're guiding is the whole skill.

## Always verify

Ask the tool to *"list the facts in this answer that I should double-check."*
Then check the ones that matter. Never paste an AI answer into something
important without reading every line yourself.

**Takeaway:** give role, task, details, and format — then iterate and verify.

## Try it yourself

Take a weak prompt like "write an email" and rewrite it using the four parts —
role, task, details, format. Run both versions and compare the answers. Notice
how much the detail changed the result.
""",
    },
    {
        "title": "Using AI in Your Field",
        "content": """\
## The same tool, pointed at your work

AI gets powerful when you stop using it in general and start using it on *your*
real tasks. Here's what that looks like across common fields.

## By area

- **Business & admin** — draft emails and proposals, summarise long documents,
  turn messy notes into a clean report, build a first budget or plan to edit.
- **Software & IT** — explain unfamiliar code, find a likely bug, write a first
  version of a function or script, draft documentation. (You still test it —
  AI-written code can look right and be wrong.)
- **Design & content** — brainstorm concepts, draft copy, outline an article,
  generate mock-up images to show a direction.
- **Teaching & study** — turn a topic into a simple explanation at the right
  level, generate practice questions, summarise a chapter, draft a lesson plan.
- **Sales & customer service** — draft replies, summarise a conversation,
  prepare for a call by listing likely questions.

## A method that works anywhere

1. Pick one task you do often and find a little boring.
2. Write a clear prompt describing exactly how *you* do it well.
3. Let AI produce a first draft.
4. Edit it to your standard — and save your best prompt to reuse next time.

Within a week you'll have three or four prompts that quietly save you an hour a
day.

**Takeaway:** apply AI to the repetitive parts of your own real work, and keep
the prompts that work.

## Try it yourself

Choose one repetitive task from your own work or studies. Write a clear prompt for
it, get a first draft, and edit it to your standard. Save the prompt so you can
reuse it tomorrow — that saved prompt is the real prize.
""",
    },
    {
        "title": "Working Responsibly with AI",
        "content": """\
## Speed is not the only thing that matters

Using AI well also means using it safely and honestly. A few habits keep you —
and the people who trust you — out of trouble.

## Accuracy

AI can be confidently wrong. For anything that matters, verify facts, numbers,
names, dates, and quotes against a real source. The rule: *trust it to draft,
never to be the final authority.*

## Privacy

Don't paste genuinely confidential information — client data, passwords,
national ID numbers, private financial details — into a public AI tool. Treat
the input box like a message you might not want shared. When in doubt, remove or
fake the sensitive parts.

## Honesty

Use AI to help you work, not to misrepresent your work. In study, follow your
institution's rules on AI use. In a job, the output is *yours* — you're
responsible for it, so you must understand and stand behind every line.

## Avoiding over-reliance

If AI does all your thinking, your own skills quietly fade. Keep learning the
fundamentals of your field. The goal is to be a skilled professional *with* a
powerful tool — not someone who is helpless without it.

## Bias and fairness

AI learned from human data, so it can repeat human bias. Be especially careful
when it touches decisions about people — hiring, grading, lending. Keep a human
in charge of those.

**Takeaway:** verify facts, protect private data, stay honest, and keep your own
skills sharp.

## Try it yourself

Look back at one AI answer you got this week. List every fact in it that matters,
then check at least one against a real source. The goal is to make verifying a
habit, not an afterthought.
""",
    },
    {
        "title": "Building Your AI-Augmented Career",
        "content": """\
## Turn these skills into opportunity

You now understand what AI is, how to use the main tools, how to prompt well, how
to apply it to your field, and how to do it responsibly. The last step is making
it visible and making it count.

## Show it, don't just say it

Anyone can write "AI skills" on a CV. Stand out by showing results:
- **Build a small portfolio.** Pick two or three real tasks you improved with AI
  and write up what you did and the outcome ("cut report writing from 3 hours to
  40 minutes").
- **Do a real project.** Use AI to help you build or create something — a simple
  website, a tool, a piece of writing, an analysis — and publish it.
- **Help someone.** Solve a real problem for a business, a classmate, or a local
  organisation. A genuine result is worth more than any certificate.

## Position yourself

In your CV, profile, and interviews, describe yourself as someone who gets more
done because you use modern tools well — and can be trusted to use them
carefully. That combination is rare and valuable.

## Keep learning

AI tools change fast, but the fundamentals in this course don't: understand the
tool, prompt clearly, verify, stay responsible. Spend 20 minutes a week trying
one new thing, and you'll stay comfortably ahead.

## Where to go next

Keep a running list of tasks you'd love to speed up, and work through them one at
a time. If you'd like help turning these skills into a real project or product,
that's exactly what WAMUGII TECH SOLUTIONS does — reach out any time.

**Takeaway:** show real results, position yourself as a careful power-user, and
keep learning a little every week.

## Try it yourself

Write one honest "result" line for your CV, such as "Used AI to cut report
writing from 3 hours to 40 minutes." If it isn't true yet, do the task this week
and make it true — then you have both the skill and the proof.
""",
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        existing = course_crud.get_course_by_slug(db, COURSE_SLUG)
        if existing:
            print(f"Course already exists: {existing.title} (slug: {existing.slug})")
            return

        course = course_crud.create_course(db, COURSE)
        print(f"Created course: {course.title} (slug: {course.slug}, status: {course.status.value})")

        for order, lesson in enumerate(LESSONS, start=1):
            created = course_crud.create_lesson(
                db,
                course.id,
                LessonCreate(
                    title=lesson["title"],
                    content=lesson["content"],
                    display_order=order,
                ),
            )
            print(f"  + Lesson {order}: {created.title}")

        print(f"Done. {len(LESSONS)} lessons added. The course is PUBLISHED and live in the catalog.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
