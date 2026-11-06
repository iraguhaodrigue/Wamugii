"""Modern AI: LLMs & Generative AI -- Week 2: Building with LLM APIs. Original WAMUGII content."""

# Shared setup cell: install the SDK, read the key safely, define a helper.
SETUP = r"""
```python
import importlib.util, os, subprocess, sys

if importlib.util.find_spec("anthropic") is None:          # install once per Colab session
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "anthropic"], check=True)

try:
    from google.colab import userdata                     # Colab: key saved in the Secrets panel (key icon)
    os.environ["ANTHROPIC_API_KEY"] = userdata.get("ANTHROPIC_API_KEY")
except ImportError:
    pass                                                    # not in Colab: set ANTHROPIC_API_KEY in your environment
except Exception:
    print("Add a secret called ANTHROPIC_API_KEY in Colab's Secrets panel, then run this cell again.")

import anthropic

client = anthropic.Anthropic()        # reads ANTHROPIC_API_KEY from the environment
MODEL = "claude-haiku-5-5"            # fast and low-cost; check docs.claude.com for current model names

def ask(prompt, system=None, max_tokens=500):
    extra = {"system": system} if system else {}
    response = client.messages.create(model=MODEL, max_tokens=max_tokens,
                                      messages=[{"role": "user", "content": prompt}], **extra)
    return response.content[0].text
```
""".strip()

# Customer messages for a fictional mobile-money company, used in several lessons.
MESSAGES = r"""
```python
support_messages = [
    ("I sent 20,000 RWF to my brother yesterday but he did not receive it", "payment"),
    ("Internet is very slow in Huye since this morning", "network"),
    ("I forgot my mobile money PIN, please help", "account"),
    ("Money was deducted twice when I paid at the supermarket", "payment"),
    ("No 4G signal in my village for two days", "network"),
    ("My SIM card is blocked after I typed the wrong PIN", "account"),
    ("How do I reverse a payment to a wrong number?", "payment"),
    ("The data bundle I bought is not working", "network"),
]
CATEGORIES = ["payment", "network", "account"]
print(len(support_messages), "messages")
```
""".strip()

WEEK2 = {
    "title": "Week 2 · Building with LLM APIs",
    "lessons": [
        # ------------------------------------------------------------------ 7
        {
            "title": "Your First LLM API Call",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=EWvNQjAaOHw",
            "content": r"""
**Learning objective:** Call a large language model from Python, keep your API key safe, read the parts of a response (text, stop reason, token usage) and estimate what a call costs.

## Chat app vs API

A chat app (claude.ai, ChatGPT, Gemini) is a website for people. An **API** (application programming interface) lets **your code** send a request and get the answer back — so you can build the model into your own website, WhatsApp bot, school system or business tool.

```
your program  --(prompt, settings, API key)-->  LLM provider
your program  <--(answer, token usage)--------  LLM provider
```

## Step 1 — Get an API key, and keep it secret

1. Create an account in the provider's console (for Claude: console.anthropic.com) and create an **API key**.
2. API use is paid per token. A few dollars of credit is enough for this whole course with a small, fast model. Set a **spending limit** in the console.
3. Free options exist too: some providers offer free tiers (see the Gemini example below), and Lesson 22 shows how to run open models for free in Colab.

An API key is like a password **and** a credit card. Never paste it into code you share, a GitHub repository, a screenshot or a chat. In Colab, open the **Secrets** panel (key icon on the left), add a secret named `ANTHROPIC_API_KEY`, and let your notebook read it.

## Step 2 — Set up

{SETUP}

`ask()` is a small helper we reuse all week: one prompt in, one text answer out.

## Step 3 — Your first call

```python
response = client.messages.create(
    model=MODEL,
    max_tokens=300,
    system="You are a friendly tutor for students in Rwanda. Use simple English.",
    messages=[{"role": "user", "content": "In two sentences, what is an API?"}],
)
print(response.content[0].text)
```

The answer is **different every time you run it** (Lesson 3: sampling). Your result will not match anyone else's word for word.

## Step 4 — Read the whole response

```python
print("stop reason: ", response.stop_reason)
print("input tokens:", response.usage.input_tokens)
print("output tokens:", response.usage.output_tokens)
print("model:       ", response.model)
```

| Field | Meaning |
|---|---|
| `content` | A list of blocks; for plain answers, `content[0].text` is the text |
| `stop_reason` | `end_turn` (finished), `max_tokens` (cut off — raise the limit), `tool_use` (wants a tool, Lesson 9) |
| `usage` | Tokens read and written — this is what you pay for |

`max_tokens` is a **ceiling** on the answer length, not a target. If `stop_reason` is `max_tokens`, the answer was cut off mid-sentence.

## Step 5 — Estimate the cost

Prices are listed per **million** tokens and change over time — always check the provider's current price list. With example prices:

```python
PRICE_IN = 1.00     # example US$ per million input tokens  (check the real price list)
PRICE_OUT = 5.00    # example US$ per million output tokens

def cost_usd(usage):
    return usage.input_tokens / 1e6 * PRICE_IN + usage.output_tokens / 1e6 * PRICE_OUT

c = cost_usd(response.usage)
print(f"this call: ${c:.6f}   ->  10,000 similar calls: ${c * 10_000:.2f}")
```

One small call costs a tiny fraction of a cent; costs matter when an app makes thousands of calls a day, or sends long documents every time.

## The same idea with another provider

Many providers, including Google's Gemini, also accept the "OpenAI-compatible" format. Google AI Studio offers a free tier for experimenting:

```python
if importlib.util.find_spec("openai") is None:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "openai"], check=True)
from openai import OpenAI

gemini = OpenAI(api_key=os.environ.get("GEMINI_API_KEY", "paste-in-colab-secrets"),
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
GEMINI_MODEL = "gemini-2.5-flash"          # pick a current model name in aistudio.google.com
if os.environ.get("GEMINI_API_KEY"):
    reply = gemini.chat.completions.create(
        model=GEMINI_MODEL,
        messages=[{"role": "system", "content": "Answer in one sentence."},
                  {"role": "user", "content": "What is an API?"}])
    print(reply.choices[0].message.content)
```

The shapes differ slightly — `choices[0].message.content` instead of `content[0].text` — but the ideas (messages, roles, tokens) are the same everywhere. The rest of the course uses the Claude API; adapting to another provider takes a few lines.

## Key terms

- **API** — a way for programs to use a service.
- **API key** — your secret credential; whoever has it can spend your money.
- **Messages** — the conversation sent to the model, each with a role.
- **max_tokens** — the most tokens the answer may use.
- **stop_reason** — why the model stopped.
- **Usage** — tokens in and out, the basis of cost.

**Takeaway:** An LLM API call is a list of messages in, text and token usage out — keep the key secret, check why the model stopped, and keep an eye on tokens because they are your cost.

## Try it yourself

1. Ask the same question three times. Compare the answers and their token counts.
2. Set `max_tokens=20` and ask for a long explanation. What is the `stop_reason`?
3. Change the system prompt to "Answer only in Kinyarwanda" and ask a simple question. How good is the answer?
4. Calculate the cost of sending a 10-page document (about 5,000 tokens) and getting a 300-token summary, with the example prices.
""",
            "quiz": [
                ("What does an LLM API let you do?",
                 ["Chat only on a website", "Use the model from your own code and apps", "Train a model for free", "Avoid paying for tokens"],
                 1, "Your program sends requests and gets answers."),
                ("Where should you keep your API key in Colab?",
                 ["Directly in the code", "In the Secrets panel, read by the notebook", "In a screenshot", "In a public GitHub repo"],
                 1, "Keys are like passwords and credit cards."),
                ("stop_reason is 'max_tokens'. What happened?",
                 ["The answer finished normally", "The answer was cut off at the token limit", "A tool was called", "The key is wrong"],
                 1, "Raise max_tokens or ask for a shorter answer."),
                ("What do you pay for with an LLM API?",
                 ["Each second of use", "Input and output tokens", "The number of users", "Nothing"],
                 1, "Usage reports tokens in and out."),
                ("Why do two runs of the same prompt give different answers?",
                 ["The API is broken", "The model samples its tokens", "The key changes", "Tokens are deleted"],
                 1, "Sampling adds variety."),
                ("Which field holds the text of a Claude API answer?",
                 ["response.text", "response.content[0].text", "response.answer", "response.choices"],
                 1, "content is a list of blocks."),
            ],
        },
        # ------------------------------------------------------------------ 8
        {
            "title": "Prompt Engineering for Developers",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=jmwLzX_ltbQ",
            "content": r"""
**Learning objective:** Write prompts that work reliably inside programs — with clear instructions, delimiters, examples and output rules — and measure prompt quality on a small test set instead of guessing.

## Prompts inside programs are different

In a chat you can rephrase until you like the answer. In an app the prompt runs **thousands of times** on inputs you never see. It must be **clear, specific and testable**.

{SETUP}

{MESSAGES}

## Technique 1 — Clear role, task and rules

```python
SYSTEM = (
    "You sort customer messages for a mobile-money company in Rwanda. "
    "Reply with exactly one word, one of: payment, network or account. "
    "Do not explain."
)
print(ask("My SIM card is blocked after I typed the wrong PIN", system=SYSTEM))
```

The system prompt states the **role**, the **task**, the **allowed answers** and the **format**.

## Technique 2 — Separate instructions from data

Put user text inside clear markers, such as XML-style tags. The model can then tell your instructions from the text it must process — important when that text could contain instructions of its own (Lesson 23):

```python
def classify_prompt(message):
    return (
        "Classify the customer message inside <message> tags.\n"
        "Answer with one of: payment, network or account.\n\n"
        f"<message>\n{message}\n</message>"
    )

print(classify_prompt("No 4G signal in my village"))
```

## Technique 3 — Show examples (few-shot)

```python
FEW_SHOT = (
    "Examples:\n"
    "<message>My airtime purchase failed but money left my account</message> -> payment\n"
    "<message>I cannot open WhatsApp, the internet keeps dropping</message> -> network\n"
    "<message>I want to change the name on my account</message> -> account\n\n"
)
print(ask(FEW_SHOT + classify_prompt("Money was deducted twice at the supermarket"), system=SYSTEM))
```

Examples teach the format **and** the edge cases ("airtime failed but money left" is a payment problem, not a network one).

## Technique 4 — Let the model think first, when it helps

For multi-step problems, ask the model to reason **before** giving the final answer, and put the final answer in a fixed place so code can find it:

```python
problem = ("A shop sells 3 kg of beans at 1,200 RWF per kg and 2 kg of rice at 1,500 RWF per kg. "
           "The customer pays with 10,000 RWF. How much change?")
answer = ask(problem + "\nWork it out step by step, then give the final number on the last line as ANSWER: <number>.")
print(answer)
```

The correct change is 10,000 − (3,600 + 3,000) = **3,400 RWF**. Many modern models have a built-in "extended thinking" mode that does this reasoning for you.

## Technique 5 — Measure, don't guess

A prompt is only "good" if it works on many inputs. Build a small **test set** with the right answers and score each prompt version:

```python
def normalise(label):
    label = label.strip().lower().strip(".")
    return label if label in CATEGORIES else "other"

def evaluate(build_prompt, system=SYSTEM):
    correct = 0
    for message, expected in support_messages:
        got = normalise(ask(build_prompt(message), system=system, max_tokens=10))
        correct += got == expected
        if got != expected:
            print(f"  wrong: {message[:45]!r} -> {got} (expected {expected})")
    return correct / len(support_messages)

print("zero-shot accuracy:", evaluate(classify_prompt))
print("few-shot accuracy: ", evaluate(lambda m: FEW_SHOT + classify_prompt(m)))
```

`normalise` protects your app from small surprises ("Payment." or an explanation): anything outside the allowed labels becomes "other", which your code can send to a person. With real data, use at least 50–100 labelled examples, and keep them to re-test whenever you change the prompt or the model.

## A prompt checklist

| Ask yourself | Example |
|---|---|
| Is the role clear? | "You sort customer messages for a mobile-money company" |
| Is the task specific? | "Classify the message inside the tags" |
| Are the allowed outputs listed? | "one of: payment, network or account" |
| Is user text separated? | `<message>…</message>` |
| Are tricky cases shown? | Few-shot examples |
| Can code check the output? | One word, JSON, or `ANSWER:` line |
| Has it been tested? | Accuracy on a labelled test set |

## Key terms

- **Prompt template** — a prompt with slots filled by code.
- **Delimiters** — markers (tags, quotes) separating instructions from data.
- **Few-shot prompting** — giving solved examples in the prompt.
- **Step-by-step reasoning** — asking the model to work through a problem before answering.
- **Prompt evaluation** — scoring a prompt on a labelled test set.

**Takeaway:** In software, a prompt is code: give it a clear role and format, separate data from instructions, show examples, and measure it on a test set before you trust it.

## Try it yourself

1. Add five harder messages to the test set (for example "my money was sent but the internet failed"). Which prompt handles them best?
2. Write a prompt that extracts the amount of money from a message and returns only the number.
3. Ask the change problem with and without "step by step". Run each three times. Which is more reliable?
4. Translate the system prompt into Kinyarwanda and test it on Kinyarwanda messages.
""",
            "quiz": [
                ("Why must prompts in apps be more careful than in a chat?",
                 ["They cost nothing", "They run many times on inputs you never see", "Apps cannot use system prompts", "Chats are always wrong"],
                 1, "No one is there to rephrase."),
                ("Why put user text inside tags such as <message>…</message>?",
                 ["To make it shorter", "To separate data from your instructions", "To translate it", "To hide it from the model"],
                 1, "Delimiters reduce confusion and injection risk."),
                ("What is few-shot prompting?",
                 ["Using a small model", "Giving solved examples in the prompt", "Asking short questions", "Sending few tokens"],
                 1, "Examples show format and edge cases."),
                ("Why ask for the final answer on a fixed line such as ANSWER: <number>?",
                 ["It looks nicer", "So code can find and check it", "It reduces tokens to zero", "It is required by the API"],
                 1, "Machine-checkable output."),
                ("How do you know if a new prompt is better?",
                 ["It sounds better", "It scores higher on a labelled test set", "It is longer", "The model says so"],
                 1, "Measure, don't guess."),
                ("What should code do with an output that is not an allowed label?",
                 ["Crash", "Treat it as 'other' and handle it, for example send to a person", "Ignore the customer", "Retry forever"],
                 1, "Defensive handling keeps the app safe."),
            ],
        },
        # ------------------------------------------------------------------ 9
        {
            "title": "Structured Output and Tool Use",
            "minutes": 55,
            "video": "https://www.youtube.com/watch?v=jOEdb9HnwsQ",
            "content": r"""
**Learning objective:** Get reliable structured data (JSON) out of an LLM, validate it with Pydantic, and let the model call your own Python functions as tools.

## Text is for people; programs need structure

Your app needs fields it can store and act on — a category, an amount, a phone number — not a paragraph. Two techniques:

1. **Ask for JSON and validate it.**
2. **Use a tool definition (a JSON schema) to force the structure.**

{SETUP}

## Technique 1 — Ask for JSON, then validate

```python
import json
from pydantic import BaseModel, ValidationError, Field
from typing import Literal

class Ticket(BaseModel):
    category: Literal["payment", "network", "account"]
    urgent: bool
    summary: str = Field(max_length=120)

def extract_ticket(message, attempts=2):
    prompt = (
        "Read the customer message and reply with JSON only, no other text, with keys: "
        '"category" (payment, network or account), "urgent" (true or false), '
        '"summary" (under 120 characters).\n\n'
        f"<message>{message}</message>"
    )
    for attempt in range(attempts):
        raw = ask(prompt, max_tokens=200)
        try:
            return Ticket.model_validate(json.loads(raw))
        except (json.JSONDecodeError, ValidationError) as error:
            print(f"attempt {attempt + 1} failed validation: {type(error).__name__}")
            prompt += "\nYour last reply was not valid. Reply with the JSON object only."
    return None

ticket = extract_ticket("URGENT: money was deducted twice when I paid my rent!")
print(ticket)
```

**Pydantic** checks every field: the category must be one of the three words, `urgent` must be true or false, the summary must be short. If anything is wrong, we retry once with a reminder, and give up safely (return `None`) instead of crashing.

## Technique 2 — Force the shape with a tool

The API lets you describe a "tool" with a **JSON schema** and require the model to use it. The model then returns arguments that follow the schema. Pydantic can even write the schema for you:

```python
ticket_tool = {
    "name": "save_ticket",
    "description": "Save a classified customer support ticket.",
    "input_schema": Ticket.model_json_schema(),
}
response = client.messages.create(
    model=MODEL, max_tokens=300,
    tools=[ticket_tool],
    tool_choice={"type": "tool", "name": "save_ticket"},      # must use this tool
    messages=[{"role": "user", "content": "My SIM card is blocked, I cannot receive my salary!"}],
)
tool_call = next(block for block in response.content if block.type == "tool_use")
print(tool_call.input)
print(Ticket.model_validate(tool_call.input))
```

This is usually more reliable than asking for JSON in words. Still validate: your code, not the model, is responsible for what gets saved.

## Tool use: letting the model call your functions

Tools are not only for structure. You can give the model **real functions** — check a balance, look up an exchange rate, search a database. The model **decides** when a tool is needed and with what arguments; **your code runs it** and sends back the result; the model then writes the final answer.

```python
# Two "real" functions (here with practice data)
BALANCES = {"0788123456": 45_300, "0722000111": 1_250}
RATES_TO_RWF = {"USD": 1_400, "EUR": 1_500, "KES": 10.8}       # practice rates, not live data

def get_balance(phone: str) -> str:
    return f"{BALANCES.get(phone, 0):,} RWF" if phone in BALANCES else "unknown number"

def convert_to_rwf(amount: float, currency: str) -> str:
    rate = RATES_TO_RWF.get(currency.upper())
    return f"{amount * rate:,.0f} RWF" if rate else "unknown currency"

TOOLS = [
    {"name": "get_balance", "description": "Get the mobile-money balance of a phone number.",
     "input_schema": {"type": "object", "properties": {"phone": {"type": "string"}}, "required": ["phone"]}},
    {"name": "convert_to_rwf", "description": "Convert an amount of a foreign currency to Rwandan francs.",
     "input_schema": {"type": "object",
                      "properties": {"amount": {"type": "number"}, "currency": {"type": "string", "enum": ["USD", "EUR", "KES"]}},
                      "required": ["amount", "currency"]}},
]
FUNCTIONS = {"get_balance": get_balance, "convert_to_rwf": convert_to_rwf}
```

## The tool loop

```python
def run_with_tools(question, max_rounds=5):
    messages = [{"role": "user", "content": question}]
    for _ in range(max_rounds):
        response = client.messages.create(model=MODEL, max_tokens=500, tools=TOOLS, messages=messages)
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = FUNCTIONS[block.name](**block.input)        # YOUR code runs the tool
                print(f"  tool {block.name}({block.input}) -> {output}")
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
        messages.append({"role": "user", "content": results})
    return "Stopped: too many tool rounds."

print(run_with_tools("What is the balance of 0788123456?"))
```

Step by step: the model replies with `stop_reason == "tool_use"` and the tool name and arguments; your code runs the function; you send a `tool_result` back; the model writes a normal answer using the result. `max_rounds` stops endless loops.

## Safety rules for tools

- The model only **asks**; **your code decides** whether to run the tool. Check arguments (is this phone number allowed for this user?).
- Give read-only tools first. Anything that moves money or deletes data needs a **human confirmation** step.
- Log every tool call.

## Key terms

- **Structured output** — data in a fixed format such as JSON.
- **JSON schema** — a description of the fields and types allowed.
- **Pydantic** — a Python library that validates data against a model.
- **Tool use (function calling)** — the model requests a function call; your code runs it.
- **Tool result** — the output you send back for the model to use.

**Takeaway:** Validate every structured output with code, use tool schemas to force the shape, and remember that in tool use the model only asks — your program decides and acts.

## Try it yourself

1. Add a field `amount_rwf: int | None` to `Ticket` and test it on messages with and without an amount.
2. Ask "How much is 50 US dollars in Rwandan francs?" with `run_with_tools`. Which tool is used?
3. Add a tool `report_fraud(phone, description)` that only **prints** a report. When should it require a person to confirm?
4. Make `get_balance` refuse numbers that do not belong to the logged-in user. Where does that check belong — in the prompt or in the code?
""",
            "quiz": [
                ("Why validate an LLM's JSON with Pydantic?",
                 ["To make it longer", "Because the model can return wrong or missing fields", "Pydantic calls the API", "It is required by JSON"],
                 1, "Your code is responsible for what gets saved."),
                ("What does tool_choice={'type': 'tool', 'name': 'save_ticket'} do?",
                 ["Disables tools", "Forces the model to answer by using that tool", "Runs the tool automatically", "Deletes the ticket"],
                 1, "The output follows the tool's schema."),
                ("In tool use, who actually runs the function?",
                 ["The model", "Your code", "The user", "Nobody"],
                 1, "The model only requests it."),
                ("What stop_reason means the model wants a tool?",
                 ["end_turn", "tool_use", "max_tokens", "stop_sequence"],
                 1, "Then run the tool and send a tool_result."),
                ("Why limit the tool loop with max_rounds?",
                 ["To save the API key", "To avoid endless loops and runaway costs", "Tools only work once", "It makes answers longer"],
                 1, "Always bound loops."),
                ("Which tool most needs a human confirmation step?",
                 ["Check a balance", "Send money to another account", "Convert currency", "Look up a holiday date"],
                 1, "Actions that move money must be confirmed."),
            ],
        },
        # ------------------------------------------------------------------ 10
        {
            "title": "Conversations, Memory and Streaming",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=zjkBMFhNj_g",
            "content": r"""
**Learning objective:** Build a multi-turn chatbot, manage the context window by counting and trimming tokens, summarise long histories, and stream answers word by word.

## The model has no memory

Each API call is independent: the model remembers **nothing** between calls. A chat "remembers" only because the app sends the **whole conversation so far** every time.

{SETUP}

## A simple chat class

```python
class Chat:
    def __init__(self, system, max_history_tokens=2000):
        self.system = system
        self.history = []                      # list of {"role", "content"}
        self.max_history_tokens = max_history_tokens

    def send(self, user_text):
        self.history.append({"role": "user", "content": user_text})
        self.trim()
        response = client.messages.create(model=MODEL, max_tokens=400,
                                          system=self.system, messages=self.history)
        reply = response.content[0].text
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def tokens(self):
        return client.messages.count_tokens(model=MODEL, system=self.system,
                                            messages=self.history).input_tokens

    def trim(self):
        # drop the oldest question-and-answer pair until the history fits
        while len(self.history) > 2 and self.tokens() > self.max_history_tokens:
            self.history = self.history[2:]

bot = Chat("You are a helpful assistant for a Kigali library. Keep answers short.")
print(bot.send("Hello! My name is Aline. Do you have books about farming?"))
print(bot.send("What is my name?"))
print("history messages:", len(bot.history), "| tokens:", bot.tokens())
```

The second answer can use "Aline" only because the first exchange was sent again with the new question.

## Why trim?

Every token of history is sent — and paid for — on **every** turn, and the total must fit the model's **context window**. A long chat gets slower and more expensive with each message. `trim()` keeps the most recent turns within a budget, measured with the API's own `count_tokens` (exact for that model, unlike guessing from characters).

The messages list must start with a **user** turn and alternate user/assistant, which is why the trimming removes a whole question-and-answer pair at a time.

## Summarise instead of forgetting

Dropping old turns loses information ("My name is Aline"). A better approach for long chats: replace old turns with a short summary.

```python
def summarise_history(history):
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in history)
    return ask("Summarise this conversation in at most 3 short bullet points, keeping names, "
               "numbers and decisions:\n\n" + transcript, max_tokens=200)

def compact(chat, keep_last=2):
    old, recent = chat.history[:-keep_last], chat.history[-keep_last:]
    if not old:
        return
    summary = summarise_history(old)
    chat.system += "\n\nSummary of the earlier conversation:\n" + summary
    chat.history = recent

compact(bot)
print("history messages after compacting:", len(bot.history))
print(bot.system[-300:])
```

The summary moves into the system prompt; the recent turns stay word for word. Many production chatbots combine both: keep the last few turns exactly, summarise the rest.

## Long-term memory

For memory across days (a customer's preferences, a student's progress), store facts in your **own database** and add the relevant ones to the prompt when needed. Week 3's retrieval techniques do exactly this for documents. Store only what you need, and tell users what you keep — personal data is protected by law in Rwanda.

## Streaming: show words as they arrive

A long answer can take several seconds. **Streaming** sends the text in small pieces as it is generated, so people start reading immediately:

```python
with client.messages.stream(
    model=MODEL, max_tokens=300,
    messages=[{"role": "user", "content": "Give three tips for saving money as a student."}],
) as stream:
    for piece in stream.text_stream:
        print(piece, end="", flush=True)
    final = stream.get_final_message()
print("\n\noutput tokens:", final.usage.output_tokens)
```

Same total time, but it **feels** much faster. Web apps forward these pieces to the browser (for example with server-sent events).

## Key terms

- **Stateless** — the API keeps no memory between calls.
- **Conversation history** — earlier messages your app re-sends each turn.
- **Context window budget** — a token limit you choose for the history.
- **Summarisation memory** — replacing old turns with a summary.
- **Streaming** — receiving the answer in pieces as it is generated.

**Takeaway:** Chat memory is your app re-sending history; keep it within a token budget by trimming or summarising, store long-term facts yourself, and stream answers so people are not left waiting.

## Try it yourself

1. Set `max_history_tokens=150` and chat for six turns. When does the bot forget your name?
2. Use `compact` instead, and check whether the bot still knows your name.
3. Print `bot.tokens()` after each turn and plot how it grows.
4. Write a `Chat` method `reset()` that starts a new conversation but keeps the system prompt.
""",
            "quiz": [
                ("How does a chatbot 'remember' earlier messages?",
                 ["The model stores them", "The app re-sends the conversation history each turn", "The API key stores them", "It doesn't remember anything"],
                 1, "The API itself is stateless."),
                ("Why trim or summarise long conversations?",
                 ["History costs tokens every turn and must fit the context window", "The model gets angry", "Old messages are illegal", "To change the system prompt"],
                 0, "Cost and limits grow with history."),
                ("What is the advantage of summarising over simply dropping old turns?",
                 ["It is free", "Important facts such as names and decisions are kept", "It removes the system prompt", "It makes the model bigger"],
                 1, "Summaries keep key information in fewer tokens."),
                ("Why remove a whole question-and-answer pair when trimming?",
                 ["Messages must start with the user and alternate roles", "Pairs are cheaper", "The API deletes them anyway", "It is random"],
                 0, "The messages list must stay valid."),
                ("What does streaming improve?",
                 ["The total cost", "How fast the answer feels, by showing words as they arrive", "Accuracy", "The context window"],
                 1, "People start reading immediately."),
                ("Where should long-term memory such as user preferences be kept?",
                 ["Inside the model", "In your own database, added to prompts when needed", "In the API key", "Nowhere"],
                 1, "Store only what you need, legally."),
            ],
        },
        # ------------------------------------------------------------------ 11
        {
            "title": "Cost, Speed and Reliability",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=jmwLzX_ltbQ",
            "content": r"""
**Learning objective:** Measure the speed and cost of LLM calls, cut them with caching and good model choice, and handle errors, rate limits and timeouts so your app keeps working.

## Three things users notice

1. **Speed (latency)** — seconds until an answer.
2. **Cost** — your bill grows with tokens × calls.
3. **Reliability** — the network fails, providers are busy, limits are hit.

{SETUP}

## Measure first

```python
import time

def timed_ask(prompt, **kwargs):
    start = time.perf_counter()
    response = client.messages.create(model=MODEL, max_tokens=kwargs.get("max_tokens", 200),
                                      messages=[{"role": "user", "content": prompt}])
    seconds = time.perf_counter() - start
    return response, seconds

response, seconds = timed_ask("Name three crops grown in Rwanda.")
print(f"{seconds:.2f} s, {response.usage.input_tokens} tokens in, {response.usage.output_tokens} tokens out")
```

Output tokens dominate latency: the model writes one token at a time. Asking for **shorter answers** ("in one sentence", a lower `max_tokens`) is the easiest speed-up.

## Track spending across your app

```python
class UsageTracker:
    def __init__(self, price_in=1.00, price_out=5.00):     # example US$ per million tokens
        self.calls = self.tokens_in = self.tokens_out = 0
        self.price_in, self.price_out = price_in, price_out

    def add(self, usage):
        self.calls += 1
        self.tokens_in += usage.input_tokens
        self.tokens_out += usage.output_tokens

    def cost(self):
        return self.tokens_in / 1e6 * self.price_in + self.tokens_out / 1e6 * self.price_out

tracker = UsageTracker()
tracker.add(response.usage)
print(f"{tracker.calls} call(s), estimated ${tracker.cost():.6f}")
```

Log usage per feature and per user; set budgets and alerts in the provider console.

## Cache repeated questions

Many apps receive the same questions again and again ("What are your opening hours?"). Do not pay twice:

```python
import hashlib

cache = {}

def cached_ask(prompt, system=None):
    key = hashlib.sha256(f"{MODEL}|{system}|{prompt}".encode()).hexdigest()
    if key in cache:
        return cache[key], True
    answer = ask(prompt, system=system)
    cache[key] = answer
    return answer, False

for _ in range(3):
    answer, from_cache = cached_ask("What documents do I need to open a mobile-money account?")
    print("from cache" if from_cache else "new API call")
```

Only cache answers that do not depend on the user or on changing data. In production, use Redis or a database table with an expiry time.

## Prompt caching for long, repeated instructions

If every call starts with the same long text (a policy handbook, a product catalogue), providers can cache that prefix so repeated calls are cheaper and faster. With Claude you mark the reusable part:

```python
POLICY = "Company policy for customer support. " * 50       # imagine a long handbook here
response = client.messages.create(
    model=MODEL, max_tokens=200,
    system=[{"type": "text", "text": POLICY, "cache_control": {"type": "ephemeral"}}],
    messages=[{"role": "user", "content": "Can I get a refund for a failed airtime purchase?"}],
)
print(response.usage)
```

On later calls with the same prefix, `usage` reports cached tokens, which are billed at a reduced rate (see the provider's documentation for minimum lengths and prices).

## Choose the right model size

| Task | Usually enough |
|---|---|
| Classify, extract fields, short replies | Smallest, fastest model |
| Everyday chat and writing | Mid-size model |
| Hard reasoning, long documents, complex code | Largest model |

Test the small model first; move up only if your test set shows it is needed. A common pattern: a small model handles most messages and **escalates** hard cases to a larger model or a person.

## Handle errors

```python
import random

def ask_with_retry(prompt, attempts=4):
    for attempt in range(attempts):
        try:
            return ask(prompt, max_tokens=200)
        except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError) as error:
            wait = (2 ** attempt) + random.random()          # 1, 2, 4, 8 s... plus jitter
            print(f"{type(error).__name__}: retrying in {wait:.1f} s")
            time.sleep(wait)
        except anthropic.BadRequestError as error:
            print("Bad request — fix the code, do not retry:", error)
            return None
    return None

print(ask_with_retry("Say hello in Kinyarwanda."))
```

- **Temporary errors** (rate limits, network, server busy): retry with **exponential backoff** — wait longer each time, plus a little randomness so many clients don't retry together.
- **Permanent errors** (bad request, invalid key): don't retry; fix the cause.
- The official SDK already retries some errors; you can tune it: `anthropic.Anthropic(max_retries=3, timeout=30.0)`.
- Always have a **fallback**: a polite message, a simpler answer, or a hand-off to a person.

## Key terms

- **Latency** — time until the answer arrives.
- **Rate limit** — the maximum requests or tokens per minute your account may use.
- **Caching** — reusing earlier answers or prompt prefixes.
- **Exponential backoff** — retrying after waits that double each time.
- **Fallback** — what the app does when the model cannot answer.

**Takeaway:** Measure tokens and time, cache what repeats, use the smallest model that passes your tests, and treat errors as normal events with retries and fallbacks.

## Try it yourself

1. Time the same question with `max_tokens=50` and `max_tokens=500` and "answer in one sentence" vs "explain in detail".
2. Add a `max_size` to the cache that removes the oldest entry when it is full.
3. Simulate an error by setting `client = anthropic.Anthropic(api_key="wrong")`. Which exception do you get, and should it be retried?
4. Estimate the monthly cost of a bot answering 2,000 messages a day at about 400 input and 150 output tokens each, with the example prices.
""",
            "quiz": [
                ("What usually makes up most of an LLM call's latency?",
                 ["Reading the API key", "Generating output tokens one by one", "DNS lookups", "The system prompt"],
                 1, "Shorter answers are faster."),
                ("When is it safe to cache an answer?",
                 ["Always", "When it doesn't depend on the user or on changing data", "Never", "Only for errors"],
                 1, "Personal or live answers must not be shared."),
                ("What does prompt caching help with?",
                 ["Repeating a long identical prefix such as a handbook more cheaply and quickly", "Storing API keys", "Changing models", "Removing tokens from answers"],
                 0, "Repeated prefixes are cached by the provider."),
                ("Which error should NOT be retried?",
                 ["Rate limit", "Network connection error", "Bad request (invalid input)", "Server temporarily busy"],
                 2, "Fix the request instead."),
                ("What is exponential backoff?",
                 ["Retrying immediately forever", "Waiting longer after each failed attempt", "Switching off the app", "Lowering the price"],
                 1, "1, 2, 4, 8 seconds… plus jitter."),
                ("How should you choose a model size?",
                 ["Always the largest", "Start small and move up only if your tests show it is needed", "Always the cheapest regardless of quality", "Randomly"],
                 1, "Let the test set decide."),
            ],
        },
        # ------------------------------------------------------------------ 12
        {
            "title": "Week 2 Project: A Customer-Support Assistant",
            "minutes": 120,
            "video": "https://www.youtube.com/watch?v=EWvNQjAaOHw",
            "content": r"""
**Learning objective:** Build and test a complete LLM-powered support assistant that classifies messages, extracts details, protects personal data, drafts replies from company rules and knows when to hand over to a person.

## The brief

**PayKwik** (a made-up mobile-money company) receives thousands of messages a day. Build an assistant that, for each message:

1. **Removes personal data** (phone numbers, ID numbers) before anything is sent to the AI provider.
2. **Classifies** it (payment, network, account) and marks urgency — as validated structured data.
3. **Drafts a reply** using only the company's rules.
4. **Escalates** to a human when it should.

{SETUP}

{MESSAGES}

## Part 1 — Protect personal data first

```python
import re

PHONE = re.compile(r"\b(?:\+?250|0)7[2389]\d{7}\b")      # Rwandan mobile numbers
NATIONAL_ID = re.compile(r"\b1\d{15}\b")                  # 16-digit national ID format

def redact(text):
    text = PHONE.sub("[PHONE]", text)
    return NATIONAL_ID.sub("[ID]", text)

print(redact("Please send it to 0788123456, my ID is 1199880012345678"))
```

Only send what the AI needs. Keep the original message in your own secure system; the provider sees the redacted version. This follows the "data minimisation" principle in Rwanda's data protection law.

## Part 2 — Classify with a validated schema

```python
from pydantic import BaseModel
from typing import Literal

class Triage(BaseModel):
    category: Literal["payment", "network", "account"]
    urgent: bool
    confidence: float          # 0 to 1: how sure the model is

triage_tool = {"name": "triage", "description": "Classify a customer support message.",
               "input_schema": Triage.model_json_schema()}

def triage(message):
    response = client.messages.create(
        model=MODEL, max_tokens=200, tools=[triage_tool],
        tool_choice={"type": "tool", "name": "triage"},
        system="You triage messages for a mobile-money company. Mark as urgent anything involving lost money, fraud or blocked access.",
        messages=[{"role": "user", "content": f"<message>{message}</message>"}],
    )
    data = next(b.input for b in response.content if b.type == "tool_use")
    return Triage.model_validate(data)

print(triage(redact("My SIM is blocked and I cannot receive my salary, number 0788123456")))
```

## Part 3 — Draft replies from the rules only

```python
RULES = '''PayKwik support rules (practice text):
- Failed or double payments: refunds are checked within 48 hours; give the customer the transaction ID if they have it.
- Forgotten PIN: the customer must visit a PayKwik agent with their national ID. Never ask for the PIN.
- Network problems: ask for the location and the time it started; restarting the phone often helps.
- Never promise a refund amount or date beyond these rules.'''

def draft_reply(message, category):
    return ask(
        f"<rules>\n{RULES}\n</rules>\n\n<message>{message}</message>\n\n"
        f"Write a short, polite reply (at most 3 sentences) to this {category} message. "
        "Use only the rules. If the rules do not cover it, say a colleague will follow up.",
        system="You are PayKwik's support assistant. Be kind and clear.",
        max_tokens=250,
    )
```

## Part 4 — Decide when a person takes over

```python
ALWAYS_HUMAN = ("fraud", "stole", "steal", "scam", "hack", "police", "court")   # word stems: "stole" also matches "stolen"

def handle(message):
    safe = redact(message)
    t = triage(safe)
    needs_human = (t.urgent or t.confidence < 0.7
                   or any(word in message.lower() for word in ALWAYS_HUMAN))
    reply = None if needs_human else draft_reply(safe, t.category)
    return {"category": t.category, "urgent": t.urgent, "confidence": round(t.confidence, 2),
            "to_human": needs_human, "reply": reply}

for text, _ in support_messages[:3]:
    print(text[:50], "->", handle(text))
print(handle("Someone stole my phone and is using my mobile money!"))
```

The escalation rules are **code**, not prompt text: they work even if the model is wrong or manipulated.

## Part 5 — Test before you trust

```python
correct, to_human = 0, 0
for text, expected in support_messages:
    result = handle(text)
    correct += result["category"] == expected
    to_human += result["to_human"]
print(f"category accuracy: {correct}/{len(support_messages)}, sent to a person: {to_human}")
```

Record accuracy, the share sent to humans, average tokens per message and estimated monthly cost. Read 20 drafted replies yourself: are they polite, correct and within the rules?

## Part 6 — Report (two pages)

1. The problem, the users and the risks.
2. The pipeline diagram: redact → triage → escalate or draft → (human review).
3. Test results: accuracy, escalation rate, cost estimate.
4. Five example replies with your comments.
5. Data protection: what is sent to the provider, what is stored, for how long.
6. What must be true before going live (for example: a human reviews drafts for the first month).

## Marking guide (self-check)

| Area | Excellent work |
|---|---|
| Privacy | Phone numbers and IDs redacted before every API call |
| Reliability | Structured output validated; errors handled |
| Safety | Escalation rules in code; no promises beyond the rules |
| Evaluation | Test set, accuracy and escalation rate reported |
| Communication | A manager can decide whether to pilot it |

**Takeaway:** A useful LLM app is a pipeline around the model — privacy first, validated structure, rules in code, human hand-off and testing — not just a clever prompt.

## Try it yourself

Complete Parts 1–6. Then add five messages in Kinyarwanda to the test set and measure how the assistant handles them.
""",
            "quiz": [
                ("Why redact phone numbers and ID numbers before calling the AI provider?",
                 ["To save tokens only", "To send only the data the task needs and protect customers' privacy", "Because the model cannot read numbers", "To make replies longer"],
                 1, "Data minimisation."),
                ("Why are escalation rules written in code rather than only in the prompt?",
                 ["Code is shorter", "They then work even if the model is wrong or manipulated", "Prompts cannot mention fraud", "It is cheaper"],
                 1, "Critical rules belong in code."),
                ("Which message should always go to a person?",
                 ["How do I check my balance?", "Someone stole my phone and is using my mobile money", "Internet is slow", "What are your hours?"],
                 1, "Fraud and theft need human handling."),
                ("Why does the reply prompt include the company rules inside <rules> tags?",
                 ["To make the model creative", "So replies are based only on approved rules", "To hide them from customers", "Rules are required by the API"],
                 1, "Grounding prevents invented promises."),
                ("What does the confidence field help with?",
                 ["Pricing", "Sending uncertain cases to a person", "Translation", "Formatting"],
                 1, "Low confidence → human review."),
                ("What should you do before going live?",
                 ["Nothing", "Test on labelled messages and have people review drafts at first", "Remove the tests", "Hide the escalation rules"],
                 1, "Evidence and oversight first."),
            ],
        },
    ],
}

for _lesson in WEEK2["lessons"]:
    _lesson["content"] = _lesson["content"].replace("{SETUP}", SETUP).replace("{MESSAGES}", MESSAGES)
