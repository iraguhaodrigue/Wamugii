"""AI Foundations -- Week 4: AI in Society. Original WAMUGII content."""

WEEK4 = {
    "title": "Week 4 · AI in Society",
    "lessons": [
        # ------------------------------------------------------------------ 19
        {
            "title": "Bias and Fairness",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=UG_X_7g63rY",
            "content": """
**Learning objective:** Explain how bias enters AI systems, describe real cases of unfair AI, and apply practical steps to make a model fairer.

## When a model is unfair

An AI system is **biased** (in the fairness sense) when it gives systematically worse results for some groups of people — by gender, age, region, language, skin colour, disability or income. A model does not need to be "told" to discriminate. It learns patterns from data, and if the data reflects an unfair past, the model can repeat and even amplify it.

## Real cases

- **Face analysis:** the *Gender Shades* study (2018) by Joy Buolamwini and Timnit Gebru tested commercial gender-classification systems. Error rates were under 1% for lighter-skinned men but far higher — over 30% in one system — for darker-skinned women. The training images had included far fewer darker-skinned faces.
- **Hiring:** Amazon stopped using an experimental CV-screening tool after finding it rated CVs lower when they mentioned the word "women's" (as in "women's football club"). It had learned from ten years of past hiring, mostly of men.
- **Language:** many AI tools work well in English and poorly in Kinyarwanda, Kirundi or Luganda, so speakers of those languages get worse service.

## Where bias comes from

| Source | What happens | Example |
|---|---|---|
| **Historical bias** | The data reflects past unfairness | Past loans given mostly to men |
| **Representation bias** | Some groups are missing or rare in the data | Few rural farmers in a crop dataset |
| **Measurement bias** | A feature measures groups differently | Using "number of arrests" as a stand-in for "crime" |
| **Labelling bias** | The people labelling bring their own assumptions | Annotators judging "professional" photos |
| **Deployment bias** | A model is used in a setting it was not built for | A model trained in Kigali used unchanged in a rural district |

## Proxy features

Removing a sensitive column (such as gender) is **not enough**. Other features can act as **proxies** — they carry the same information indirectly. A first name, a school attended, or a home district can reveal gender, ethnicity or income.

## Measuring fairness

Check results **separately for each group**, not only overall:

- Is the **accuracy** similar for women and men, urban and rural users?
- Is the **recall** similar? (Does the model catch high-risk patients equally in every district?)
- Is the **approval rate** fair, given real differences?

A model with 92% overall accuracy might be 96% accurate for one group and 75% for another. The average hides the harm.

## Practical steps to reduce bias

1. **Ask who could be harmed** at the very start of the project.
2. **Collect representative data** — include the groups the model will serve.
3. **Measure performance per group** before deployment, and keep measuring after.
4. **Involve the affected community** and domain experts in design and testing.
5. **Keep a human in the loop** for high-stakes decisions such as loans, jobs, health and justice.
6. **Document** the data, its limits and the fairness checks (a "model card").

**Takeaway:** Bias enters through data, labels, measurements and use. Removing sensitive columns is not enough. Measure results per group, use representative data, and keep humans responsible for serious decisions.

## Try it yourself

1. Pick a model idea from your Week 2 plan.
2. List three groups that might get worse results, and why.
3. Name one proxy feature in your data that could reveal a sensitive attribute.
4. Write the per-group checks you would run before deployment.
""",
            "quiz": [
                ("When is an AI system biased in the fairness sense?",
                 ["When it is slow", "When it gives systematically worse results for some groups of people", "When it uses colour", "When it has many layers"],
                 1, "Fairness bias means some groups consistently receive worse outcomes."),
                ("What did the Gender Shades study find?",
                 ["All systems were equally accurate", "Error rates were much higher for darker-skinned women than for lighter-skinned men", "Face recognition never makes mistakes", "Men were always misclassified"],
                 1, "The study showed large accuracy gaps linked to unrepresentative training images."),
                ("Training data contains very few rural farmers. This is…",
                 ["Representation bias", "Gradient descent", "Data leakage", "Overfitting only"],
                 0, "When groups are missing or rare in the data, the model serves them poorly — representation bias."),
                ("Why is deleting the gender column not enough to stop gender bias?",
                 ["Other features can act as proxies for gender", "Gender columns cannot be deleted", "Models do not use columns", "It is always enough"],
                 0, "Names, schools or other features can reveal the same information indirectly."),
                ("A model is 92% accurate overall. What should you also check?",
                 ["Nothing more", "Accuracy and recall for each group separately", "Only the training speed", "The colour of the dashboard"],
                 1, "Overall averages can hide much worse performance for some groups."),
                ("Which step helps reduce bias in high-stakes decisions?",
                 ["Remove all humans", "Keep a human in the loop and measure results per group", "Use less data", "Hide the model's results"],
                 1, "Human oversight and per-group monitoring are key protections."),
            ],
        },
        # ------------------------------------------------------------------ 20
        {
            "title": "Explainable AI",
            "minutes": 40,
            "video": "https://www.youtube.com/watch?v=yJkCuEu3K68",
            "content": """
**Learning objective:** Explain why some AI models are "black boxes", why explanations matter, and describe common ways to explain a model's decisions.

## The black-box problem

A decision tree can show its reasoning: *sales above 100,000 RWF → few late payments → approve.* A deep neural network with millions of weights cannot. It may be very accurate, but nobody can easily say **why** it made a particular decision. Such models are called **black boxes**.

This matters when a decision affects someone's life. If a bank's AI refuses your loan, you deserve to know why — and the bank needs to be sure the reason is legitimate, not a hidden bias.

## Why explanations matter

| Who | Why they need explanations |
|---|---|
| **The affected person** | To understand, challenge or fix the decision ("increase my savings history") |
| **The organisation** | To trust the model, catch mistakes and meet legal duties |
| **Engineers** | To debug the model and find data problems or leakage |
| **Regulators** | To check the system is safe and fair |

## Interpretable models vs. explaining black boxes

There are two approaches:

1. **Use an interpretable model** — linear or logistic regression, small decision trees. You can read the logic directly. Often good enough, especially for tabular data.
2. **Explain a complex model after training** — use tools that describe what the black box is doing.

A good rule: **start with the simplest model that works.** Use a black box only when it is clearly better, and then add explanation tools.

## Common explanation methods

- **Feature importance** — which features matter most to the model overall. "Repayment history is the strongest factor, then monthly sales."
- **Local explanations** — why *this one* decision was made. Tools such as **LIME** and **SHAP** estimate how much each feature pushed a single prediction up or down.
- **Counterfactual explanations** — what would need to change for a different result. "If your monthly sales were 30,000 RWF higher, the loan would be approved." These are often the most useful for ordinary people.
- **Saliency maps** — for images, highlight which pixels the model focused on. A crop-disease model should focus on the leaf spots, not the background soil.

## Explanations can reveal hidden problems

A famous lesson from research: a model that seemed to tell wolves from huskies was really looking at **snow in the background** — most wolf photos had snow. Only an explanation method revealed the shortcut. Explanations help catch models that are right for the wrong reasons.

## Limits of explanations

Explanation tools give **approximations**, not the full truth of a complex model. Different tools can disagree. Explanations support human judgement; they do not replace it.

**Takeaway:** Black-box models can be accurate but hard to understand. Prefer interpretable models where possible; otherwise use feature importance, local explanations and counterfactuals — and remember they are approximations.

## Try it yourself

1. Imagine an AI rejects a student's scholarship application. Write the explanation the student should receive, in plain words, including a counterfactual ("If… then…").
2. A crop-disease model's saliency map shows it focuses on the soil, not the leaf. What could be wrong with the training data? Suggest one fix.
""",
            "quiz": [
                ("What is a 'black-box' model?",
                 ["A model stored in a black case", "A model whose reasons for a decision are hard to see or explain", "A model with no data", "A model that only works at night"],
                 1, "Complex models like deep networks can be accurate but hard to interpret."),
                ("Which model is usually easiest to interpret directly?",
                 ["A deep neural network with millions of weights", "A small decision tree", "A large language model", "A random mix of models"],
                 1, "You can read the decision path of a small tree directly."),
                ("'If your monthly sales were 30,000 RWF higher, the loan would be approved.' This is a…",
                 ["Counterfactual explanation", "Loss function", "Saliency map", "Confusion matrix"],
                 0, "A counterfactual explains what would need to change to get a different outcome."),
                ("What do LIME and SHAP help with?",
                 ["Collecting data", "Explaining how features pushed one particular prediction", "Training faster", "Storing passwords"],
                 1, "They are local explanation methods for individual predictions."),
                ("A wolf-vs-husky model was really detecting snow. What does this show?",
                 ["Explanations can reveal a model that is right for the wrong reasons", "Snow is a good feature", "Models cannot be explained", "Wolves only live in snow"],
                 0, "Explanation methods exposed a shortcut that would fail on new photos."),
                ("What is an important limit of explanation tools?",
                 ["They give approximations and can disagree", "They are always 100% exact", "They replace all human judgement", "They only work on text"],
                 0, "Explanations support judgement; they are not a perfect view inside the model."),
            ],
        },
        # ------------------------------------------------------------------ 21
        {
            "title": "Privacy, Security and Safety",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=gEtTVlQsGcQ",
            "content": """
**Learning objective:** Explain the main privacy, security and safety risks of AI systems, describe key duties under Rwanda's data-protection law, and apply basic protections.

## Three different questions

- **Privacy** — Is personal information collected and used fairly and lawfully?
- **Security** — Can attackers trick, steal or break the AI system?
- **Safety** — Could the system cause harm, even when nobody is attacking it?

## Privacy and personal data

AI runs on data, and much of it is **personal**: names, phone numbers, ID numbers, locations, health records, photos and voice. Risks include:

- Collecting more data than needed.
- Using data for a purpose people never agreed to.
- Data **leaks** and breaches.
- Models that **memorise** and later repeat personal details from their training data.
- Users pasting confidential information into public chatbots.

## Rwanda's data-protection law

Rwanda's **Law No. 058/2021 of 13/10/2021 relating to the protection of personal data and privacy** sets the rules. The **National Cyber Security Authority (NCSA)** supervises it. Key ideas every AI builder in Rwanda should know:

- Have a **lawful basis** (such as clear consent) for processing personal data.
- Collect only what you **need**, for a stated **purpose**.
- Keep data **accurate** and **secure**, and not longer than necessary.
- Respect people's **rights** — to be informed, to access their data, to correct it and to object.
- Organisations that process personal data must **register** with the supervisory authority.
- Personal data should generally be **stored in Rwanda**, unless the authority allows otherwise.

Always check the current official text and guidance from NCSA before building a real system.

## Privacy protections

- **Data minimisation** — use only the data you need.
- **Anonymisation / pseudonymisation** — remove or replace names and IDs.
- **Access control** — only the right people can see the data.
- **Encryption** — protect data when stored and when sent.
- **Never paste** customer, patient or company secrets into public AI tools unless your organisation allows it.

## Security threats to AI

| Threat | What it is | Example |
|---|---|---|
| **Adversarial examples** | Tiny changes to input that fool a model | Stickers on a road sign confuse a car's camera |
| **Data poisoning** | Attackers add bad examples to training data | Fake reviews that teach a model wrong patterns |
| **Prompt injection** | Hidden instructions that hijack a chatbot or AI agent | A web page tells an AI assistant to leak the user's data |
| **Model theft** | Copying a model by querying it many times | A competitor clones a paid model |
| **Deepfakes** | Realistic fake audio, images or video | A fake voice of a manager asking staff to send money |

## Safety

Even without attackers, AI can cause harm: wrong medical advice, a self-driving error, a chatbot encouraging dangerous behaviour, or an automated system that fails silently. Safety practices include:

- **Testing** in realistic conditions, including rare and difficult cases.
- **Human oversight** for high-stakes decisions.
- **Clear limits** — tell users what the system can and cannot do.
- **Monitoring and a way to switch off** or roll back the system.
- **Reporting channels** so users can flag problems.

Researchers also study **alignment**: making sure powerful AI systems pursue the goals people actually intend.

**Takeaway:** Protect personal data (follow Law No. 058/2021), defend AI systems against attacks like poisoning and prompt injection, and design for safety with testing, oversight and monitoring.

## Try it yourself

1. Take your Week 2 project plan. List every piece of personal data it uses and whether you truly need it.
2. Write a one-paragraph privacy notice a user would understand.
3. Name one security threat and one safety risk for your system, with one protection for each.
""",
            "quiz": [
                ("Which question is about privacy?",
                 ["Can attackers fool the model?", "Is personal information collected and used fairly and lawfully?", "How fast is the GPU?", "How many layers does the model have?"],
                 1, "Privacy concerns the fair and lawful use of personal information."),
                ("Which law protects personal data in Rwanda?",
                 ["Law No. 058/2021 relating to the protection of personal data and privacy", "The EU traffic law", "There is no such law", "A school rule"],
                 0, "Law No. 058/2021 of 13/10/2021 sets Rwanda's data-protection rules, supervised by NCSA."),
                ("What is data minimisation?",
                 ["Making files smaller", "Collecting and using only the data you need", "Deleting the model", "Using cheaper computers"],
                 1, "Collect only what is necessary for a stated purpose."),
                ("Hidden text on a web page tells an AI assistant to leak the user's data. This is…",
                 ["Prompt injection", "Gradient descent", "Clustering", "Feature engineering"],
                 0, "Prompt injection hides instructions that hijack an AI system's behaviour."),
                ("Attackers add fake examples to a model's training data. This is…",
                 ["Data poisoning", "Early stopping", "Recall", "Tokenisation"],
                 0, "Poisoning corrupts training data so the model learns wrong patterns."),
                ("Which is a good safety practice for high-stakes AI?",
                 ["No testing, to save time", "Human oversight, monitoring and a way to switch the system off", "Hiding all limits from users", "Removing reporting channels"],
                 1, "Testing, oversight, clear limits and the ability to stop the system reduce harm."),
            ],
        },
        # ------------------------------------------------------------------ 22
        {
            "title": "AI Governance and Policy",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=9B02MzWwkSo",
            "content": """
**Learning objective:** Describe how governments and organisations govern AI, summarise Rwanda's National AI Policy and the EU AI Act's risk-based approach, and write simple governance rules for an organisation.

## What is AI governance?

**AI governance** is the set of rules, roles and processes that make sure AI is developed and used **safely, fairly, lawfully and for the public good**. It happens at three levels:

1. **International** — shared principles between countries.
2. **National** — laws, policies and regulators.
3. **Organisational** — a company's or ministry's own rules for using AI.

## International principles

- The **OECD AI Principles** (2019) — AI should be inclusive, respect human rights, be transparent, robust and safe, with clear accountability.
- The **UNESCO Recommendation on the Ethics of Artificial Intelligence** (2021) — adopted by UNESCO's member states, focused on human rights, fairness, environment and diversity.
- The **African Union Continental AI Strategy** (2024) — an African approach that stresses development, skills, inclusion and African data and languages.

## Rwanda's National AI Policy

Rwanda's Cabinet approved a **National Artificial Intelligence Policy in 2023**, developed by the Ministry of ICT and Innovation with partners including C4IR Rwanda. It aims to make Rwanda a leader in responsible, inclusive AI in Africa. Its priority areas include:

- **Skills** — AI literacy and 21st-century skills, from schools to universities.
- **Infrastructure and computing power** — the hardware and connectivity AI needs.
- **Data** — a strategy for making quality data available while protecting privacy.
- **Public sector** — trustworthy AI to improve government services.
- **Private sector** — helping businesses adopt AI widely.
- **Ethics** — practical guidelines for responsible AI.

This policy works together with the data-protection law you studied in Lesson 21.

## The EU AI Act — a risk-based model

The European Union's **AI Act** entered into force in **August 2024**, with its rules applying in stages. It matters to African companies too, because anyone offering AI in the EU must follow it. Its core idea is to **regulate according to risk**:

| Risk level | Examples | What the law requires |
|---|---|---|
| **Unacceptable** | Social scoring of citizens; manipulative systems that exploit vulnerable people | **Banned** |
| **High** | AI for hiring, credit scoring, education access, medical devices, critical infrastructure | Strict duties: risk management, quality data, documentation, human oversight, accuracy |
| **Limited** | Chatbots, AI-generated content | **Transparency**: tell people they are dealing with AI, label deepfakes |
| **Minimal** | Spam filters, AI in video games | No special duties |

The risk-based idea is useful everywhere: **the more an AI system can affect people's rights and safety, the more care and control it needs.**

## Governance inside an organisation

Every organisation that uses AI — a school, a bank, a start-up — should have simple, written rules:

1. **An AI use policy** — which tools staff may use, and for what.
2. **Data rules** — what information must never go into external AI tools.
3. **Risk review** — high-impact uses (people's money, jobs, health) need extra checks before launch.
4. **Human accountability** — a named person is responsible for each AI system.
5. **Transparency** — tell customers when AI is used and how to reach a human.
6. **Monitoring and incident reporting** — track problems and fix them.

**Takeaway:** AI governance works at international, national and organisational levels. Rwanda has a National AI Policy (2023) and a data-protection law; the EU AI Act regulates by risk. Every organisation needs its own clear AI rules.

## Try it yourself

1. Classify these systems using the EU AI Act risk levels: a CV-screening tool, a customer-service chatbot, a spam filter, a credit-scoring app, a system that scores citizens' behaviour.
2. Write a one-page AI use policy (six short rules) for a small business or school you know.
""",
            "quiz": [
                ("What is AI governance?",
                 ["A type of neural network", "Rules, roles and processes that keep AI safe, fair, lawful and beneficial", "A programming language", "A data format"],
                 1, "Governance covers how AI is controlled and held accountable at every level."),
                ("When did Rwanda's Cabinet approve the National AI Policy?",
                 ["2016", "2019", "2023", "It has not been approved"],
                 2, "Rwanda approved its National Artificial Intelligence Policy in 2023."),
                ("What is the core idea of the EU AI Act?",
                 ["All AI is banned", "Rules depend on the level of risk a system poses", "Only games are regulated", "AI needs no rules"],
                 1, "The Act is risk-based: higher risk means stricter requirements."),
                ("Under the EU AI Act, a system that socially scores citizens is…",
                 ["Minimal risk", "Limited risk", "Unacceptable — banned", "High risk but allowed without rules"],
                 2, "Social scoring of citizens is an unacceptable risk and is banned."),
                ("An AI tool that screens job applicants is classed as…",
                 ["Minimal risk", "High risk, with strict duties", "Unacceptable", "Not AI"],
                 1, "Hiring systems affect people's livelihoods, so they are high-risk."),
                ("Which rule belongs in an organisation's AI policy?",
                 ["Staff may paste any customer data into any AI tool", "A named person is accountable for each AI system", "Never tell customers AI is used", "No monitoring is needed"],
                 1, "Clear human accountability is a core governance rule."),
            ],
        },
        # ------------------------------------------------------------------ 23
        {
            "title": "Careers in AI",
            "minutes": 40,
            "video": "https://www.youtube.com/watch?v=MIbP9kgCc4w",
            "content": """
**Learning objective:** Describe the main career paths in AI, the skills each one needs, and build a personal learning path for the next year.

## AI needs many kinds of people

AI is not only for people with PhDs in mathematics. Real AI products need a whole team — and many of the most valuable people combine **AI understanding with knowledge of a specific field** such as health, farming, finance or education.

## Technical roles

| Role | What they do | Key skills |
|---|---|---|
| **Data analyst** | Cleans data, makes charts and reports, finds insights | Excel, SQL, statistics, visualisation |
| **Data scientist** | Builds and evaluates models to answer business questions | Python, statistics, machine learning, communication |
| **Machine-learning engineer** | Turns models into reliable software that runs at scale | Python, software engineering, cloud, MLOps |
| **Data engineer** | Builds the pipelines that collect, store and move data | SQL, databases, cloud, programming |
| **AI / LLM application developer** | Builds apps and agents on top of language models | Programming, APIs, prompt design, evaluation |
| **AI researcher** | Invents new methods | Advanced maths, research, deep learning |

## Non-technical and hybrid roles

- **AI product manager** — decides what to build and why, for real users.
- **AI ethics, policy and governance specialist** — fairness, privacy, regulation (Lessons 19–22).
- **Data annotator / quality lead** — creates and checks labelled data.
- **AI trainer / educator** — teaches teams and students to use AI well.
- **Domain expert using AI** — a nurse, agronomist, accountant or teacher who uses AI to work better. This is the largest group of all.

## Skills that last

Tools change every year; these skills keep their value:

1. **Problem framing** — turning a real need into a clear AI problem (Weeks 1–2).
2. **Data thinking** — knowing what makes data good or bad.
3. **Evaluation** — judging results honestly (Week 3).
4. **Responsible AI** — fairness, privacy and safety (Week 4).
5. **Communication** — explaining AI to non-experts in simple words.
6. **Python and statistics** — the base for any technical path.

## The Rwandan ecosystem

Rwanda has a growing tech community: universities and institutes such as **Carnegie Mellon University Africa** and **AIMS Rwanda** in Kigali, innovation hubs such as **kLab** and **Norrsken House Kigali**, and a national AI policy that prioritises skills. Join meet-ups, hackathons and online communities — many first jobs come from people you meet and projects you show.

## Build a portfolio, not just certificates

Employers want **proof you can do the work**:

- 2–3 small projects on real local problems (your Week 1–4 projects are a start).
- Clear write-ups: the problem, the data, the method, the results, the limits.
- A public profile (GitHub for code, LinkedIn for your story).

## Your next steps in the WAMUGII AI Program

After AI Foundations, continue with **Math & Python for AI**, then **Machine Learning Fundamentals**, **Deep Learning & Neural Networks**, **Modern AI: LLMs & Generative AI**, and **Responsible AI & Deployment**. Each builds directly on what you learned here.

**Takeaway:** AI careers include technical, hybrid and domain roles. Lasting skills are problem framing, data thinking, evaluation, responsibility and communication. Build a portfolio of real projects.

## Try it yourself

1. Choose one role from this lesson that fits you best and explain why in three sentences.
2. Write a 12-month learning path: three skills to learn, one project for each, and one community to join.
3. Find one job advert for that role (in Rwanda or remote) and list the five skills it asks for most.
""",
            "quiz": [
                ("Which statement about AI careers is true?",
                 ["Only PhD researchers can work in AI", "AI teams need many roles, including people who combine AI with knowledge of a field", "AI jobs need no communication skills", "There are no AI jobs in Africa"],
                 1, "Real AI products need analysts, engineers, product people, ethicists and domain experts."),
                ("Who turns models into reliable software that runs at scale?",
                 ["Machine-learning engineer", "Data annotator", "AI ethicist", "Graphic designer"],
                 0, "ML engineers bring software engineering skills to deploy and maintain models."),
                ("Which skill keeps its value even as AI tools change?",
                 ["Memorising one app's buttons", "Problem framing and honest evaluation", "Typing fast", "Using one specific version of a tool"],
                 1, "Framing problems, thinking about data and evaluating honestly stay valuable."),
                ("What do employers most want to see from a new AI learner?",
                 ["Only a long list of certificates", "A portfolio of real projects with clear write-ups", "Expensive laptops", "Social media followers"],
                 1, "Projects prove you can do the work; certificates alone do not."),
                ("A nurse who uses AI tools to improve patient care is an example of…",
                 ["A domain expert using AI", "An AI researcher", "A data engineer", "Someone outside the AI economy"],
                 0, "Domain experts using AI form the largest and fastest-growing group."),
                ("Which WAMUGII course comes right after AI Foundations?",
                 ["Responsible AI & Deployment", "Math & Python for AI", "Deep Learning & Neural Networks", "Modern AI: LLMs & Generative AI"],
                 1, "The next step is Math & Python for AI, the base for the technical courses."),
            ],
        },
        # ------------------------------------------------------------------ 24
        {
            "title": "Final Project: AI Problem Analysis and Certificate",
            "minutes": 90,
            "video": "https://www.youtube.com/watch?v=hQX_wIW9Nh0",
            "content": """
**Learning objective:** Produce a complete, professional AI problem analysis that brings together all four weeks — and earn your AI Foundations certificate.

## About the final project

Choose one real problem in Rwanda or your community that AI could help with. Write an **AI Problem Analysis** of 4–6 pages (or 12–15 slides). Build on your Week 1, 2 and 3 projects — you have already done much of the thinking.

This is the kind of document a consultant, analyst or founder writes before any money is spent on building. It is also a strong first item for your portfolio.

## Part 1 — The problem (Week 1)

- Who has the problem, how big is it, and how is it handled today?
- Describe the AI system as an **agent**: write its **PEAS** table and classify its **environment**.
- Name the **problem type** (classification, regression, clustering, generation…).

## Part 2 — The learning plan (Week 2)

- **Learning type** — supervised, unsupervised or reinforcement, and why.
- **Data** — features and label, sources, quality risks, leakage check, and whether the data is **representative**.
- **Workflow** — a short plan for each of the seven stages, including deployment and monitoring for **drift**.
- Could a simple rule do the job instead? Justify using AI.

## Part 3 — Model and evaluation (Week 3)

- A **baseline** method and a stronger method, with the trade-off.
- How you will split data (training, validation, test).
- The **main measure** (accuracy, precision, recall, MAE…) and why — which mistake is more costly?
- A numeric **success target**.

## Part 4 — Responsible AI (Week 4)

- **Fairness** — which groups could get worse results, and which per-group checks you will run.
- **Explainability** — how will a person understand or challenge a decision?
- **Privacy and security** — which personal data is used, how you will follow Rwanda's data-protection law, and one security threat with a protection.
- **Governance** — the risk level (using the EU AI Act categories as a guide), who is accountable, and how users can reach a human.

## Part 5 — Recommendation

One page: should this project go ahead? What is the first small step (a pilot)? What would make you stop?

## Marking guide (self-check)

| Area | What "excellent" looks like |
|---|---|
| Problem framing | Clear user, decision and numeric success measure |
| Technical correctness | Correct agent, problem type, learning type and measures |
| Data thinking | Specific features, honest quality and representativeness risks |
| Responsibility | Concrete fairness, privacy and governance steps — not general words |
| Communication | Simple English, clear structure, a busy reader understands quickly |

## Getting your certificate

1. Complete **every lesson** in the course (tick each one as done).
2. Finish your final project and keep it in your portfolio.
3. When all lessons are complete, your **WAMUGII Certificate of Completion** unlocks on the course page and you receive a congratulations email. Download it and add it to your CV and LinkedIn.

## What you have achieved

You can now explain AI precisely, describe any AI system as an agent, frame problems correctly, understand how models learn and are evaluated, and judge AI's impact on people and society. That foundation sets you apart from people who only *use* AI tools without understanding them.

**Takeaway:** A strong AI problem analysis connects the problem, the data, the method, honest evaluation and responsible use — in clear language anyone can follow.

## Try it yourself

Complete Parts 1–5. Ask one person from the field you chose (a teacher, nurse, farmer, trader or official) to read your recommendation and tell you what they think. Add their feedback as a final short section — real feedback is what turns a school project into professional work.
""",
            "quiz": [
                ("What does Part 1 of the final project cover?",
                 ["Only the budget", "The problem, the agent's PEAS table, its environment and the problem type", "The certificate design", "Only the code"],
                 1, "Part 1 applies Week 1: problem, agent description, environment and problem type."),
                ("Why include a baseline method in your analysis?",
                 ["To have a reference point a stronger method must beat", "Because baselines are always best", "To fill pages", "It is not needed"],
                 0, "A baseline shows what simple methods achieve, so complex methods must prove their worth."),
                ("Which part of the project checks fairness, privacy and governance?",
                 ["Part 1", "Part 3", "Part 4 — Responsible AI", "None"],
                 2, "Part 4 brings in Week 4: fairness, explainability, privacy, security and governance."),
                ("What should the recommendation include?",
                 ["Whether to go ahead, a first small pilot step, and what would make you stop", "Only praise for AI", "The model's source code", "A list of programming languages"],
                 0, "A good recommendation is decisive, starts small and names stopping conditions."),
                ("How is the AI Foundations certificate issued?",
                 ["By posting a letter", "It unlocks on the course page when every lesson is completed", "Only after paying a fee", "It is not available"],
                 1, "Completing all lessons unlocks the certificate on the course page, and a congratulations email is sent."),
                ("What does 'excellent' communication look like in the marking guide?",
                 ["Long, complex sentences with many technical words", "Simple English and clear structure that a busy reader understands quickly", "No headings at all", "Only tables"],
                 1, "Clear, simple writing is a professional skill and part of the marking guide."),
            ],
        },
    ],
}
