"""AI Foundations -- Week 3: Measuring and Building Models. Original WAMUGII content."""

WEEK3 = {
    "title": "Week 3 · Measuring and Building Models",
    "lessons": [
        # ------------------------------------------------------------------ 13
        {
            "title": "Training, Testing and Overfitting",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=EuBBz3bI-aA",
            "content": """
**Learning objective:** Explain why data is split into training, validation and test sets, recognise overfitting and underfitting, and name ways to prevent overfitting.

## Memorising is not learning

Imagine a student who memorises the answers to last year's exam word for word. On last year's paper they score 100%. On this year's paper, with new questions, they fail. They memorised — they did not learn.

Models can do the same thing. A model that is perfect on its training data may be useless on new data. To know the truth, we must test it on examples it has **never seen**.

## Three sets of data

| Set | Typical share | Used for |
|---|---|---|
| **Training set** | about 70% | The model learns its patterns here |
| **Validation set** | about 15% | Compare models and tune settings during development |
| **Test set** | about 15% | One final, honest check at the very end |

The test set is like the sealed national exam paper: you open it **once**. If you keep checking it and changing the model, you slowly "teach to the test", and the score stops being honest.

**Cross-validation** is a way to use small datasets well: split the data into, say, 5 parts, train on 4 and validate on 1, rotate five times, and average the results.

## Overfitting and underfitting

| | Underfitting | Good fit | Overfitting |
|---|---|---|---|
| What happens | The model is too simple to capture the pattern | Captures the real pattern | Learns the noise and accidents in the training data |
| Training score | Poor | Good | Excellent |
| New-data score | Poor | Good | Poor |
| Exam analogy | Did not study | Understood the topic | Memorised last year's answers |

The tell-tale sign of **overfitting** is a big gap: very high training score, much lower validation score.

## Why overfitting happens

- The model is **too complex** for the amount of data (a very deep decision tree on 200 rows).
- **Too little data**, so random accidents look like patterns.
- **Training too long**, so the model starts memorising.
- **Noisy labels** that the model tries to copy exactly.

## How to prevent it

- **Get more (good) data** — the most reliable fix.
- **Use a simpler model**, or limit its complexity (for example, limit tree depth).
- **Regularisation** — add a penalty for complexity, so the model prefers simpler patterns.
- **Early stopping** — stop training when the validation score stops improving.
- **Dropout** (in neural networks) — randomly switch off some neurons during training so the network cannot rely on any single path.

## The bias–variance idea

- **High bias** = the model's assumptions are too simple → underfitting.
- **High variance** = the model changes a lot with small changes in the data → overfitting.

Good models balance the two. (This "bias" is a statistics word; it is different from unfair bias, which you study in Week 4.)

**Takeaway:** Always judge a model on data it has not seen. A large gap between training and validation scores means overfitting; more data, simpler models, regularisation and early stopping help.

## Try it yourself

A team reports these results. For each, say *underfitting*, *good fit* or *overfitting*, and suggest one action:

1. Training accuracy 99%, validation 71%.
2. Training accuracy 62%, validation 60%.
3. Training accuracy 88%, validation 86%.

Then explain in two sentences why the test set must be used only once.
""",
            "quiz": [
                ("Why do we keep a separate test set?",
                 ["To make training faster", "To get one honest final check on data the model has never seen", "Because training data is too small", "To store backups"],
                 1, "The test set gives an unbiased estimate of real-world performance, so it is used once at the end."),
                ("Training accuracy 99%, validation accuracy 71%. What is the likely problem?",
                 ["Underfitting", "Overfitting", "A perfect model", "Data cleaning"],
                 1, "A big gap between training and validation scores is the classic sign of overfitting."),
                ("Training 62%, validation 60%. What is the likely problem?",
                 ["Underfitting — the model is too simple", "Overfitting", "Leakage", "Nothing, it is perfect"],
                 0, "Both scores are low and close together, so the model has not captured the pattern."),
                ("Which is a way to reduce overfitting?",
                 ["Train for much longer", "Use a more complex model on less data", "Get more good data or use regularisation", "Test on the training set"],
                 2, "More data, simpler models, regularisation and early stopping all fight overfitting."),
                ("What is early stopping?",
                 ["Stopping training when the validation score stops improving", "Stopping the project early", "Deleting the test set", "Turning off the computer"],
                 0, "Training stops before the model starts memorising noise."),
                ("What is the purpose of the validation set?",
                 ["Final exam only", "Comparing models and tuning settings during development", "Storing labels", "Training the model"],
                 1, "The validation set guides choices during development, protecting the test set for the final check."),
            ],
        },
        # ------------------------------------------------------------------ 14
        {
            "title": "Measuring Performance: Accuracy, Precision and Recall",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=Kdsp6soqA7o",
            "content": """
**Learning objective:** Read a confusion matrix, calculate accuracy, precision and recall, and choose the right measure for a real problem.

## Why accuracy is not enough

A mobile-money company has 1,000 transactions; **50 are fraud**. A lazy model that says "not fraud" every time is correct on 950 of them: **95% accuracy** — and it catches **zero** fraud. When one class is rare, accuracy can hide total failure. We need better measures.

## The confusion matrix

A better model flags 60 transactions as fraud. Comparing with the truth:

| | **Really fraud** | **Really normal** |
|---|---|---|
| **Predicted fraud** | True positives (TP) = **40** | False positives (FP) = **20** |
| **Predicted normal** | False negatives (FN) = **10** | True negatives (TN) = **930** |

- **True positive** — fraud correctly caught.
- **False positive** — a normal transaction wrongly flagged (an annoyed customer).
- **False negative** — fraud that slipped through (lost money).
- **True negative** — normal transaction correctly left alone.

## The key measures

| Measure | Formula | Our model | Plain question |
|---|---|---|---|
| **Accuracy** | (TP + TN) ÷ total | (40 + 930) ÷ 1000 = **97%** | How often is it right overall? |
| **Precision** | TP ÷ (TP + FP) | 40 ÷ 60 = **67%** | When it says "fraud", how often is it really fraud? |
| **Recall** | TP ÷ (TP + FN) | 40 ÷ 50 = **80%** | Of all real fraud, how much did it catch? |
| **F1 score** | 2 × P × R ÷ (P + R) | 2 × 0.67 × 0.80 ÷ 1.47 ≈ **0.73** | One number balancing precision and recall |

## Precision or recall — which matters more?

It depends on which mistake is **more costly**:

- **Recall first** when missing a case is dangerous: detecting disease, fraud, or a child at risk of dropping out. Better to check a few extra cases than miss real ones.
- **Precision first** when false alarms are costly: blocking a customer's account, sending a spam warning on an important email, accusing someone.

There is usually a **trade-off**. Flag more cases and recall rises but precision falls; flag fewer and the opposite happens. Many models give a **probability**, and the team chooses a **threshold** (for example, flag if above 0.7) to set the balance.

## Measuring regression

For number predictions, we measure how far off the predictions are:

- **MAE (mean absolute error)** — the average size of the error. "Our yield forecast is off by 0.3 tonnes on average."
- **RMSE (root mean squared error)** — like MAE but punishes big errors more.

## Always compare with a baseline

A score means little alone. Compare with: the lazy model (always predict the most common answer), a simple rule, or the current human process. "97% accuracy" is weak if the lazy model gets 95%.

**Takeaway:** Use the confusion matrix. Accuracy can mislead on rare events; recall measures how much you catch, precision how trustworthy your alarms are. Choose based on which mistake costs more.

## Try it yourself

A malaria test model checks 200 patients; 20 really have malaria. It flags 30 patients, of whom 18 really have malaria.

1. Fill in TP, FP, FN and TN.
2. Calculate accuracy, precision and recall.
3. Which measure matters most here, and why?

(Answers to check yourself: TP 18, FP 12, FN 2, TN 168; accuracy 93%, precision 60%, recall 90%.)
""",
            "quiz": [
                ("Why can accuracy be misleading for fraud detection?",
                 ["Fraud is rare, so always predicting 'not fraud' gives high accuracy while catching nothing", "Accuracy cannot be calculated", "Fraud is always common", "Accuracy is only for images"],
                 0, "With rare classes, a useless model can still score high accuracy."),
                ("What is a false negative in fraud detection?",
                 ["A normal transaction flagged as fraud", "Fraud that the model missed", "Fraud that was caught", "A normal transaction left alone"],
                 1, "A false negative is a real positive (fraud) that the model predicted as negative."),
                ("Precision answers which question?",
                 ["Of all real fraud, how much was caught?", "When the model says fraud, how often is it right?", "How fast is the model?", "How many features are there?"],
                 1, "Precision = TP ÷ (TP + FP): how trustworthy the positive predictions are."),
                ("A model has TP = 40 and FN = 10. What is its recall?",
                 ["40%", "67%", "80%", "97%"],
                 2, "Recall = TP ÷ (TP + FN) = 40 ÷ 50 = 80%."),
                ("For detecting a serious disease, which measure usually matters most?",
                 ["Recall, because missing a sick patient is dangerous", "Precision only", "Training speed", "File size"],
                 0, "Missing real cases (false negatives) is the costly mistake, so recall comes first."),
                ("What does MAE measure?",
                 ["The average size of the error in number predictions", "The number of clusters", "The accuracy of a classifier", "The model's memory"],
                 0, "Mean absolute error is the average distance between predictions and true values in regression."),
            ],
        },
        # ------------------------------------------------------------------ 15
        {
            "title": "Neural Networks Explained",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=aircAruvnKk",
            "content": """
**Learning objective:** Describe the parts of a neural network — neurons, weights, biases, layers and activation functions — and explain why depth helps with images, sound and language.

## Inspired by the brain, built with maths

A **neural network** is a model made of many small calculating units called **neurons**, connected in **layers**. It was loosely inspired by brain cells, but it is really a large mathematical function. Neural networks are the engine of **deep learning**.

## One neuron

A single artificial neuron does three things:

1. Takes some inputs (numbers).
2. Multiplies each input by a **weight** (how important that input is), adds them up, and adds a **bias** (a starting offset).
3. Passes the total through an **activation function**, which decides how strongly the neuron "fires".

**Example:** a neuron deciding "should I carry an umbrella?"
- Inputs: cloudiness = 0.9, rain forecast = 0.8, already raining = 0
- Weights: 0.5, 0.8, 1.0; bias: −0.6
- Total = 0.9×0.5 + 0.8×0.8 + 0×1.0 − 0.6 = 0.45 + 0.64 − 0.6 = **0.49**
- A positive result → the neuron fires → "take the umbrella".

Learning means finding good values for all the weights and biases.

## Layers

| Layer | Job | Example: reading a handwritten digit |
|---|---|---|
| **Input layer** | Receives the raw data | 784 numbers — one per pixel of a 28×28 image |
| **Hidden layers** | Build up patterns step by step | First edges, then curves and loops, then digit shapes |
| **Output layer** | Gives the answer | 10 neurons, one for each digit 0–9; the highest wins |

A network with **many hidden layers** is a **deep** network — that is where "deep learning" gets its name.

## Why depth helps

Each layer builds on the one before. In image recognition, early layers detect simple **edges**, middle layers combine edges into **shapes** (eyes, wheels, leaf spots), and later layers recognise **whole objects**. This step-by-step building is why deep networks work so well on images, sound and language, where hand-written rules fail.

## Activation functions

Without activation functions, stacking layers would still give only a straight-line model. Activations add the **curves** that let networks learn complex patterns.

- **ReLU** — keeps positive numbers, turns negatives into zero. Simple and very common.
- **Sigmoid** — squeezes any number into 0 to 1; useful for probabilities.
- **Softmax** — turns the output layer into probabilities that add up to 100% (for example, 92% "digit 7").

## Special network designs

- **Convolutional neural networks (CNNs)** — designed for images; they scan small patches to find patterns anywhere in the picture. Used in crop-disease apps and medical scans.
- **Recurrent neural networks (RNNs)** — process sequences step by step; used for speech and text before transformers.
- **Transformers** — the modern design for language and more (Lesson 17).

## The cost of power

Deep networks can have **millions or billions** of weights. They need lots of data, powerful GPUs and energy to train, and they are hard to explain — a challenge you will study in Week 4.

**Takeaway:** A neural network is layers of neurons; each neuron weighs its inputs, adds a bias and applies an activation. Many layers let the network build simple patterns into complex ones.

## Try it yourself

1. Redo the umbrella neuron with your own weights for a sunny day (cloudiness 0.2, rain forecast 0.1, already raining 0). Does it fire?
2. Change one weight so the neuron becomes more "careful" (fires more easily). Explain your change.
3. Describe in three sentences what the early, middle and late layers might detect in a network that recognises cassava diseases from leaf photos.
""",
            "quiz": [
                ("What does a single artificial neuron do?",
                 ["Stores files", "Weighs its inputs, adds a bias and applies an activation function", "Draws pictures", "Connects to Wi-Fi"],
                 1, "A neuron computes a weighted sum plus bias, then passes it through an activation."),
                ("What is a weight in a neural network?",
                 ["How heavy the computer is", "A number showing how important an input is", "The number of layers", "The output label"],
                 1, "Weights scale each input; learning means finding good weights."),
                ("What makes a network 'deep'?",
                 ["It is stored underground", "It has many hidden layers", "It uses only one neuron", "It has no activation function"],
                 1, "Deep learning uses networks with many hidden layers."),
                ("In image recognition, what do early layers usually detect?",
                 ["Whole objects", "Simple edges", "Names of people", "Sounds"],
                 1, "Early layers pick up simple features like edges; later layers combine them into shapes and objects."),
                ("Why are activation functions needed?",
                 ["To make the network colourful", "Without them, stacked layers would only learn straight-line patterns", "To delete data", "They are not needed"],
                 1, "Activations add non-linearity, letting networks learn complex patterns."),
                ("Which network design is built especially for images?",
                 ["Convolutional neural network (CNN)", "Decision tree", "k-means", "Linear regression"],
                 0, "CNNs scan small patches of an image to find patterns anywhere in it."),
            ],
        },
        # ------------------------------------------------------------------ 16
        {
            "title": "How Neural Networks Learn",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=IHZwWFHWa-w",
            "content": """
**Learning objective:** Explain how a neural network learns using a loss function, gradient descent and backpropagation, and describe the role of the learning rate and epochs.

## Learning = reducing mistakes

A new network starts with **random** weights, so its first predictions are nonsense. Training is the process of adjusting millions of weights, little by little, so the predictions become less wrong. Four ideas make this work.

## 1. The loss function — measuring the mistake

The **loss** is a single number that says how wrong the network is on a set of examples. Small loss = good predictions; big loss = bad ones.

- For regression, a common loss is the **mean squared error** (average of the squared differences).
- For classification, a common loss is **cross-entropy**, which punishes confident wrong answers heavily.

The goal of training is simple to say: **make the loss as small as possible.**

## 2. Gradient descent — walking downhill

Imagine you are on a hill near Nyungwe in thick fog, and you want to reach the valley. You cannot see far, but you can feel which way the ground slopes under your feet. So you take a step downhill, feel again, take another step, and repeat.

That is **gradient descent**:
- The "hill" is the loss.
- The **gradient** tells us which direction makes the loss rise fastest — so we step the **opposite** way.
- Each step changes every weight a little to reduce the loss.

## 3. The learning rate — step size

The **learning rate** decides how big each step is.

| Learning rate | What happens |
|---|---|
| Too small | Progress is very slow; training takes forever |
| Too large | You jump over the valley and bounce around, or even climb up |
| Just right | Steady progress down to a low loss |

Choosing it well is one of the most important settings (**hyperparameters**) in deep learning.

## 4. Backpropagation — sharing the blame

A network has many layers. When the output is wrong, which weights are to blame? **Backpropagation** answers this. It works **backwards** from the output layer to the first layer, calculating how much each weight contributed to the error. Then gradient descent adjusts each weight by its share of the blame.

Backpropagation became popular in the 1980s and is still how almost every neural network is trained today.

## The training loop

1. Take a small group of examples (a **batch**).
2. **Forward pass:** the network makes predictions.
3. Calculate the **loss**.
4. **Backward pass:** backpropagation computes the gradients.
5. **Update:** gradient descent changes the weights a little.
6. Repeat for all batches. One full pass through the training data is an **epoch**. Training often takes many epochs.

Watch the **validation loss** while training. If training loss keeps falling but validation loss starts rising, the network is overfitting — time for early stopping (Lesson 13).

## Key terms

- **Loss** — a number measuring how wrong the predictions are.
- **Gradient** — the direction and steepness of the loss for each weight.
- **Learning rate** — the size of each update step.
- **Batch** — a small group of examples used for one update.
- **Epoch** — one full pass through the training data.
- **Hyperparameter** — a setting chosen by people, not learned (learning rate, number of layers, epochs).

**Takeaway:** Networks learn by measuring their mistakes (loss), finding which way reduces them (gradients via backpropagation), and stepping that way (gradient descent) — many small steps over many epochs.

## Try it yourself

1. Explain gradient descent to a friend using a real place you know (a hill, a valley, a staircase) in no more than five sentences.
2. A team's training loss falls quickly, then jumps up and down wildly. What setting would you change first, and how?
3. A dataset has 10,000 examples and the batch size is 100. How many updates happen in one epoch? (Answer: 100.)
""",
            "quiz": [
                ("What does the loss function measure?",
                 ["How fast the computer is", "How wrong the network's predictions are", "The number of layers", "The size of the dataset"],
                 1, "Loss is a single number showing how far predictions are from the truth."),
                ("In gradient descent, which way do we step?",
                 ["In the direction that increases the loss", "Opposite to the gradient, so the loss goes down", "Randomly", "We do not move"],
                 1, "The gradient points uphill; we step the opposite way to reduce the loss."),
                ("What happens if the learning rate is far too large?",
                 ["Training becomes very slow but steady", "The updates overshoot and the loss bounces around or grows", "Nothing changes", "The model becomes smaller"],
                 1, "Huge steps jump over the minimum, so training becomes unstable."),
                ("What does backpropagation do?",
                 ["Deletes bad data", "Works backwards to calculate how much each weight contributed to the error", "Collects new data", "Deploys the model"],
                 1, "Backpropagation computes each weight's share of the error so it can be updated."),
                ("What is an epoch?",
                 ["One full pass through the training data", "One neuron", "One prediction", "One test set"],
                 0, "An epoch means the network has seen every training example once."),
                ("Training loss falls but validation loss starts rising. What is happening?",
                 ["Underfitting", "Overfitting — consider early stopping", "Perfect learning", "Data leakage is impossible"],
                 1, "The network is memorising the training data; stop or regularise."),
            ],
        },
        # ------------------------------------------------------------------ 17
        {
            "title": "Transformers and Large Language Models",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=wjZofJX0v4M",
            "content": """
**Learning objective:** Explain how large language models work — tokens, embeddings, attention and next-token prediction — and describe how they are trained in stages.

## A machine that predicts the next word

A **large language model (LLM)** — the engine behind ChatGPT, Gemini and Claude — does one basic job: given some text, it **predicts the next piece of text**. Repeat that prediction again and again, and it writes sentences, emails, code and essays.

This sounds simple, but to predict well across billions of examples, the model must learn grammar, facts, styles of writing and patterns of reasoning.

## Step 1: tokens

Text is first cut into **tokens** — whole words, parts of words, or punctuation. "Murakoze cyane" may become several tokens. Each token gets a number ID. Languages with less training data, including Kinyarwanda, are often cut into more, smaller tokens, which can make models slower and less accurate for them.

## Step 2: embeddings

Each token is turned into an **embedding**: a long list of numbers that captures its meaning. Words with similar meanings end up with similar numbers. "Teacher" and "lecturer" sit close together; "teacher" and "banana" sit far apart.

## Step 3: attention — the key idea

The word "bank" means different things in "the bank gave me a loan" and "we sat on the river bank". To understand a word, you must look at the **other words around it**.

**Attention** lets every token look at every other token in the text and decide which ones matter most for its meaning. In "The farmer sold the cow because **it** was old", attention helps the model link "it" to "cow".

The **transformer** (introduced in 2017) is built from many layers of attention plus small neural networks. Because attention looks at all tokens at once instead of one by one, transformers train efficiently on GPUs — which is why they could be scaled up to huge sizes.

## Step 4: predict, pick, repeat

At the end, the model gives a probability for every possible next token. One is chosen (a setting called **temperature** controls how adventurous the choice is), added to the text, and the process repeats.

## How an LLM is trained

| Stage | What happens | Result |
|---|---|---|
| **1. Pre-training** | Predict the next token on a huge amount of text from books, websites and code (self-supervised) | A model that knows language and many facts, but is not yet a helpful assistant |
| **2. Fine-tuning** | Train on examples of good questions and answers written by people | Follows instructions |
| **3. RLHF / preference tuning** | People rank answers; the model is tuned towards preferred ones (Lesson 11) | More helpful, polite and safer |

## Important limits

- **Hallucinations** — the model predicts *likely* text, not checked truth, so it can state false things confidently.
- **Knowledge cutoff** — it only knows what was in its training data, unless connected to search or documents.
- **Context window** — it can only read a limited amount of text at once.
- **Bias** — it can repeat unfair patterns from its training text.
- **Weaker in low-resource languages** — less training data means lower quality.

## Beyond text

The same transformer ideas now power image generators, speech recognition, translation and **multimodal** models that handle text, images and audio together.

**Takeaway:** An LLM turns text into tokens and embeddings, uses attention to understand context, and predicts the next token again and again. It is pre-trained on huge text, then fine-tuned and tuned with human feedback — and it can still be confidently wrong.

## Try it yourself

1. Ask an AI assistant the same question three times. Note how the answers differ, and explain why using the idea of next-token probabilities.
2. Ask it a question in Kinyarwanda and the same question in English. Compare the quality and write two sentences on what you notice.
3. Write the sentence "The student gave the book to the teacher because she needed it." Who is "she"? Explain how attention helps a model decide.
""",
            "quiz": [
                ("What basic job does a large language model do?",
                 ["Searches a database of answers", "Predicts the next piece of text, again and again", "Copies Wikipedia exactly", "Translates only"],
                 1, "LLMs generate text by repeatedly predicting the next token."),
                ("What is a token?",
                 ["A payment coin", "A piece of text such as a word or part of a word", "A type of GPU", "A user account"],
                 1, "Text is split into tokens — words, sub-words or punctuation — before processing."),
                ("What does attention allow a model to do?",
                 ["Look at other words in the text to understand each word's meaning", "Pay for electricity", "Store more files", "Work without data"],
                 0, "Attention lets each token weigh the importance of other tokens, capturing context."),
                ("What happens during pre-training?",
                 ["People rank answers", "The model learns to predict the next token on a huge amount of text", "The model is deployed to phones", "The model is deleted"],
                 1, "Pre-training is self-supervised next-token prediction on large text collections."),
                ("Why can an LLM hallucinate?",
                 ["It predicts likely text rather than checking facts", "It is connected to the internet", "It has too few tokens", "It never makes mistakes"],
                 0, "The model produces fluent, likely text that may not be true, so important facts must be checked."),
                ("Why might an LLM perform worse in Kinyarwanda than in English?",
                 ["Kinyarwanda has no grammar", "There is much less Kinyarwanda training data, and words are split into more tokens", "LLMs cannot read African languages at all", "Kinyarwanda uses numbers"],
                 1, "Low-resource languages have less training text, which lowers quality and efficiency."),
            ],
        },
        # ------------------------------------------------------------------ 18
        {
            "title": "Week 3 Project: Evaluate a Model",
            "minutes": 60,
            "video": "https://www.youtube.com/watch?v=LPZh9BOjkQs",
            "content": """
**Learning objective:** Evaluate a model's results like a professional: read the numbers, spot overfitting, pick the right measure for the decision, and write a clear recommendation.

## About this project

You are a junior analyst at a health organisation in Rwanda. Two teams built models to predict which pregnant women are at **high risk** and should get extra clinic visits. Your manager asks: *"Which model should we use, and is it ready?"* Write a 1–2 page evaluation report.

## The results

Both models were tested on the same **test set of 1,000 women**, of whom **100 are truly high-risk**.

**Model A** (a large neural network)

| | Truly high-risk | Truly low-risk |
|---|---|---|
| Predicted high-risk | 70 | 30 |
| Predicted low-risk | 30 | 870 |

Training accuracy: 99%. Validation accuracy: 91%.

**Model B** (a random forest)

| | Truly high-risk | Truly low-risk |
|---|---|---|
| Predicted high-risk | 88 | 112 |
| Predicted low-risk | 12 | 788 |

Training accuracy: 89%. Validation accuracy: 87%.

## Step 1 — Calculate

For each model, calculate **accuracy, precision and recall**. Show your working.

## Step 2 — Check for overfitting

Compare training and validation accuracy for each model. Which shows signs of overfitting? What would you suggest to the team?

## Step 3 — Choose the measure that matters

- What does a **false negative** mean here? (A high-risk woman not given extra care.)
- What does a **false positive** mean? (A low-risk woman given extra visits.)
- Which mistake is more costly? So which measure matters most?

## Step 4 — Recommend

Write a short recommendation (one paragraph): which model, why, and what must happen before it is used with real patients (for example, testing in more districts, checking fairness across rural and urban clinics, and a doctor always making the final decision).

## Step 5 — One-slide summary

Make one slide or half-page summary a busy manager could read in one minute: the choice, three key numbers, and one risk.

## Check your numbers

- Model A: accuracy 94%, precision 70%, recall 70%.
- Model B: accuracy 87.6%, precision 44%, recall 88%.

Model A has higher accuracy, but Model B catches far more high-risk women. In health screening, missing a high-risk woman is usually the more serious mistake — but Model B also sends many low-risk women for extra visits. Your report should weigh this trade-off honestly.

**Takeaway:** Good evaluation is not "pick the highest accuracy". It means computing the right measures, checking for overfitting, linking errors to real costs and recommending clear next steps.

## Try it yourself

Complete all five steps and write your report. Then add one paragraph: *"If clinics can only handle 150 extra-visit referrals per 1,000 women, how does this change your recommendation?"*
""",
            "quiz": [
                ("Model A has TP = 70 and FN = 30. What is its recall?",
                 ["30%", "70%", "88%", "94%"],
                 1, "Recall = TP ÷ (TP + FN) = 70 ÷ 100 = 70%."),
                ("Model B has TP = 88 and FP = 112. What is its precision?",
                 ["44%", "70%", "88%", "12%"],
                 0, "Precision = 88 ÷ (88 + 112) = 88 ÷ 200 = 44%."),
                ("Model A: training 99%, validation 91%. Model B: training 89%, validation 87%. Which shows more overfitting?",
                 ["Model A, because its gap is larger", "Model B", "Neither", "Both equally"],
                 0, "Model A's 8-point gap between training and validation is larger, a sign of overfitting."),
                ("In this health screening, what is a false negative?",
                 ["A low-risk woman sent for extra visits", "A high-risk woman not given extra care", "A correct prediction", "A missing file"],
                 1, "A false negative misses a true high-risk case — usually the more serious mistake here."),
                ("Why is the highest accuracy not automatically the best choice?",
                 ["Accuracy ignores which kind of mistake is more costly", "Accuracy is always wrong", "Accuracy cannot be compared", "Managers dislike accuracy"],
                 0, "The right model depends on the cost of each type of error, not only on overall accuracy."),
                ("What should happen before using the model with real patients?",
                 ["Nothing, deploy immediately", "Wider testing, fairness checks and a doctor making the final decision", "Delete the test set", "Remove all doctors"],
                 1, "Responsible use needs more testing, fairness checks and human oversight."),
            ],
        },
    ],
}
