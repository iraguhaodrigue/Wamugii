"""AI Foundations -- Week 1: What AI Is. Original WAMUGII content."""

WEEK1 = {
    "title": "Week 1 · What AI Is",
    "lessons": [
        # ------------------------------------------------------------------ 1
        {
            "title": "Defining AI: AI, Machine Learning and Deep Learning",
            "minutes": 40,
            "video": "https://www.youtube.com/watch?v=4RixMPF4xis",
            "content": """
**Learning objective:** Give a precise definition of artificial intelligence, explain how AI, machine learning and deep learning fit inside each other, and place a real product in the right circle.

## A precise definition

In everyday talk, "AI" can mean almost anything. In this course we use the definition most university textbooks use:

> **Artificial intelligence** is the study and building of systems that **perceive** their surroundings, **reason** about what they perceive, and **act** to reach a goal — doing tasks that normally need human intelligence.

Notice what the definition does *not* say. It does not say "a computer that thinks like a human". A system is intelligent because it reaches goals well, not because it copies the human brain. An aeroplane flies very well without flapping its wings like a bird.

## Three circles inside each other

Picture three circles, one inside the other:

| Circle | What it means | Example |
|---|---|---|
| **Artificial intelligence** (biggest) | Any technique that makes machines act intelligently — including hand-written rules and search | A chess program that searches millions of moves |
| **Machine learning** (inside AI) | Systems that **learn patterns from data** instead of following only hand-written rules | A model that predicts loan risk from past loans |
| **Deep learning** (inside ML) | Machine learning with **many-layered neural networks**, trained on large data | Face unlock on your phone, ChatGPT |

So every deep-learning system is a machine-learning system, and every machine-learning system is an AI system — but not the other way round.

## Two big families of AI

- **Symbolic AI (rule-based)** — people write the knowledge as rules and logic: *IF fever AND rash THEN check for measles.* Strong when rules are clear; weak when the world is messy.
- **Statistical AI (learning-based)** — the system learns from examples. Strong on messy data like photos, speech and language; weaker at explaining itself.

Most modern products use learning, but many still mix both. A bank's fraud system may use a learned model *and* hard rules such as "block any transfer above the daily limit".

## Narrow AI and general AI

- **Narrow AI** does one kind of task: translating, recognising faces, recommending videos. **All AI that exists today is narrow**, even very capable chatbots.
- **Artificial general intelligence (AGI)** would match people across almost all thinking tasks. It is a research goal and a topic of debate, not a product you can buy.

Be careful with headlines. "AI can now do X" usually means *one narrow system* does X under certain conditions.

## Key terms

- **Agent** — anything that perceives and acts (you will study agents in Lesson 3).
- **Model** — the learned pattern stored after training.
- **Training** — the process of learning a model from data.
- **Inference** — using a trained model to make a prediction on new input.
- **Algorithm** — a step-by-step method; a learning algorithm produces a model.

**Takeaway:** AI is the big field; machine learning is the part that learns from data; deep learning is the part of ML that uses large neural networks. All of today's AI is narrow.

## Try it yourself

1. List five apps you used this week (for example MoMo, Google Maps, WhatsApp, YouTube, Irembo).
2. For each one, name one feature that might use AI.
3. Place each feature in a circle: rule-based AI, machine learning, or deep learning. Write one sentence explaining your choice.
4. Keep this list — you will use it again in the Week 1 project.
""",
            "quiz": [
                ("Which definition of AI matches this lesson best?",
                 ["A computer that has feelings", "Systems that perceive, reason and act to reach goals that normally need human intelligence", "Any program that uses the internet", "A robot with a human body"],
                 1, "AI is about perceiving, reasoning and acting well towards a goal. It does not need feelings, a body or the internet."),
                ("How are AI, machine learning and deep learning related?",
                 ["They are three unrelated fields", "Deep learning contains machine learning, which contains AI", "AI contains machine learning, which contains deep learning", "Machine learning is bigger than AI"],
                 2, "AI is the largest circle. Machine learning sits inside it, and deep learning sits inside machine learning."),
                ("A system follows the rule 'IF fever AND rash THEN check for measles'. What kind of AI is this?",
                 ["Symbolic (rule-based) AI", "Deep learning", "Unsupervised learning", "General AI"],
                 0, "Knowledge written by people as IF-THEN rules is symbolic, rule-based AI."),
                ("Which statement about today's AI is correct?",
                 ["Most AI products are general AI", "All AI that exists today is narrow AI", "Narrow AI cannot be useful", "AGI is sold in app stores"],
                 1, "Every system available today is narrow, even powerful chatbots. AGI remains a research goal."),
                ("What is 'inference'?",
                 ["Collecting data", "Using a trained model to make a prediction on new input", "Writing rules by hand", "Deleting a model"],
                 1, "Training builds the model; inference is when the finished model is used on new inputs."),
                ("Face unlock on a smartphone is best described as…",
                 ["Deep learning", "A hand-written rule", "Not AI at all", "General AI"],
                 0, "Face recognition uses many-layered neural networks trained on many images — deep learning."),
            ],
        },
        # ------------------------------------------------------------------ 2
        {
            "title": "A Short History of AI",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=fa8k8IQ1_X0",
            "content": """
**Learning objective:** Describe the main periods in the history of AI, explain why progress came in waves, and say what changed after 2012.

## Why history matters

AI is not new. Knowing its history helps you judge today's claims. Again and again, people expected human-level AI "within 20 years" — and were wrong. Again and again, quiet research later became huge products.

## The timeline

| Year | Event | Why it matters |
|---|---|---|
| 1950 | Alan Turing publishes *Computing Machinery and Intelligence* and proposes the "imitation game" (the Turing Test) | Asked seriously: can machines think? |
| 1956 | The Dartmouth workshop; John McCarthy uses the term **"artificial intelligence"** | AI becomes a research field |
| 1958 | Frank Rosenblatt builds the **perceptron**, an early neural network | First machine that learned from examples |
| 1970s | First **"AI winter"** — funding falls after promises are not met | Hype has a cost |
| 1980s | **Expert systems** — big rule-based programs used in business | Symbolic AI goes commercial |
| late 1980s–1990s | Second AI winter; expert systems prove costly to maintain | Hand-written rules do not scale |
| 1997 | IBM's **Deep Blue** beats world chess champion Garry Kasparov | Search plus fast hardware wins |
| 2012 | A deep neural network (**AlexNet**) wins the ImageNet image-recognition contest by a wide margin | The **deep-learning era** begins |
| 2016 | DeepMind's **AlphaGo** beats Go champion Lee Sedol | Learning plus search beats humans in a far harder game |
| 2017 | Google researchers publish *Attention Is All You Need* — the **transformer** | The design behind today's language models |
| 2022 | **ChatGPT** is released and reaches millions of users within weeks | AI becomes an everyday tool |

## Why progress came in waves

Each big jump needed three things at the same time:

1. **Data** — the internet and smartphones created huge collections of text, images and sound.
2. **Computing power** — graphics chips (**GPUs**), first made for video games, turned out to be perfect for training neural networks.
3. **Better methods** — new ideas such as deep networks and transformers.

When one of the three was missing, progress slowed and funding fell — an AI winter. When all three came together after 2012, progress became very fast.

## AI in Africa and Rwanda

Africa is not only a user of AI. Some examples:

- **Zipline** has delivered blood and medical supplies by autonomous drone in Rwanda since 2016, using software to plan routes and flights.
- Rwanda's Cabinet approved a **National AI Policy in 2023**, with goals for skills, data, infrastructure and responsible use.
- Kigali hosts the **Centre for the Fourth Industrial Revolution (C4IR) Rwanda** and has hosted international AI meetings, including the Global AI Summit on Africa in 2025.
- Researchers across the continent build tools for African languages such as Kinyarwanda, Swahili and Yoruba, which big global models often handle poorly.

## Key terms

- **AI winter** — a period when interest and funding in AI fell sharply.
- **Expert system** — a program that stores expert knowledge as many rules.
- **GPU** — a graphics processing unit; it does many small calculations at once, which makes training fast.
- **Transformer** — the neural network design behind modern language models (Lesson 17).

**Takeaway:** AI grew in waves. The current boom comes from data, computing power and better methods arriving together — and history warns us to be careful with hype.

## Try it yourself

1. Pick one event from the timeline.
2. Write a short paragraph (5–6 sentences): what happened, which of the three ingredients (data, computing, methods) made it possible, and what it changed.
3. Find one recent AI headline. Write one sentence on whether it sounds like careful progress or hype, and why.
""",
            "quiz": [
                ("Who proposed the 'imitation game', later called the Turing Test?",
                 ["John McCarthy", "Alan Turing", "Garry Kasparov", "Frank Rosenblatt"],
                 1, "Alan Turing proposed it in his 1950 paper 'Computing Machinery and Intelligence'."),
                ("What happened at the 1956 Dartmouth workshop?",
                 ["ChatGPT was released", "The term 'artificial intelligence' was used and AI became a research field", "Deep Blue beat Kasparov", "The first GPU was built"],
                 1, "John McCarthy and colleagues organised the workshop; it is seen as the birth of AI as a field."),
                ("What is an 'AI winter'?",
                 ["A cold-weather robot", "A period when interest and funding in AI fell sharply", "A type of neural network", "The season when models are trained"],
                 1, "AI winters followed periods when big promises were not met, so funding dropped."),
                ("Which event is usually seen as the start of the deep-learning era?",
                 ["Deep Blue in 1997", "AlexNet winning ImageNet in 2012", "Expert systems in the 1980s", "The Dartmouth workshop"],
                 1, "AlexNet's large win in 2012 showed the power of deep neural networks trained on GPUs."),
                ("Which three ingredients drove the recent boom in AI?",
                 ["Robots, satellites and cables", "Data, computing power and better methods", "Laws, schools and money", "Phones, apps and games only"],
                 1, "Large data, fast GPUs and new methods such as deep networks and transformers came together."),
                ("Which 2017 paper introduced the transformer?",
                 ["Computing Machinery and Intelligence", "Attention Is All You Need", "The Perceptron", "Deep Blue Report"],
                 1, "'Attention Is All You Need' (2017) introduced the transformer design used by modern language models."),
            ],
        },
        # ------------------------------------------------------------------ 3
        {
            "title": "Intelligent Agents and Environments",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=BkedAnQfJ_U",
            "content": """
**Learning objective:** Describe any AI system as an agent, use the PEAS method to specify it, and classify its environment.

## What is an agent?

An **agent** is anything that **perceives** its environment through **sensors** and **acts** on it through **actuators**.

- A person: eyes and ears are sensors; hands and voice are actuators.
- A self-driving car: cameras and radar are sensors; steering and brakes are actuators.
- A chatbot: your typed message is its input (sensor); its reply is its action.

An agent's **percept** is what it senses at one moment. Its **agent function** maps what it has perceived so far to an action. The goal of AI is to build **rational agents**: agents that choose the action expected to give the best result, given what they know.

Rational does not mean perfect. A rational agent can still be wrong when it lacks information — just like a careful doctor who has not yet seen a test result.

## Specifying an agent with PEAS

Before building an agent, engineers describe its task with **PEAS**:

| Letter | Question | Example: a delivery drone in Rwanda |
|---|---|---|
| **P**erformance measure | How do we judge success? | On-time delivery, safety, battery use, cost |
| **E**nvironment | Where does it work? | Hills, wind, rain, airspace, hospitals |
| **A**ctuators | How does it act? | Motors, parachute release, radio messages |
| **S**ensors | How does it perceive? | GPS, cameras, wind and battery sensors |

Getting the **performance measure** right is the most important step. If you reward a drone only for speed, it may take unsafe risks. What you measure is what you get.

## Kinds of environments

| Property | One side | Other side |
|---|---|---|
| Observable | **Fully** — the agent sees everything it needs (chess board) | **Partially** — some things are hidden (a driver cannot see round a corner) |
| Outcome | **Deterministic** — the same action always gives the same result | **Stochastic** — chance plays a part (weather, other people) |
| Time | **Episodic** — each decision stands alone (sorting photos) | **Sequential** — today's action changes tomorrow (driving, investing) |
| Change | **Static** — the world waits while the agent thinks | **Dynamic** — the world keeps moving (traffic) |
| Agents | **Single-agent** | **Multi-agent** — others act too (football, markets) |

The harder side of each row makes the agent harder to build. A self-driving car in Kigali traffic faces almost all the hard sides: partially observable, stochastic, sequential, dynamic and multi-agent.

## Types of agents (simplest to most capable)

1. **Simple reflex agent** — reacts to the current percept with a rule (*if the room is dark, turn on the light*).
2. **Model-based agent** — keeps an internal picture of the world, so it can handle what it cannot see right now.
3. **Goal-based agent** — plans actions to reach a goal (*reach the hospital*).
4. **Utility-based agent** — compares how *good* different outcomes are (*reach the hospital fast, safely and cheaply*).
5. **Learning agent** — improves its own behaviour from experience.

**Takeaway:** Any AI system can be described as an agent that senses and acts. PEAS makes the task clear, and the type of environment tells you how hard the problem is.

## Try it yourself

1. Choose one system: a MoMo fraud detector, a crop-disease app, a customer-service chatbot or a traffic-light controller.
2. Write its full PEAS table.
3. Classify its environment on all five properties and explain each choice in one sentence.
4. Say which type of agent it most likely is.
""",
            "quiz": [
                ("What is an agent in AI?",
                 ["Only a human customer-service worker", "Anything that perceives its environment through sensors and acts through actuators", "A type of computer virus", "A database"],
                 1, "An agent senses (perceives) and acts. People, robots and software can all be agents."),
                ("In PEAS, what does the P stand for?",
                 ["Program", "Performance measure", "Prediction", "Power"],
                 1, "P is the performance measure: how success is judged. It shapes everything the agent does."),
                ("A driver cannot see what is round the next corner. This environment is…",
                 ["Fully observable", "Partially observable", "Static", "Single-agent"],
                 1, "When some needed information is hidden, the environment is partially observable."),
                ("Which agent compares how good different outcomes are, not just whether a goal is reached?",
                 ["Simple reflex agent", "Utility-based agent", "Model-based agent", "Episodic agent"],
                 1, "A utility-based agent weighs outcomes, for example speed, safety and cost together."),
                ("What does 'rational agent' mean?",
                 ["An agent that is never wrong", "An agent that chooses the action expected to give the best result, given what it knows", "An agent with feelings", "An agent with no sensors"],
                 1, "Rational means doing the best expected thing with the information available. It can still be wrong."),
                ("Why is the performance measure so important?",
                 ["It decides the colour of the robot", "The agent will pursue whatever is measured, so a bad measure leads to bad behaviour", "It is only needed for games", "It replaces the sensors"],
                 1, "What you measure is what you get. Rewarding only speed can make an agent unsafe."),
            ],
        },
        # ------------------------------------------------------------------ 4
        {
            "title": "The Types of AI Problems",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=R9OHn5ZF4Uo",
            "content": """
**Learning objective:** Name the main types of AI problems, recognise each one from a real-world description, and choose the right type for a new problem.

## Why problem type comes first

Before choosing a tool or a model, an AI practitioner asks one question: **what kind of output do we need?** The answer decides the data you collect, the method you use and how you measure success. Getting the problem type wrong is one of the most common and expensive mistakes in AI projects.

## The main problem types

| Type | Output | Real example |
|---|---|---|
| **Classification** | A category (a label from a fixed list) | Is this MoMo transaction *fraud* or *normal*? Is this cassava leaf *healthy*, *mosaic disease* or *brown streak*? |
| **Regression** | A number | What will this house in Kicukiro sell for? How many litres of milk will the cooperative collect next week? |
| **Clustering** | Groups that the data forms by itself, with no labels given | Group customers by buying habits so you can market to each group |
| **Recommendation** | A ranked list of items for a person | Which videos or products to show this user next |
| **Anomaly detection** | "This is unusual" | Spot a strange login or a broken machine sensor |
| **Generation** | New content: text, images, audio, code | Write a product description; draw an illustration |
| **Sequential decision-making** | A series of actions | A robot finding its way; a game-playing agent |

## Classification vs. regression — the classic pair

The easiest test: **is the answer a category or a quantity?**

- "Will this student pass or fail?" → category → **classification**.
- "What mark will this student get out of 100?" → number → **regression**.

The same situation can be framed either way. A bank can ask "will this loan be repaid — yes or no?" (classification) or "how much of this loan will be repaid?" (regression). The right framing depends on the decision the business must make.

**Binary** classification has two classes (fraud / normal). **Multi-class** has more than two (three cassava diseases plus healthy).

## Supervised, unsupervised — a first look

- If you have **examples with the correct answers** (past transactions marked fraud or normal), the problem is **supervised**.
- If you have data **without answers** and want the computer to find structure (customer groups), it is **unsupervised**.

You will study both in Week 2.

## A quick decision guide

1. Do you need new content? → **Generation**.
2. Do you need to choose actions over time? → **Sequential decision-making**.
3. Is the answer a category? → **Classification**.
4. Is it a number? → **Regression**.
5. No answers available, want natural groups? → **Clustering**.
6. Want to flag rare strange cases? → **Anomaly detection**.
7. Ranking items for a person? → **Recommendation**.

**Takeaway:** Always ask "what output do we need?" first. Category means classification, number means regression, and the other types cover groups, rankings, rare events, new content and actions.

## Try it yourself

Classify each problem and explain your choice in one sentence:

1. Predict tomorrow's maximum temperature in Huye.
2. Decide if an email is spam.
3. Group 10,000 farmers by the crops they grow and their yields.
4. Write a thank-you message for a customer.
5. Find unusual electricity use in a factory.
6. Suggest courses a student might like next.

Then invent one problem of your own from your field and classify it.
""",
            "quiz": [
                ("What is the first question to ask before choosing an AI method?",
                 ["Which laptop to buy", "What kind of output do we need?", "Which programming language is popular", "How many people work on the team"],
                 1, "The needed output decides the problem type, which then decides the data, method and measure."),
                ("Predicting the selling price of a house is…",
                 ["Classification", "Regression", "Clustering", "Generation"],
                 1, "A price is a number, so this is regression."),
                ("Deciding whether a cassava leaf is healthy or has one of two diseases is…",
                 ["Binary classification", "Multi-class classification", "Regression", "Clustering"],
                 1, "There are three possible categories (healthy, disease A, disease B), so it is multi-class classification."),
                ("You have customer data with no labels and want to find natural groups. This is…",
                 ["Clustering", "Regression", "Classification", "Generation"],
                 0, "Finding groups without given answers is clustering, an unsupervised problem."),
                ("Writing a product description automatically is…",
                 ["Anomaly detection", "Generation", "Regression", "Recommendation"],
                 1, "Creating new content such as text or images is generation."),
                ("Which pair is correctly matched?",
                 ["Pass or fail → regression", "Exam mark out of 100 → regression", "Spam or not → clustering", "Customer groups → classification"],
                 1, "A mark out of 100 is a number, so regression. Pass/fail and spam/not are classification; groups without labels are clustering."),
            ],
        },
        # ------------------------------------------------------------------ 5
        {
            "title": "Search and Problem Solving",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=ySN5Wnu88nE",
            "content": """
**Learning objective:** Describe a problem as a search problem, explain how breadth-first, depth-first and A* search work, and say what a heuristic is.

## Many problems are search problems

Finding a route on a map, solving a puzzle, scheduling exams or planning a delivery all share one shape: there is a **start**, a **goal**, and many possible **steps** in between. The computer must search for a good path. This is one of the oldest ideas in AI, and it still powers maps apps and logistics today.

## The parts of a search problem

- **State** — a description of the situation (*the bus is in Muhanga*).
- **Initial state** — where we start (*Kigali*).
- **Actions** — what we can do from a state (*drive to a neighbouring town*).
- **Goal test** — how we know we are done (*are we in Rubavu?*).
- **Path cost** — what a path costs (distance, time, fuel).

All the states and the actions between them form a **state space**, often drawn as a graph: towns are dots, roads are lines.

## Uninformed search: no hints

**Breadth-first search (BFS)** explores all places one step away, then all places two steps away, and so on — like ripples on water.
- Finds the path with the **fewest steps**.
- Uses a lot of memory on big problems.

**Depth-first search (DFS)** follows one road as far as it can, then backs up and tries another.
- Uses little memory.
- May find a long, poor path first, or get lost in very deep spaces.

**Uniform-cost search** always expands the cheapest path so far. It finds the **lowest-cost** path even when steps have different costs (some roads are longer).

## Informed search: using a hint

A **heuristic** is an estimate of how far a state is from the goal. On a map, the straight-line ("as the crow flies") distance to the destination is a good heuristic: it is easy to compute and never more than the real road distance.

**A-star search** (written `A*`) ranks each option by:

> **f = g + h** — cost so far (*g*) plus estimated cost still to go (*h*)

It expands the option with the smallest *f*. If the heuristic never **overestimates** the real remaining cost, A-star is guaranteed to find the cheapest path, and it usually explores far fewer states than uninformed search. Route-planning software uses ideas from A-star every day.

## Worked example

From Kigali you can go to Muhanga (50 km) or Musanze (90 km). You want to reach Rubavu. Straight-line estimates to Rubavu: Muhanga 100 km, Musanze 55 km.

- Muhanga: f = 50 + 100 = 150
- Musanze: f = 90 + 55 = 145

A-star explores Musanze first, because it looks cheaper overall — even though the first step is longer. That is the power of combining real cost with a good estimate.

## Search in games

In two-player games (chess, draughts), the agent must expect the opponent to fight back. **Minimax** search assumes the opponent always picks the move worst for you, and chooses the move with the best guaranteed result. Deep Blue (1997) used this kind of search with very fast hardware.

## Key terms

- **State space** — all possible states and the actions linking them.
- **Heuristic** — a quick estimate of the distance to the goal.
- **Admissible heuristic** — one that never overestimates; makes A-star optimal.
- **Optimal** — finds the best (cheapest) solution.

**Takeaway:** Search turns a problem into states and actions. Uninformed search explores blindly; informed search like A-star uses a heuristic (f = g + h) to reach good answers faster.

## Try it yourself

1. Draw a map with six places you know (home, school, market, church, bus park, hospital) and the walking minutes between them.
2. Run breadth-first search by hand from home to the hospital and write the order you visit places.
3. Invent a heuristic for each place (your best guess of minutes to the hospital). Run A-star and compare the path and the number of places explored.
""",
            "quiz": [
                ("Which is NOT a part of a search problem?",
                 ["Initial state", "Goal test", "Path cost", "Screen brightness"],
                 3, "A search problem has states, an initial state, actions, a goal test and a path cost. Screen brightness is irrelevant."),
                ("Breadth-first search guarantees the path with…",
                 ["The fewest steps", "The most steps", "The highest cost", "Random steps"],
                 0, "BFS explores level by level, so the first time it reaches the goal it has used the fewest steps."),
                ("What is a heuristic?",
                 ["The exact final answer", "A quick estimate of how far a state is from the goal", "A type of computer", "A list of all states"],
                 1, "A heuristic is an estimate, such as straight-line distance on a map."),
                ("In A* search, what does f = g + h mean?",
                 ["Final score = games + hours", "Cost so far plus estimated cost to go", "Goal minus heuristic", "Height plus width"],
                 1, "g is the real cost so far, h is the estimated remaining cost, and A* expands the smallest total."),
                ("When is A* guaranteed to find the cheapest path?",
                 ["When the heuristic never overestimates the real remaining cost", "When the heuristic is always zero only", "When it uses depth-first order", "Never"],
                 0, "An admissible heuristic (one that never overestimates) makes A* optimal."),
                ("Kigali→Muhanga costs 50 with h=100; Kigali→Musanze costs 90 with h=55. Which does A* expand first?",
                 ["Muhanga, because 50 < 90", "Musanze, because 145 < 150", "Both at once", "Neither"],
                 1, "f(Muhanga) = 150 and f(Musanze) = 145, so A* expands Musanze first."),
            ],
        },
        # ------------------------------------------------------------------ 6
        {
            "title": "Week 1 Project: Analyse an AI System",
            "minutes": 60,
            "video": "https://www.youtube.com/watch?v=3AZF1TTDdEM",
            "content": """
**Learning objective:** Bring together everything from Week 1 by analysing one real AI system: where it sits on the AI map, its PEAS description, its environment, its problem type and its history.

## What you will do

This video shows Zipline's drone deliveries in Rwanda — a real AI-powered system working in our hills and weather. Use it as a model, then analyse a system of your own choice. Your analysis should be about **two pages** (or 8–10 slides). It is the kind of short, clear report companies expect from a junior analyst.

## Step 1 — Choose your system

Choose one AI system you can learn about. Ideas:

- Drone delivery (Zipline)
- Mobile-money fraud detection
- A crop-disease app that reads leaf photos
- A Kinyarwanda speech or translation tool
- A chatbot used by a bank, telecom or government service
- A recommendation feed (YouTube, TikTok, Jumia)

## Step 2 — Place it on the AI map

- Is it rule-based AI, machine learning, deep learning — or a mix? Give evidence.
- Is it narrow AI? (It is — but explain what its narrow task is.)

## Step 3 — Write its PEAS table

| | Your system |
|---|---|
| Performance measure | |
| Environment | |
| Actuators | |
| Sensors | |

Then name **one risk** if the performance measure were chosen badly.

## Step 4 — Classify its environment

Fully or partially observable? Deterministic or stochastic? Episodic or sequential? Static or dynamic? Single- or multi-agent? One sentence of reasoning for each.

## Step 5 — Name the problem type(s)

Is it classification, regression, clustering, recommendation, anomaly detection, generation or sequential decision-making? Many systems combine several — a drone system *plans routes* (search, sequential decisions) and may *predict* weather risk (regression or classification).

## Step 6 — History and impact

- Which of the three ingredients (data, computing, methods) made this system possible?
- Who benefits? Who could be harmed or left out?

## Checklist before you submit

- Every section above is answered.
- At least one source is named (website, article or video).
- You used the correct terms: agent, PEAS, environment properties, problem type.
- Simple, clear sentences — a manager should understand it in five minutes.

**Takeaway:** You can now describe any AI system precisely, using the same language professionals use. This skill is the base for everything else in the course.

## Try it yourself

Complete the six steps for your chosen system. If you are studying with friends, swap reports and check each other's PEAS tables and problem types. Keep your report — it becomes the first page of your final project in Week 4.
""",
            "quiz": [
                ("In the Week 1 project, what should the PEAS table describe?",
                 ["The price of the system", "Performance measure, Environment, Actuators and Sensors of the system", "The programmer's CV", "Only the sensors"],
                 1, "PEAS covers all four parts: performance measure, environment, actuators and sensors."),
                ("A drone delivery system plans routes. Which problem type is this mainly?",
                 ["Clustering", "Sequential decision-making / search", "Generation of images", "Recommendation"],
                 1, "Planning a route is a search and sequential decision problem."),
                ("Which ingredient question belongs in the history and impact step?",
                 ["Which data, computing power and methods made the system possible", "Which colour the logo is", "How many employees the company has", "What the CEO eats"],
                 0, "The three ingredients of AI progress explain why the system became possible."),
                ("Why name at least one source in your report?",
                 ["To make the report longer", "So readers can check your facts", "Because it is decoration", "It is not needed"],
                 1, "Sources let others verify your claims — a basic habit of professional analysis."),
                ("A system uses both hard rules and a learned model. How should you place it on the AI map?",
                 ["Only rule-based", "As a mix, with evidence for each part", "Only deep learning", "Not AI"],
                 1, "Many real systems combine rules and learning. Describe both and give evidence."),
                ("What is a good risk to name about the performance measure?",
                 ["Rewarding only speed could make the system unsafe", "The app icon is small", "The website loads slowly", "Users like the colour blue"],
                 0, "A badly chosen performance measure can push an agent towards harmful behaviour."),
            ],
        },
    ],
}
