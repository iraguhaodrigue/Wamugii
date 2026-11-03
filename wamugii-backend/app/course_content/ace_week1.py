"""AI Career Essentials -- Week 1: Understanding AI. Original WAMUGII content."""

WEEK1 = {
    "title": "Week 1 · Understanding AI",
    "lessons": [
        # ------------------------------------------------------------------ 1
        {
            "title": "What AI Really Is (and Isn't)",
            "minutes": 40,
            "video": "https://www.youtube.com/watch?v=4RixMPF4xis",
            "content": """
**Learning objective:** Explain in simple words what artificial intelligence is, tell AI apart from ordinary software, and name three things AI is not.

## The one idea to start with

Ordinary software follows rules that a person wrote by hand: *if the amount is above 100,000 RWF, ask for a manager's approval.* Artificial intelligence (AI) is different. Instead of being given every rule, an AI system **learns patterns from examples**.

Think of a spam filter. Years ago, programmers wrote lists of "bad words". Spammers simply changed the words. Today's filters have *learned* from millions of real emails what spam usually looks like — the strange links, the urgent tone, the unknown sender. Nobody wrote those rules. The system found the pattern.

That single idea — **learning patterns from examples instead of following hand-written rules** — explains almost everything you will meet in this course.

## Rules vs. learning: a side-by-side view

| | Ordinary software | AI system |
|---|---|---|
| How it works | Follows rules people wrote | Learns patterns from examples (data) |
| Example | A calculator, a payroll formula | A spam filter, a voice assistant, ChatGPT |
| When the world changes | A person must rewrite the rules | It can be retrained on new examples |
| Can it be wrong? | Only if the rule is wrong | Yes — even when the pattern looked right |

## Words you will keep hearing

- **Artificial intelligence (AI)** — the broad goal: machines doing tasks that normally need human thinking, like understanding language or recognising images.
- **Machine learning (ML)** — the main method behind today's AI: learning patterns from data.
- **Model** — the "learned pattern" stored inside the computer after training. When you use ChatGPT, you are talking to a model.
- **Data** — the examples a model learns from: text, photos, sounds, numbers.
- **Large language model (LLM)** — a model trained on a huge amount of text so it can read and write language. ChatGPT, Gemini and Claude are built on LLMs.

## You already use AI every day

- Your phone keyboard suggests the next word as you type.
- Google Maps predicts how long the trip from Kimironko to Nyabugogo will take.
- Your bank or MoMo app flags a strange transaction.
- YouTube and TikTok decide which video to show you next.
- Your phone camera recognises faces and improves photos at night.

None of these feel like "robots", but all of them learned patterns from data.

## What AI is *not*

1. **AI is not magic.** It is mathematics running on computers, using data that people collected.
2. **AI does not "understand" like you do.** A language model produces the most *likely* next words. Usually that is helpful, but it can sound completely confident while being wrong. This is called a **hallucination**.
3. **AI is not conscious and has no goals of its own.** It does what it was built and asked to do.
4. **AI is not always right.** A pattern learned from the past can fail on something new or unusual.

## Why this matters for your career

You do not need to *build* AI to benefit from it — just as you did not need to build Excel to use a spreadsheet. The people who get ahead will not all be AI engineers. They will be teachers, accountants, nurses, farmers, students and business owners who know how to **use AI tools well and check their work**. That is exactly what this course teaches.

**Takeaway:** AI learns patterns from examples, it predicts rather than knows, and your job is to use it well and check its work.

## Try it yourself

1. Open any free AI assistant (ChatGPT, Gemini, Copilot or Claude).
2. Ask: *"Explain [a topic from your studies or work] to me in simple words, as if I am 15 years old."*
3. Read the answer and find **one statement you should double-check**. Check it using a trusted source (a textbook, an official website or your lecturer).
4. Write two sentences: what the AI did well, and what you had to verify.
""",
            "quiz": [
                ("What is the key difference between ordinary software and an AI system?",
                 ["AI runs on faster computers", "AI learns patterns from examples instead of only following hand-written rules", "AI never makes mistakes", "Ordinary software cannot use the internet"],
                 1, "The defining idea of modern AI is learning patterns from data (examples) rather than being told every rule."),
                ("Which of these is an everyday example of AI?",
                 ["A basic calculator adding 2 + 2", "A light switch", "Your phone keyboard suggesting the next word", "A printed timetable"],
                 2, "Next-word suggestion is learned from huge amounts of typing data. The others follow fixed rules or no rules at all."),
                ("What is a 'model' in AI?",
                 ["A person who poses for photos", "The learned pattern stored after training", "The computer's screen", "A list of rules typed by a programmer"],
                 1, "After training on data, the learned pattern is stored as a model. Tools like ChatGPT let you talk to a model."),
                ("What is an AI 'hallucination'?",
                 ["When the AI refuses to answer", "When the AI produces a confident answer that is false", "When the screen shows strange colours", "When the AI becomes conscious"],
                 1, "A hallucination is a fluent, confident but wrong answer. It is why you always verify important facts."),
                ("Which statement about AI is TRUE?",
                 ["AI has its own goals and feelings", "AI understands meaning exactly like a person", "AI can be useful and still be wrong", "AI does not need any data"],
                 2, "AI is a powerful pattern-finder. It is often useful, but it can be wrong, so human checking stays important."),
                ("According to this lesson, who will benefit most from AI at work?",
                 ["Only AI engineers", "People in any field who use AI well and check its work", "Only large companies", "Nobody — AI will replace everyone"],
                 1, "You do not need to build AI to benefit. Professionals in every field who use it well and verify its output gain the most."),
            ],
        },
        # ------------------------------------------------------------------ 2
        {
            "title": "How Machines Learn: Data, Patterns and Models",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=R9OHn5ZF4Uo",
            "content": """
**Learning objective:** Describe the three steps of machine learning (data, training, prediction), explain why data quality matters, and name the three main types of learning.

## Learning by example — just like people

How did you learn to recognise a mango? Nobody gave you a rule like "oval, 10–15 cm, green-yellow". You saw many mangoes, and your brain found the pattern. Machine learning works the same way, only with far more examples and mathematics instead of a brain.

## The three steps of machine learning

1. **Data** — collect many examples. For a model that predicts crop yields, that could be past rainfall, soil type, fertiliser used and the harvest that followed.
2. **Training** — the computer looks at the examples again and again, adjusting itself to make fewer mistakes each time. The result is a **model**.
3. **Prediction** — the model is given something new it has never seen (this season's rainfall and soil) and makes a prediction (the expected harvest).

A simple way to remember it: **examples in → pattern learned → prediction out.**

## Features and labels

- A **feature** is a piece of information the model looks at: rainfall, house size, number of rooms.
- A **label** is the answer we want the model to learn to predict: the harvest, the house price, "spam" or "not spam".

| Feature: house size | Feature: rooms | Feature: area | Label: monthly rent |
|---|---|---|---|
| 80 m² | 3 | Kicukiro | 250,000 RWF |
| 120 m² | 4 | Kacyiru | 450,000 RWF |
| 60 m² | 2 | Nyamirambo | 150,000 RWF |

After seeing thousands of rows like these, a model can estimate the rent of a house it has never seen.

## Three ways machines learn

- **Supervised learning** — learning from examples *with* the correct answers (labels). Example: thousands of X-ray images each marked "pneumonia" or "healthy".
- **Unsupervised learning** — finding groups in data *without* answers. Example: a supermarket discovering that its customers fall into four shopping styles.
- **Reinforcement learning** — learning by trial, error and reward. Example: a program that learns to play a game by getting points for winning.

## Garbage in, garbage out

A model can only be as good as its data.

- If the data is **too small**, the model has not seen enough to learn the real pattern.
- If the data is **wrong or messy**, the model learns mistakes.
- If the data is **unbalanced** — for example, a face-recognition system trained mostly on light-skinned faces — the model will work worse for the people it rarely saw. This is one way **bias** enters AI, and we return to it in Week 4.

## Why this matters for you

When you use an AI tool, remember it is drawing on patterns from its training data. That explains both its strengths (it has "seen" a lot) and its weaknesses (it may not know recent events, local facts about Rwanda, or your organisation's own information unless you give them to it).

**Takeaway:** Machine learning turns examples into a model that makes predictions — and the quality of the data decides the quality of the model.

## Try it yourself

Choose a decision from your life or work that could be predicted from past examples (for example: *Will a customer pay on time? How many students will attend on Friday? Will it rain tomorrow?*).

1. Write the **label** you want to predict.
2. List **five features** that could help predict it.
3. Write one way the data could be **biased or misleading**, and how you would fix it.
""",
            "quiz": [
                ("What are the three basic steps of machine learning, in order?",
                 ["Prediction, data, training", "Data, training, prediction", "Training, prediction, data", "Coding, testing, selling"],
                 1, "First you collect data, then the computer trains a model on it, then the model makes predictions on new cases."),
                ("In a model that predicts house rent, which of these is the LABEL?",
                 ["Number of rooms", "House size", "Monthly rent", "Neighbourhood"],
                 2, "The label is the answer the model learns to predict — here, the rent. Rooms, size and area are features."),
                ("Learning from examples that already have the correct answers is called…",
                 ["Supervised learning", "Unsupervised learning", "Reinforcement learning", "Random learning"],
                 0, "Supervised learning uses labelled examples, such as X-rays marked 'healthy' or 'pneumonia'."),
                ("A supermarket groups its customers into shopping styles without any labels. This is…",
                 ["Supervised learning", "Unsupervised learning", "Reinforcement learning", "Not machine learning"],
                 1, "Finding groups in data without correct answers is unsupervised learning."),
                ("What does 'garbage in, garbage out' mean for AI?",
                 ["AI cleans dirty data automatically", "A model can only be as good as the data it learned from", "AI throws away old data", "Computers need regular cleaning"],
                 1, "Wrong, messy, small or unbalanced data leads to a weak or unfair model."),
                ("Why might an AI tool not know a recent local event in Rwanda?",
                 ["Because AI is not allowed in Rwanda", "Because it only knows patterns from its training data, which may not include it", "Because AI cannot read English", "Because the event was too small to matter"],
                 1, "Models learn from their training data. Recent or local information may be missing unless you provide it."),
            ],
        },
        # ------------------------------------------------------------------ 3
        {
            "title": "Generative AI and Large Language Models",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=LPZh9BOjkQs",
            "content": """
**Learning objective:** Explain what generative AI is, describe in simple terms how a large language model produces text, and list what these tools can create.

## From recognising to creating

Earlier AI mostly **recognised** or **predicted**: "this email is spam", "this photo shows a cat". **Generative AI** goes further — it **creates new content**: text, images, audio, video and computer code.

When you ask ChatGPT to write a cover letter, or ask an image tool to draw "a modern Kigali office at sunset", you are using generative AI.

## How a large language model writes

A **large language model (LLM)** is trained on an enormous amount of text — books, websites, articles, code. During training it plays one simple game billions of times: **guess the next word**.

> "The capital of Rwanda is ___" → most likely next word: "Kigali".

By getting extremely good at predicting the next word (more exactly, the next small piece of text called a **token**), the model learns grammar, facts, writing styles and even some reasoning patterns. When you ask a question, it writes the answer one token at a time, each time choosing a likely next token.

Two important consequences:

1. **It is very fluent.** It has seen so much language that its writing sounds natural and confident.
2. **Fluent is not the same as true.** The model picks *likely* words, not *verified* facts. That is why hallucinations happen.

## Key ideas in plain words

- **Prompt** — the instruction or question you give the AI.
- **Token** — a small piece of text (a word or part of a word) that the model reads and writes.
- **Context window** — how much text the model can "keep in mind" at once in one conversation.
- **Training data cut-off** — the date after which the model has no built-in knowledge, unless the tool can search the web.
- **Multimodal** — a model that can work with more than text, such as reading a photo of a receipt or listening to audio.

## What generative AI can create

| Type | Example tools | Example use |
|---|---|---|
| Text | ChatGPT, Gemini, Claude, Copilot | Emails, reports, summaries, lesson plans |
| Images | Image generators in ChatGPT, Gemini, Canva | Posters, social-media graphics |
| Audio | Voice and music tools | Voice-overs, podcast clean-up |
| Video | Video generators and editors | Short promotional clips |
| Code | GitHub Copilot, AI assistants | Formulas, scripts, websites |

## Where it shines — and where to be careful

**Shines at:** first drafts, summarising long text, explaining ideas at different levels, brainstorming, translating, re-formatting.

**Be careful with:** exact numbers and dates, recent news, quotations, legal or medical advice, and anything about Rwanda that is very local or very new. Always check.

**Takeaway:** Generative AI creates new content by predicting likely next pieces; that makes it fluent and fast — but not automatically correct.

## Try it yourself

1. Ask an AI assistant: *"Write a 100-word welcome message for new students joining a computer course in Kigali."*
2. Then ask it to rewrite the same message **(a)** for parents, **(b)** in a more formal tone, and **(c)** as three short bullet points.
3. Note how the same model changes style when you change the instruction. Which version is best, and why?
""",
            "quiz": [
                ("What makes generative AI different from earlier AI?",
                 ["It only recognises images", "It creates new content such as text, images and code", "It cannot use language", "It works without electricity"],
                 1, "Generative AI produces new content, while earlier systems mostly recognised or predicted."),
                ("How does a large language model produce an answer?",
                 ["It searches a single correct answer in a database", "It writes one token at a time, choosing likely next tokens", "It copies a website word for word", "A person types the answer in real time"],
                 1, "LLMs generate text by repeatedly predicting a likely next token."),
                ("Why can a fluent AI answer still be wrong?",
                 ["Because the model chooses likely words, not verified facts", "Because the internet was slow", "Because the user typed in lowercase", "It cannot be wrong if it is fluent"],
                 0, "Fluency comes from predicting likely language. Likely is not the same as true."),
                ("What is a 'prompt'?",
                 ["The AI's training data", "The instruction or question you give the AI", "A type of computer chip", "The answer the AI gives"],
                 1, "Your prompt is what you ask or tell the AI to do."),
                ("A model that can read a photo of a receipt and answer questions about it is…",
                 ["Multimodal", "Offline", "Unsupervised", "Rule-based"],
                 0, "Multimodal models work with more than one kind of input, such as text and images."),
                ("For which task should you be MOST careful and check the AI's output?",
                 ["Brainstorming poster ideas", "Rewriting a paragraph more simply", "Exact figures from a recent government report", "Changing the tone of an email"],
                 2, "Exact numbers, dates and recent facts are where hallucinations do the most harm. Always verify them."),
            ],
        },
        # ------------------------------------------------------------------ 4
        {
            "title": "What AI Does Well — and Where It Fails",
            "minutes": 40,
            "video": "https://www.youtube.com/watch?v=cfqtFvWOfg0",
            "content": """
**Learning objective:** List the main strengths and failure modes of AI tools, recognise hallucinations and bias, and decide when a task is safe to hand to AI.

## The jagged edge

AI is surprisingly good at some hard tasks and surprisingly bad at some easy ones. It can write a decent poem in seconds but may miscount the letters in a word or invent a book that does not exist. Researchers call this a **jagged frontier**: there is no smooth line between "easy for AI" and "hard for AI". You learn where the edge is by trying, checking and noticing.

## What AI does well

- **Drafting** — first versions of emails, reports, letters, lesson plans.
- **Summarising** — turning 20 pages into one page of key points.
- **Explaining** — breaking difficult ideas into simple steps, at the level you ask for.
- **Transforming** — changing tone, translating, turning notes into a table.
- **Brainstorming** — giving you many options quickly to choose from.
- **Pattern spotting** — finding trends in data you provide.

## Where AI fails

1. **Hallucinations** — invented facts, fake quotes, made-up references and links that look real.
2. **Out-of-date knowledge** — the model may not know recent events, new laws or new prices.
3. **Local blind spots** — less training data about Rwanda, Kinyarwanda and local institutions means more mistakes on local topics.
4. **Bias** — patterns learned from unbalanced data can treat some groups unfairly.
5. **Maths and exact counting** — many tools still make arithmetic slips unless they use a calculator tool.
6. **Over-confidence** — the tone sounds certain even when the content is a guess.
7. **No responsibility** — the AI cannot be held accountable. You can.

## A quick risk test before you use AI

Ask yourself two questions:

| | Low cost if wrong | High cost if wrong |
|---|---|---|
| **Easy for me to check** | ✅ Use AI freely (brainstorming, drafts) | ⚠️ Use AI, then check carefully (reports, figures) |
| **Hard for me to check** | ⚠️ Use AI as a starting point only | ⛔ Do not rely on AI (medical, legal, financial decisions) |

## Spotting a hallucination

Warning signs:

- Very specific numbers, dates or names without a source.
- References or links you cannot find when you search for them.
- Quotes from real people that you cannot confirm.
- An answer that changes when you ask the same question again.

**Simple habit:** for anything that matters, ask the AI *"What are your sources?"*, then check those sources yourself.

**Takeaway:** Let AI do the drafting, summarising and explaining — and keep human judgement for facts, fairness and final decisions.

## Try it yourself

1. Ask an AI assistant for *"three academic books about digital transformation in Rwanda, with authors and years."*
2. Search for each book online or in a library catalogue.
3. Record which ones are real, which are partly wrong, and which seem invented. What does this teach you about using AI for references?
""",
            "quiz": [
                ("What does the 'jagged frontier' of AI mean?",
                 ["AI is equally good at everything", "AI can be strong at some hard tasks and weak at some easy ones", "AI only works in some countries", "AI tools have sharp graphics"],
                 1, "AI ability is uneven, so you learn its edge by testing and checking."),
                ("Which task is AI generally GOOD at?",
                 ["Taking legal responsibility for a decision", "Summarising a long document into key points", "Knowing tomorrow's exchange rate", "Guaranteeing every reference is real"],
                 1, "Summarising is a core strength. The others are known weaknesses or impossible for AI."),
                ("Which is a warning sign of a hallucination?",
                 ["The answer is short", "A reference you cannot find anywhere when you search", "The answer uses simple words", "The AI asks a follow-up question"],
                 1, "References and links that cannot be found are a classic hallucination sign."),
                ("Why might AI make more mistakes on local Rwandan topics?",
                 ["Rwanda bans AI tools", "There is usually less training data about very local topics", "Local topics are too easy", "AI cannot read place names"],
                 1, "Less local data in training means weaker, less reliable patterns for local questions."),
                ("A task is HIGH cost if wrong and HARD for you to check (for example, a medical decision). What should you do?",
                 ["Rely fully on the AI", "Do not rely on AI; use qualified experts", "Ask the AI twice and choose the longer answer", "Use AI because it sounds confident"],
                 1, "High-stakes, hard-to-check decisions need qualified human professionals, not AI alone."),
                ("Who is responsible for work you submit that used AI?",
                 ["The AI company", "The AI tool itself", "You", "Nobody"],
                 2, "AI cannot be held accountable. The person who uses and submits the work is responsible."),
            ],
        },
        # ------------------------------------------------------------------ 5
        {
            "title": "AI in Rwanda and Across Africa",
            "minutes": 40,
            "video": "https://www.youtube.com/watch?v=3AZF1TTDdEM",
            "content": """
**Learning objective:** Describe how AI is already being used in Rwanda and Africa, explain why local data and languages matter, and identify opportunities in your own field.

## AI is not only a Silicon Valley story

Some of the most practical uses of technology in the world are happening in Africa, because the problems are real and the need is urgent. Rwanda in particular has made digital transformation a national priority, and in **2023 the Government of Rwanda adopted a National Artificial Intelligence Policy** to guide the safe and useful adoption of AI across the economy.

## Examples close to home

- **Health logistics** — Rwanda has used drones (Zipline) since 2016 to deliver blood and medical supplies to hospitals in hard-to-reach areas, using software to plan routes and manage demand.
- **Agriculture** — AI tools can identify crop diseases from a phone photo, forecast weather, and help farmers plan planting and fertiliser use.
- **Financial services** — mobile-money and banking systems use machine learning to detect fraud and assess credit for people without a long banking history.
- **African languages** — communities such as **Masakhane** build language technology for African languages, and **Digital Umuganda** has collected Kinyarwanda voice data so speech technology can understand Kinyarwanda speakers.
- **Education** — AI tutors and study assistants help learners practise at their own pace.
- **Research and talent** — the **Deep Learning Indaba** brings together thousands of African AI researchers and students, and Kigali hosts international technology and AI events.

## Why local data and languages matter

An AI tool trained mostly on English text from other countries may:

- misunderstand Kinyarwanda, Swahili or French mixed with English;
- give advice that fits another country's laws, prices or culture;
- know little about Rwandan institutions, places and history.

That is why **local data, local languages and local experts** are so valuable — and why there are real jobs and businesses to be built by people who understand both AI and the local context.

## Opportunities by field

| Field | Where AI can help |
|---|---|
| Education | Lesson planning, practice questions, feedback on writing |
| Health | Appointment reminders, record summaries, health information in local languages |
| Agriculture | Disease detection, weather and market-price information |
| Business | Customer service, marketing content, bookkeeping help |
| Government services | Faster answers to citizens, document processing |
| Tourism & hospitality | Multilingual guest communication, booking support |

## A balanced view

AI also brings real challenges for Africa: the cost of internet and devices, protecting personal data, avoiding tools that do not fit local needs, and making sure benefits reach everyone, not only big cities. Good professionals keep both the opportunity and the risk in view.

**Takeaway:** AI is already solving real problems in Rwanda and Africa, and people who understand the local context are exactly the people needed to use it well.

## Try it yourself

1. Pick your field (or the field you want to work in).
2. Write down **two problems** in that field in Rwanda that AI might help with.
3. For each problem, write: the data that would be needed, who would benefit, and one risk to watch out for.
""",
            "quiz": [
                ("In which year did Rwanda adopt its National Artificial Intelligence Policy?",
                 ["2016", "2019", "2023", "2030"],
                 2, "The Government of Rwanda adopted its National AI Policy in 2023."),
                ("What has Zipline been doing in Rwanda since 2016?",
                 ["Teaching coding in schools", "Delivering blood and medical supplies by drone", "Running a social network", "Selling smartphones"],
                 1, "Zipline uses drones to deliver blood and medical supplies, with software planning routes and demand."),
                ("Why is Kinyarwanda voice data, like Digital Umuganda's, important?",
                 ["It makes phones cheaper", "It helps speech technology understand Kinyarwanda speakers", "It replaces English completely", "It is only used for music"],
                 1, "Voice technology needs examples in a language to understand it. Local language data closes that gap."),
                ("What is the Deep Learning Indaba?",
                 ["A Rwandan bank", "A gathering that strengthens African AI research and talent", "A type of AI model", "A government law"],
                 1, "The Deep Learning Indaba brings together African AI researchers and students."),
                ("Why might a general AI tool give poor advice about Rwandan regulations?",
                 ["It was trained mostly on data from other countries and may lack local details", "Rwandan regulations are secret", "AI cannot read numbers", "It is illegal to ask"],
                 0, "Less local training data means weaker local knowledge, so local experts and sources stay essential."),
                ("Which is a real CHALLENGE for AI adoption mentioned in this lesson?",
                 ["Too many free devices", "Protecting personal data and making sure benefits reach everyone", "There are no problems to solve", "AI only works in rural areas"],
                 1, "Data protection, cost and fair access are real challenges alongside the opportunities."),
            ],
        },
        # ------------------------------------------------------------------ 6
        {
            "title": "Week 1 Project: Map the AI Around You",
            "minutes": 60,
            "video": "https://www.youtube.com/watch?v=0yCJMt9Mx9c",
            "content": """
**Learning objective:** Apply Week 1 ideas by identifying, explaining and evaluating real AI uses in your daily life and chosen field.

## Your project

This week you learned what AI is, how it learns, how generative AI works, where it fails, and how it is used in Rwanda and Africa. Now you will put it together in a short **AI Map** — a one- to two-page document you can keep in your portfolio.

## What to produce

**Part A — AI in my day (5 examples).** For each example, write:

| AI use | What it learned from (data) | What it predicts or creates | One risk or limitation |
|---|---|---|---|
| e.g. Phone keyboard | Millions of typed messages | The next word | Suggests wrong words in Kinyarwanda |

**Part B — AI in my field (3 examples).** Choose your field of study or work. For each example, explain: the problem it solves, who benefits, and what human checking is still needed.

**Part C — One honest test.** Ask an AI assistant one real question from your field. Paste the question, summarise the answer, and mark which parts were correct, which needed checking, and which were wrong.

**Part D — Reflection (100–150 words).** What surprised you most this week? Where will you use AI next week, and where will you not use it?

## How you will be assessed (self-check)

- ☐ I gave 5 everyday examples with data, output and a risk for each.
- ☐ I gave 3 examples from my field with benefits and human checks.
- ☐ I tested an AI tool honestly and verified its answer.
- ☐ My reflection uses at least three terms from Week 1 (model, data, hallucination, bias, LLM…).
- ☐ My work is written in my own words.

**Takeaway:** Seeing AI clearly — what it learns from, what it produces and where it fails — is the foundation for using it well.

## Try it yourself

Complete Parts A–D using the worksheet in this lesson's PDF. Save your finished AI Map: you will reuse it in your Week 4 portfolio. When you are done, mark this lesson complete to move to Week 2.
""",
            "quiz": [],
        },
    ],
}
