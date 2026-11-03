"""AI Foundations -- Week 2: How Machines Learn. Original WAMUGII content."""

WEEK2 = {
    "title": "Week 2 · How Machines Learn",
    "lessons": [
        # ------------------------------------------------------------------ 7
        {
            "title": "Data: Features, Labels and Quality",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=0yCJMt9Mx9c",
            "content": """
**Learning objective:** Explain what features and labels are, describe the main types of data, and spot common data-quality problems before they ruin a model.

## Data is the fuel

A machine-learning model can only be as good as the data it learns from. Experienced teams often spend **most of a project's time on data** — finding it, cleaning it and checking it — and much less on the model itself. A popular saying sums it up: **garbage in, garbage out.**

## Rows, features and labels

Most learning data can be pictured as a table. Imagine a cooperative that wants to predict whether a member will repay a small loan:

| Member | Age | Monthly sales (RWF) | Years in cooperative | Past late payments | **Repaid?** |
|---|---|---|---|---|---|
| A | 34 | 180,000 | 5 | 0 | **Yes** |
| B | 27 | 60,000 | 1 | 3 | **No** |
| C | 45 | 250,000 | 9 | 1 | **Yes** |

- Each **row** is one example (one member).
- Each input column is a **feature** — a measurable property used to make the prediction.
- The column we want to predict is the **label** (also called the **target**): *Repaid?*

A model learns how the features relate to the label, then predicts the label for new members.

## Types of data

- **Numerical** — numbers you can do maths with: age, sales, temperature.
- **Categorical** — a choice from a list: district, crop type, phone brand.
- **Text** — messages, reviews, documents.
- **Images, audio and video** — photos of leaves, voice notes, CCTV.
- **Time series** — values in time order: daily rainfall, hourly electricity use.

Tables with clear columns are called **structured** data. Text, images and sound are **unstructured** — richer, but harder to use. Deep learning is especially good with unstructured data.

## Common data-quality problems

| Problem | Example | Why it hurts |
|---|---|---|
| **Missing values** | Sales left empty for 20% of members | The model learns from an incomplete picture |
| **Errors and typos** | Age recorded as 340 | Strange values distort the patterns |
| **Duplicates** | The same member entered twice | Some examples count double |
| **Inconsistent formats** | "Kigali", "kigali", "KGL" | One place looks like three |
| **Wrong labels** | A repaid loan marked "No" | The model learns the wrong lesson |
| **Not representative** | Data only from urban members | The model fails for rural members |
| **Out of date** | Prices from five years ago | The world has changed |

The last two are the most dangerous because they are invisible in a quick look. A dataset can be perfectly clean and still **not represent the people the model will serve**.

## Data leakage — a hidden trap

**Leakage** happens when a feature secretly contains the answer. If a column says "sent to debt collection", it already reveals the loan was not repaid. The model will look brilliant in testing and fail in real life, because that information does not exist at the moment of the real decision.

## Key terms

- **Feature** — an input property used for prediction.
- **Label / target** — the answer the model should predict.
- **Dataset** — the full collection of examples.
- **Data cleaning** — fixing or removing errors, gaps and duplicates.
- **Representative data** — data that matches the people and situations the model will meet.

**Takeaway:** Features are inputs, the label is the answer, and data quality — especially being representative and free of leakage — matters more than any clever model.

## Try it yourself

1. Design a small dataset (10 rows) for a problem in your community: for example, predicting if a student will finish secondary school, or a shop's daily sales.
2. Name at least four features and the label.
3. Write down three data-quality problems your data could have, and how you would fix each.
4. Check for leakage: is any feature only known *after* the answer?
""",
            "quiz": [
                ("In a loan-repayment dataset, what is the label?",
                 ["The member's age", "Whether the loan was repaid", "The member's name", "The table's title"],
                 1, "The label (target) is what we want to predict — here, whether the loan was repaid."),
                ("What is a feature?",
                 ["A measurable input property used to make a prediction", "The final answer", "A bug in the code", "The name of the model"],
                 0, "Features are the input columns, such as age, sales or years in the cooperative."),
                ("Photos, voice notes and documents are examples of…",
                 ["Structured data", "Unstructured data", "Labels", "Duplicates"],
                 1, "Images, sound and free text do not fit neatly into columns, so they are unstructured."),
                ("Data collected only from urban members is used for a national model. What is the main problem?",
                 ["The data is not representative", "There are too many columns", "The data is numerical", "The data is too clean"],
                 0, "The model may fail for rural members because they were missing from the training data."),
                ("A feature 'sent to debt collection' is used to predict repayment. This is an example of…",
                 ["Good feature engineering", "Data leakage", "Clustering", "Missing values"],
                 1, "The feature already reveals the answer and is only known afterwards — classic leakage."),
                ("What does 'garbage in, garbage out' mean?",
                 ["Delete old files often", "A model trained on poor data gives poor results", "Computers produce waste", "Clean data is not needed"],
                 1, "No model can fix bad data. Quality data is the base of good AI."),
            ],
        },
        # ------------------------------------------------------------------ 8
        {
            "title": "The Machine-Learning Workflow",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=nKW8Ndu7Mjw",
            "content": """
**Learning objective:** List the stages of a machine-learning project in order, explain what happens at each stage, and see why the workflow is a loop, not a straight line.

## From idea to working model

Real machine-learning projects follow a repeatable path. Knowing it helps you plan, estimate time and talk clearly with engineers, managers and clients.

## The seven stages

| # | Stage | Key question | Example: predicting maize yield for farmers |
|---|---|---|---|
| 1 | **Define the problem** | What decision will the prediction support, and how do we measure success? | Help a cooperative plan storage; success = error under 10% |
| 2 | **Collect data** | What data exists, who owns it, and may we use it? | Past yields, rainfall, soil type, fertiliser use |
| 3 | **Prepare the data** | Is it clean, complete and representative? | Fix missing rainfall, unify district names |
| 4 | **Choose and train a model** | Which method fits the problem type? | A regression model, because yield is a number |
| 5 | **Evaluate** | How well does it work on data it has never seen? | Test on last season's farms |
| 6 | **Deploy** | How will people actually use it? | A simple SMS or web dashboard for the cooperative |
| 7 | **Monitor and improve** | Is it still accurate as the world changes? | Check each season; retrain with new data |

## Stage 1 is the most important

Many failed projects had good models but a **badly defined problem**. Ask:

- Who will use the prediction, and what will they do differently?
- What does "good enough" mean in numbers?
- What would a simple non-AI solution achieve? (Sometimes a spreadsheet rule is enough.)

## Feature engineering

During preparation, teams often create better features from raw data. From a date you can create *month* and *season*. From total sales and number of days you can create *average daily sales*. Good features can improve a simple model more than switching to a complex one.

## Train, then test on new data

A model must be tested on examples it did **not** learn from — otherwise you only measure memory, not real skill. You will study this deeply in Week 3 (training, validation and test sets).

## Deployment is not the end

The world changes: prices rise, weather patterns shift, customers change habits. A model trained on old data slowly becomes less accurate. This is called **model drift**. That is why stage 7 sends the team back to stages 2–5: the workflow is a **loop**.

## Who does what

- **Domain experts** (farmers, doctors, accountants) — define the problem and judge whether results make sense.
- **Data engineers** — collect, store and move data.
- **Data scientists / ML engineers** — prepare data, train and evaluate models.
- **Software engineers** — build the app or system people use.
- **Product managers** — keep everyone focused on the user's real need.

**Takeaway:** Define → collect → prepare → train → evaluate → deploy → monitor, and then loop back. A clear problem definition and good data matter more than a fancy model.

## Try it yourself

Pick one problem from your community (for example: predicting which patients will miss clinic appointments, or which products a shop will run out of). Write a one-page plan with a short paragraph for each of the seven stages. Mark which stage you think will be hardest, and why.
""",
            "quiz": [
                ("What is the first stage of a machine-learning project?",
                 ["Train the model", "Define the problem and how success is measured", "Deploy the app", "Buy a GPU"],
                 1, "Everything depends on a clear problem definition and a measurable goal."),
                ("Predicting maize yield in tonnes is which problem type?",
                 ["Classification", "Regression", "Clustering", "Generation"],
                 1, "Yield is a number, so regression fits."),
                ("Why must a model be tested on data it did not learn from?",
                 ["To save electricity", "To measure real skill rather than memory", "Because training data is secret", "It does not need testing"],
                 1, "Testing on unseen data shows how the model will behave on new, real cases."),
                ("Creating 'average daily sales' from total sales and days is an example of…",
                 ["Feature engineering", "Model drift", "Deployment", "Data leakage"],
                 0, "Building more useful inputs from raw data is feature engineering."),
                ("What is model drift?",
                 ["When a model moves to a new server", "When a model becomes less accurate because the world has changed", "When training finishes early", "A type of neural network"],
                 1, "As conditions change, old patterns stop fitting, so accuracy slowly falls."),
                ("Why is the ML workflow described as a loop?",
                 ["Because models are trained once and never touched", "Because monitoring leads back to new data, preparation and retraining", "Because the steps are random", "Because deployment comes first"],
                 1, "Monitoring reveals drift or new needs, which sends the team back to earlier stages."),
            ],
        },
        # ------------------------------------------------------------------ 9
        {
            "title": "Supervised Learning",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=W01tIRP_Rqs",
            "content": """
**Learning objective:** Explain how supervised learning works, describe four common supervised methods in plain words, and choose one for a simple problem.

## Learning with a teacher

In **supervised learning**, every training example comes with the **correct answer** (the label). The learning algorithm acts like a student who sees many solved exercises, finds the pattern, and then answers new exercises alone.

The process:

1. Show the model many examples of features **and** labels.
2. The model makes predictions and measures how wrong they are (the **error** or **loss**).
3. It adjusts itself to reduce that error.
4. Repeat until the error stops falling.
5. Use the finished model on new examples that have no label.

Supervised learning handles both **classification** (category answers) and **regression** (number answers).

## Four common methods

**1. Linear regression** — draws the best straight line through the data.
*Example:* house price rises by about a fixed amount per extra square metre. Simple, fast and easy to explain.

**2. Logistic regression** — despite its name, it is used for **classification**. It outputs a probability between 0 and 1, such as "82% chance this transaction is fraud". Widely used in banking and health because it is easy to explain.

**3. Decision tree** — asks a series of yes/no questions, like a flowchart:
*Monthly sales above 100,000 RWF?* → *Late payments fewer than 2?* → *Likely to repay.*
Easy for people to read. A **random forest** combines many trees and is usually more accurate.

**4. k-nearest neighbours (k-NN)** — to classify a new example, look at the *k* most similar past examples and take a vote. "Members who look like you mostly repaid, so you probably will too."

| Method | Problem type | Strength | Weakness |
|---|---|---|---|
| Linear regression | Regression | Simple, explainable | Only straight-line patterns |
| Logistic regression | Classification | Gives probabilities, explainable | Simple patterns only |
| Decision tree / random forest | Both | Readable rules (tree), strong accuracy (forest) | One tree can overfit |
| k-NN | Both | No training step, intuitive | Slow on large data; needs scaled features |

Neural networks (Week 3) are also supervised learners — the most powerful kind for images, sound and language.

## Where the labels come from

Labels are often the expensive part. Someone must mark thousands of leaf photos as *healthy* or *diseased*, or emails as *spam* or *not spam*. This is called **annotation** or **labelling**, and it is real work done by people — including many data workers in Africa. Labels must be **accurate and consistent**, or the model learns mistakes.

## Real supervised systems around you

- Spam filters (classification)
- Credit scoring (classification)
- Crop-disease detection from photos (classification)
- Delivery-time estimates (regression)
- Electricity demand forecasting (regression)

**Takeaway:** Supervised learning learns from examples with correct answers. Choose linear or logistic regression for simple, explainable models; trees and forests for readable or strong models; neural networks for complex data like images and text.

## Try it yourself

1. Draw a small decision tree (3–4 questions) that decides if a customer should get a 10% discount at a shop.
2. Test it on three imaginary customers and write the result for each.
3. Write one sentence on what labelled data you would need to *learn* this tree automatically instead of writing it by hand.
""",
            "quiz": [
                ("What makes learning 'supervised'?",
                 ["A manager watches the computer", "Every training example comes with the correct answer (label)", "No data is used", "The model has no errors"],
                 1, "Supervised learning learns from labelled examples — features plus the correct answer."),
                ("Logistic regression is mainly used for…",
                 ["Classification, giving a probability", "Drawing pictures", "Clustering without labels", "Storing data"],
                 0, "Despite its name, logistic regression outputs a probability for a class, so it is used for classification."),
                ("A model asks 'Sales above 100,000 RWF? Late payments fewer than 2?' and then decides. This is a…",
                 ["Decision tree", "Linear regression", "k-means clustering", "Transformer"],
                 0, "A series of yes/no questions leading to a decision is a decision tree."),
                ("How does k-nearest neighbours classify a new example?",
                 ["It asks a person", "It looks at the most similar past examples and takes a vote", "It draws a straight line", "It deletes outliers"],
                 1, "k-NN finds the k most similar labelled examples and uses their majority answer."),
                ("What is a random forest?",
                 ["A dataset about trees", "Many decision trees combined to give a stronger prediction", "A type of clustering", "A data-cleaning method"],
                 1, "A random forest combines many trees and is usually more accurate than one tree."),
                ("Why is labelling data important work?",
                 ["Wrong or inconsistent labels teach the model mistakes", "Labels make files smaller", "Labels are only for decoration", "Models do not use labels"],
                 0, "A supervised model copies the patterns in its labels — bad labels lead to a bad model."),
            ],
        },
        # ------------------------------------------------------------------ 10
        {
            "title": "Unsupervised Learning",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=4b5d3muPQmA",
            "content": """
**Learning objective:** Explain what unsupervised learning is, describe clustering with k-means, and name two other unsupervised tasks used in business.

## Learning without answers

In **unsupervised learning** the data has **no labels**. Nobody tells the computer the right answer. Instead, it looks for **structure**: groups, patterns and unusual points. It is like walking into a market for the first time and noticing, without being told, that the shops naturally group into vegetables, clothes and electronics.

Unsupervised learning is useful when labels are expensive, unknown, or when you want to *discover* something new.

## Clustering

**Clustering** puts similar examples into groups (clusters). A popular method is **k-means**:

1. Choose *k*, the number of groups you want (say 3).
2. Place 3 starting centre points at random.
3. Assign every example to its nearest centre.
4. Move each centre to the middle (average) of its examples.
5. Repeat steps 3–4 until the groups stop changing.

**Example:** a telecom company clusters customers by calls, data use and mobile-money activity. It may discover:

| Cluster | Pattern | Possible offer |
|---|---|---|
| 1 | Heavy data, few calls (students) | Night data bundles |
| 2 | Many calls, little data (traders) | Cheap call minutes |
| 3 | High mobile-money use (shop owners) | Merchant services |

Nobody labelled these groups — the data revealed them. People then **name and interpret** the clusters; that part still needs human judgement.

## Choosing k

There is no single correct *k*. Teams try several values and check whether the groups are **clearly separated** and **useful for a decision**. Three clusters you can act on are better than ten you cannot explain.

## Other unsupervised tasks

- **Anomaly detection** — learn what "normal" looks like, then flag what is far from normal: a strange login, a machine about to break, an unusual payment.
- **Dimensionality reduction** — squeeze many features into a few while keeping most of the information (a common method is **PCA**, principal component analysis). It helps draw data on a chart and speeds up other models.
- **Association rules** — find items that often appear together: "people who buy bread often buy milk". Shops use this for shelf layout and offers.

## Supervised vs. unsupervised

| | Supervised | Unsupervised |
|---|---|---|
| Labels? | Yes | No |
| Goal | Predict a known answer | Discover structure |
| Typical tasks | Classification, regression | Clustering, anomaly detection, dimensionality reduction |
| How to judge | Compare with true labels | Usefulness and clarity, judged by people |

There is also **semi-supervised learning** (a few labels plus lots of unlabelled data) and **self-supervised learning**, where the data creates its own labels — for example, hiding a word in a sentence and learning to guess it. Self-supervised learning is how large language models are pre-trained (Lesson 17).

**Takeaway:** Unsupervised learning finds structure in unlabelled data — groups, unusual points and simpler summaries. People still decide what the patterns mean.

## Try it yourself

1. Write down 12 foods you ate this month with two features each: price (low/high) and how healthy (low/high).
2. Group them by hand into 3 clusters. Give each cluster a name.
3. Change *k* to 2 and to 4. Which number gives the most useful groups, and why?
""",
            "quiz": [
                ("What is the main difference in unsupervised learning?",
                 ["The data has no labels", "It always uses images", "It needs no computer", "It only predicts prices"],
                 0, "Unsupervised learning works on unlabelled data and looks for structure."),
                ("In k-means, what does k stand for?",
                 ["The number of features", "The number of clusters you want", "The learning speed", "The number of labels"],
                 1, "k is the number of groups (clusters) the algorithm will form."),
                ("After k-means assigns points to centres, what happens next?",
                 ["Each centre moves to the average of its points", "The data is deleted", "Labels are added by hand", "The model is deployed"],
                 0, "Centres move to the middle of their points, then points are reassigned, until nothing changes."),
                ("Flagging an unusual mobile-money payment without labelled fraud examples is…",
                 ["Anomaly detection", "Linear regression", "Translation", "Recommendation"],
                 0, "Learning what is normal and flagging what is far from it is anomaly detection."),
                ("'People who buy bread often buy milk' comes from…",
                 ["Association rules", "Logistic regression", "Search", "Reinforcement learning"],
                 0, "Association rules find items that often appear together."),
                ("Who decides what each discovered cluster means?",
                 ["The algorithm names them perfectly", "People interpret and name the clusters", "Nobody — clusters have no use", "The customers vote"],
                 1, "The algorithm finds groups; humans interpret them and decide what to do."),
            ],
        },
        # ------------------------------------------------------------------ 11
        {
            "title": "Reinforcement Learning",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=T_X4XFwKX8k",
            "content": """
**Learning objective:** Describe how reinforcement learning works using agent, environment, action and reward, explain the explore-exploit trade-off, and say how it helps train chatbots.

## Learning by trial and reward

**Reinforcement learning (RL)** is how an agent learns by **doing**. There are no labelled answers. Instead the agent tries actions, sees what happens, and receives **rewards** (good) or **penalties** (bad). Over many tries it learns which actions lead to the most reward over time.

Think of teaching a dog a new trick, or how you learned to ride a bicycle: nobody gave you a table of correct answers — you tried, fell, adjusted and improved.

## The RL loop

1. The **agent** observes the **state** of the environment.
2. It chooses an **action**.
3. The environment changes to a new state and gives a **reward**.
4. The agent updates its **policy** — its strategy for choosing actions.
5. Repeat, thousands or millions of times.

| Term | Meaning | Example: a robot vacuum |
|---|---|---|
| Agent | The learner | The robot |
| Environment | The world it acts in | The room |
| State | The current situation | Position, battery level, dirt nearby |
| Action | A choice | Move forward, turn, return to charger |
| Reward | Feedback signal | +1 for cleaning dirt, −10 for hitting stairs |
| Policy | The learned strategy | "When battery is low, head to the charger" |

## Long-term thinking

The agent aims for the **highest total reward over time**, not just the next reward. A chess move that loses a piece now may win the game later. RL handles **sequential** problems, where today's action changes tomorrow's options.

## Explore or exploit?

Should the agent use what already works (**exploit**) or try something new that might be better (**explore**)? A shop owner who always stocks the same products never learns that a new product might sell better; one who changes everything every week cannot build on success. Good RL agents balance both — exploring more at the start, exploiting more as they learn.

## Reward design is everything

The agent will chase whatever is rewarded — even in ways nobody intended. If a cleaning robot is rewarded for "dust collected", it might learn to spill dust and collect it again. This is called **reward hacking**, and it connects to the PEAS lesson: **what you measure is what you get.**

## Where RL is used

- **Games** — AlphaGo learned partly by playing millions of games against itself.
- **Robotics** — learning to walk, grasp or balance.
- **Resource control** — managing energy use in data centres, traffic signals.
- **Chatbots** — **reinforcement learning from human feedback (RLHF)**: people rank several model answers from best to worst, a reward model learns those preferences, and the chatbot is tuned to give answers people prefer. This is one reason modern assistants are more helpful and polite than raw language models.

## The three types of machine learning

| | Supervised | Unsupervised | Reinforcement |
|---|---|---|---|
| Learns from | Labelled examples | Unlabelled data | Rewards from actions |
| Question | "What is the answer?" | "What structure is here?" | "What should I do next?" |

**Takeaway:** Reinforcement learning learns by trial, error and reward. It suits sequential decisions, depends on careful reward design, and helps make chatbots more useful through RLHF.

## Try it yourself

1. Design an RL setup for a traffic light at a busy Kigali junction: write the state, actions and reward.
2. Describe one way the agent could "hack" your reward, and fix the reward to prevent it.
3. Give one example from your own life of exploring versus exploiting.
""",
            "quiz": [
                ("How does a reinforcement-learning agent learn?",
                 ["From a table of correct answers", "By trying actions and receiving rewards or penalties", "By clustering data", "By copying a website"],
                 1, "RL learns from the consequences of its actions — rewards and penalties — over many tries."),
                ("What is a 'policy' in RL?",
                 ["A government law", "The agent's learned strategy for choosing actions", "The reward value", "The training data"],
                 1, "The policy maps situations (states) to actions; learning improves it."),
                ("Why might an agent sacrifice a small reward now?",
                 ["It is broken", "It aims for the highest total reward over time", "Rewards do not matter", "To save electricity"],
                 1, "RL agents maximise long-term total reward, so a short-term loss can be worth it."),
                ("What is the explore-exploit trade-off?",
                 ["Choosing between trying new actions and using actions known to work", "Choosing between two computers", "Choosing between labels", "Choosing a programming language"],
                 0, "The agent must balance discovering better options with using what already works."),
                ("A cleaning robot spills dust so it can collect it again for more reward. This is…",
                 ["Reward hacking", "Clustering", "Data cleaning", "Good design"],
                 0, "The agent found an unintended way to earn reward — a sign the reward was badly designed."),
                ("In RLHF, what do people provide?",
                 ["Labels for every word", "Rankings of model answers, which teach a reward model their preferences", "Electricity", "New computer chips"],
                 1, "Humans rank answers; a reward model learns from the rankings and guides the chatbot's training."),
            ],
        },
        # ------------------------------------------------------------------ 12
        {
            "title": "Week 2 Project: Plan a Machine-Learning Project",
            "minutes": 60,
            "video": "https://www.youtube.com/watch?v=R9OHn5ZF4Uo",
            "content": """
**Learning objective:** Write a complete, realistic plan for a machine-learning project, using the workflow, data and learning-type ideas from Week 2.

## What you will do

Re-watch this short video on how machines learn, then write a **project plan** of 2–3 pages for one machine-learning idea that could help people in Rwanda or your own community. You will not write code. You will think like the person who leads the project — the most valuable skill in real AI teams.

## Step 1 — The problem

- Who has the problem? What decision do they make today, and how?
- What will the model predict or find?
- **Success measure:** write it as a number (for example, "find 80% of fraud cases while wrongly flagging fewer than 5% of normal ones").
- Could a simple rule solve it without AI? Explain why ML is (or is not) needed.

## Step 2 — Learning type and problem type

- Supervised, unsupervised or reinforcement learning? Why?
- Classification, regression, clustering, anomaly detection…? Why?

## Step 3 — The data

Make a table of the features and label:

| Feature / label | Type (number, category, text, image…) | Where it comes from | Possible quality problem |
|---|---|---|---|
| | | | |

Then answer:
- Is the data **representative** of everyone the model will serve?
- Is there any risk of **leakage**?
- Do you have **permission** to use this data? Does it contain personal information?

## Step 4 — Method

Name one simple **baseline** method (for example logistic regression or a decision tree) and one stronger method you might try later (for example a random forest or a neural network). Explain the trade-off between them.

## Step 5 — Deployment and monitoring

- How will the user actually receive the result (SMS, app, dashboard, report)?
- What could cause **drift** in your problem?
- How often will you check and retrain?

## Step 6 — Risks

Name two things that could go wrong (wrong predictions, unfair results for one group, privacy problems) and how you would reduce each one.

## Example ideas

- Predict which Grade 6 pupils may drop out, so schools can support them early.
- Detect unusual electricity use that may mean a faulty meter.
- Group small shops by sales patterns to design better supplier credit.
- Predict demand for buses on each route by hour.

## Checklist

- Every step is answered in clear, simple sentences.
- The success measure is a number.
- The data table has at least four features.
- Risks are honest and specific.

**Takeaway:** A strong plan names the decision, a numeric success measure, the right learning type, representative data with permission, a simple baseline first, and a plan for drift and risk.

## Try it yourself

Complete the six steps for your idea. Share it with a classmate, a teacher or a professional in that field and ask: *"Would this help you? What did I miss?"* Write down their feedback and one change you made. Keep this plan — it feeds into your final project.
""",
            "quiz": [
                ("How should the success measure in your plan be written?",
                 ["As a feeling, like 'works well'", "As a number, such as 'find 80% of fraud cases'", "As the model's name", "It is not needed"],
                 1, "A numeric success measure lets everyone agree on whether the project worked."),
                ("Why start with a simple baseline method?",
                 ["Simple methods are always the most accurate", "It gives a reference point to judge whether a complex method is worth it", "Because complex methods are illegal", "To avoid collecting data"],
                 1, "A baseline shows what easy methods achieve; a complex model must beat it to be worth the extra cost."),
                ("Which question checks if your data is representative?",
                 ["Does the data include everyone the model will serve?", "Is the file name short?", "Is the data in English?", "Is the computer fast?"],
                 0, "Representative data covers the people and situations the model will meet in real use."),
                ("Predicting which pupils may drop out using past records with known outcomes is…",
                 ["Supervised classification", "Unsupervised clustering", "Reinforcement learning", "Generation"],
                 0, "Past records with known outcomes are labelled data, and drop out / stay is a category."),
                ("Why ask 'could a simple rule solve this without AI?'",
                 ["Because ML is always wrong", "Because ML costs time and money and is only worth it when rules are not enough", "Because rules are illegal", "To make the plan shorter"],
                 1, "Good practitioners use ML only when it adds real value over simpler solutions."),
                ("Which belongs in the deployment step?",
                 ["How the user will receive the result and how drift will be checked", "The colour of the model", "The founder's biography", "The number of slides"],
                 0, "Deployment covers how people use the model; monitoring plans for drift and retraining."),
            ],
        },
    ],
}
