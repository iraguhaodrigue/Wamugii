"""AI Career Essentials -- final-exam questions (true/false, multiple answer, fill in the blank).

The lesson-quiz questions are added to the bank automatically as single-answer
questions (see seed_course_content.exam_bank). TRUE_FALSE: correct [0] = True, [1] = False.
"""

W1 = "Week 1 · Understanding AI"
W2 = "Week 2 · Using AI Tools Well"
W3 = "Week 3 · AI at Work"
W4 = "Week 4 · Responsible AI and Your Career"


def tf(q, true, why, topic):
    return {"kind": "TRUE_FALSE", "q": q, "correct": [0 if true else 1], "why": why, "topic": topic}


def multi(q, options, correct, why, topic):
    return {"kind": "MULTIPLE", "q": q, "options": options, "correct": correct, "why": why, "topic": topic}


def fill(q, answers, why, topic):
    return {"kind": "FILL_BLANK", "q": q, "correct": answers, "why": why, "topic": topic}


EXAM = [
    # --- true / false -----------------------------------------------------------
    tf("An AI system learns patterns from examples instead of following only hand-written rules.", True,
       "Learning from data is the defining idea of modern AI.", W1),
    tf("A large language model checks every fact against a database before it answers.", False,
       "It predicts likely text; it can state false things confidently (hallucinate).", W1),
    tf("All of the AI tools available today are narrow AI.", True,
       "Even powerful chatbots do specific kinds of tasks; general AI does not exist yet.", W1),
    tf("If an AI answer sounds confident and fluent, it is safe to use without checking.", False,
       "Fluency is not accuracy. Important facts must always be verified.", W1),
    tf("Drone delivery of blood and medical supplies in Rwanda is an example of AI-powered technology in Africa.", True,
       "Zipline has delivered medical supplies by autonomous drone in Rwanda since 2016.", W1),
    tf("The best AI-ready mindset is to let AI make your important decisions for you.", False,
       "Augment, don't abdicate: AI assists, you stay responsible for judgement.", W2),
    tf("Adding context and the format you want usually improves an AI answer.", True,
       "Context and format are two of the four parts of a strong R-T-C-F prompt.", W2),
    tf("Giving the AI an example of the output you want is called few-shot prompting.", True,
       "Showing examples ('show, don't just tell') is few-shot prompting.", W2),
    tf("You should cite a reference that AI gave you even if you could not find the source yourself.", False,
       "AI can invent references. Read the real source before citing it.", W3),
    tf("It is acceptable to let AI add qualifications to your CV that you do not have, as long as the writing is good.", False,
       "Never invent qualifications or results; employers check, and dishonesty ends careers.", W3),
    tf("Before pasting customer data into a public AI tool, you should anonymise it or use made-up sample data.", True,
       "Replace names and numbers with placeholders or use sample data to protect privacy.", W4),
    tf("Rwanda has a law that protects personal data and privacy.", True,
       "Law No. 058/2021 relating to the protection of personal data and privacy.", W4),
    tf("In most jobs, AI changes individual tasks before it changes whole jobs.", True,
       "Tasks change before jobs do: some are automated, many augmented, some stay human-led.", W4),
    tf("Leadership, care and negotiation are examples of tasks that stay mainly human-led.", True,
       "Human-led tasks depend on trust, judgement and relationships.", W4),
    tf("A good AI portfolio shows real examples of work you did with AI, explained honestly.", True,
       "Show, don't just say: small, true examples convince employers.", W4),
    tf("Bias in AI can only happen if a programmer intends to discriminate.", False,
       "Bias usually enters through unbalanced or historical data, without anyone intending it.", W4),

    # --- multiple answers ----------------------------------------------------------
    multi("Which of these are everyday examples of AI? (Choose all that apply.)",
          ["Next-word suggestions on a phone keyboard", "A fraud alert from a mobile-money app", "A printed bus timetable", "Video recommendations on YouTube or TikTok"],
          [0, 1, 3], "Keyboard suggestions, fraud alerts and recommendations all learn from data; a printed timetable does not.", W1),
    multi("Which statements about how machines learn are correct? (Choose all that apply.)",
          ["A model learns patterns from training data", "Better and more representative data usually gives a better model", "A model never makes mistakes after training", "A trained model can be wrong on unusual new cases"],
          [0, 1, 3], "Models learn from data, depend on data quality and can fail on unusual cases.", W1),
    multi("Which are good reasons why an AI tool can give a wrong answer? (Choose all that apply.)",
          ["It predicts likely words rather than checking facts", "Its training data may be out of date", "It may have little data about local topics such as Rwandan rules", "It always reads the latest official website first"],
          [0, 1, 2], "Prediction, outdated data and gaps in local data cause errors; tools do not always read official sources.", W1),
    multi("Which belong to the four-part R-T-C-F prompt? (Choose all that apply.)",
          ["Role", "Task", "Context", "Format", "Font size"],
          [0, 1, 2, 3], "R-T-C-F stands for Role, Task, Context and Format.", W2),
    multi("Which are advanced prompting techniques from this course? (Choose all that apply.)",
          ["Give examples of the output you want", "Ask for step-by-step reasoning", "Ask the AI to interview you first", "Type the prompt in capital letters"],
          [0, 1, 2], "Examples, step-by-step thinking and letting the AI interview you improve results; capitals do not.", W2),
    multi("Which are red flags that an AI answer must be checked? (Choose all that apply.)",
          ["Very specific numbers, dates or quotes", "References or links you cannot find", "Legal, medical or financial advice", "A short, polite tone"],
          [0, 1, 2], "Specific claims, unfindable sources and high-stakes advice need verification.", W2),
    multi("Which steps belong to the C-H-E-C-K routine? (Choose all that apply.)",
          ["Claims — list the claims that matter", "Hunt for sources", "External check with a trusted source", "Copy the answer to everyone"],
          [0, 1, 2], "C-H-E-C-K: Claims, Hunt for sources, External check, Calculate, Keep or cut.", W2),
    multi("Which tasks can a general AI assistant help with at work? (Choose all that apply.)",
          ["Drafting an email", "Summarising a long report", "Writing a spreadsheet formula", "Signing a contract for you"],
          [0, 1, 2], "Drafting, summarising and formulas are good uses; signing contracts is your legal responsibility.", W3),
    multi("Which are good slide habits? (Choose all that apply.)",
          ["One idea per slide", "A headline that states the point", "Check every number AI put on a slide", "Fill every slide with long paragraphs"],
          [0, 1, 2], "Few words, one idea and checked numbers make clear slides.", W3),
    multi("Which are part of the draft–edit–own method for writing with AI? (Choose all that apply.)",
          ["Let AI produce a first draft", "Edit it with your knowledge and voice", "Take responsibility for the final text", "Send the first draft without reading it"],
          [0, 1, 2], "Draft with AI, edit carefully, and own the result.", W3),
    multi("Which are good ways to use AI for learning? (Choose all that apply.)",
          ["Ask it to explain a topic in simple words", "Ask it to quiz you", "Ask it to check your understanding of a summary you wrote", "Ask it to write your exam answers for you"],
          [0, 1, 2], "Use AI to learn, not to skip learning or cheat.", W3),
    multi("Which should never be pasted into a public AI tool? (Choose all that apply.)",
          ["National ID or passport numbers", "Passwords", "Customer or patient records", "A made-up sample table"],
          [0, 1, 2], "Personal, secret and confidential data stay out; sample data is fine.", W4),
    multi("Which are parts of the S-A-F-E responsible-use checklist? (Choose all that apply.)",
          ["Sources checked", "Affected people considered", "Fair and honest", "Fastest possible answer"],
          [0, 1, 2], "S-A-F-E: Sources checked, Affected people considered, Fair and honest, Encrypted/private.", W4),
    multi("Which skills grow in value as AI spreads? (Choose all that apply.)",
          ["AI literacy", "Critical thinking", "Communication", "Avoiding all new tools"],
          [0, 1, 2], "AI literacy, critical thinking and communication grow in value; avoiding tools does not.", W4),
    multi("Which are good ways to protect your accounts? (Choose all that apply.)",
          ["Use a strong password", "Turn on two-step verification", "Verify unusual requests for money through a second channel", "Share your password with an AI tool to save time"],
          [0, 1, 2], "Strong passwords, two-step verification and checking unusual requests keep you safe from AI-powered scams.", W4),
    multi("Which belong in a strong AI portfolio? (Choose all that apply.)",
          ["A real task you improved with AI", "The prompts or method you used", "The result and what you checked", "Claims of results you never achieved"],
          [0, 1, 2], "Show real, honest work: the task, the method and the result.", W4),
    multi("Which describe a good 90-day AI career plan? (Choose all that apply.)",
          ["One clear goal", "Practise, apply, then show your work in three 30-day phases", "A weekly routine to keep going", "Wait until AI stops changing"],
          [0, 1, 2], "A clear goal, three phases and a weekly routine make the plan work.", W4),

    # --- fill in the blank ----------------------------------------------------------
    fill("When an AI states something false with confidence, it is called a ___.", ["hallucination", "hallucinations", "hallucinating"],
         "A hallucination is a fluent, confident but false output.", W1),
    fill("ChatGPT, Gemini and Claude are built on large ___ models (LLMs).", ["language"],
         "LLM stands for large language model.", W1),
    fill("Machine learning means learning patterns from ___.", ["data", "examples"],
         "Models learn from data (examples).", W1),
    fill("The learned pattern stored after training is called a ___.", ["model", "ai model"],
         "Training produces a model.", W1),
    fill("In the R-T-C-F prompt, the letter F stands for ___.", ["format"],
         "Role, Task, Context, Format.", W2),
    fill("Showing the AI one or more examples of what you want is called ___-shot prompting.", ["few"],
         "Few-shot prompting gives examples.", W2),
    fill("A saved collection of your best reusable prompts is called a prompt ___.", ["library"],
         "Your Week 2 project built a prompt library.", W2),
    fill("Augment, don't ___: AI supports your judgement, it does not replace it.", ["abdicate"],
         "The AI-ready mindset: augment, don't abdicate.", W2),
    fill("Before sharing data with AI, replace names with placeholders such as 'Customer A'. This is called ___ the data.", ["anonymising", "anonymizing", "anonymise", "anonymize"],
         "Anonymising removes personal details.", W4),
    fill("Rwanda's personal data law is Law No. ___/2021.", ["058", "58"],
         "Law No. 058/2021 relating to the protection of personal data and privacy.", W4),
    fill("Tasks that AI does much of, such as routine data entry, are called ___ tasks.", ["automated"],
         "Automated, augmented and human-led are the three groups of tasks.", W4),
    fill("Tasks that people and AI do together faster and better are called ___ tasks.", ["augmented"],
         "Augmented tasks combine human judgement with AI speed.", W4),
    fill("The 90-day plan has three phases of ___ days each.", ["30", "thirty"],
         "Three 30-day phases: practise, apply, show.", W4),
]
