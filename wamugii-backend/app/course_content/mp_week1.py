"""Math & Python for AI -- Week 1: Python Basics for AI. Original WAMUGII content."""

WEEK1 = {
    "title": "Week 1 · Python Basics for AI",
    "lessons": [
        # ------------------------------------------------------------------ 1
        {
            "title": "Why Python for AI — and Your First Program",
            "minutes": 40,
            "video": "https://www.youtube.com/watch?v=fWjsdhR3z3c",
            "content": r"""
**Learning objective:** Explain why Python is the main language of AI, open a free Google Colab notebook, and run your first lines of code.

## Why Python?

Almost every AI tool you have heard of — from ChatGPT's training code to the crop-disease apps built in Africa — is built mostly with **Python**. There are four simple reasons:

1. **It reads almost like English.** `if price > 5000:` means exactly what it says.
2. **Huge free libraries.** Other people have already written the hard parts: NumPy for maths, Pandas for tables, Matplotlib for charts, scikit-learn and PyTorch for machine learning.
3. **One language for everything** — data cleaning, charts, models and even web apps.
4. **A big community.** Almost any error message you meet has been answered online.

You do not need to become a professional programmer to work in AI. But being able to **read and change** simple Python is one of the most valuable skills in this field.

## Your workspace: Google Colab

You do not need to install anything. **Google Colab** is a free website that runs Python for you on Google's computers. It works on a laptop and, for small exercises, even on a smartphone browser.

1. Go to **colab.research.google.com** and sign in with a Google (Gmail) account.
2. Click **New notebook**.
3. You will see a box called a **cell**. Type code in it.
4. Press **Shift + Enter** (or the ▶ button) to run the cell.

A notebook mixes **code cells** and **text cells**, so you can write notes beside your code. Colab saves your notebooks in your Google Drive. NumPy, Pandas and Matplotlib are already installed.

## Your first program

Type this in a cell and run it:

```python
print("Muraho! I am learning Python for AI.")
```

`print()` shows something on the screen. The text inside the quotes is called a **string**.

Now try some maths:

```python
print(2 + 3)
print(7 * 6)
print(100 / 8)
print(2 ** 10)
```

`**` means "to the power of", so `2 ** 10` is 1024.

## Comments

A line that starts with `#` is a **comment**. Python ignores it — it is a note for people.

```python
# Price of one litre of milk in RWF
print(800 * 3)   # three litres
```

Good comments explain **why**, not just what. You will thank yourself later.

## Errors are normal

Type this on purpose:

```python
print("Hello"
```

Python shows a **SyntaxError**, because the closing bracket is missing. Every programmer sees errors every day. Read the **last line** of the error first: it usually tells you what went wrong. Fix it and run again.

## Key terms

- **Python** — a programming language that is easy to read and widely used for AI and data.
- **Notebook** — a document that mixes code, results and notes (Colab, Jupyter).
- **Cell** — one box of code or text in a notebook.
- **String** — text inside quotes, such as `"Kigali"`.
- **Comment** — a note after `#` that Python ignores.
- **Error message** — Python's explanation of what went wrong; read the last line first.

**Takeaway:** Python is the language of AI because it is readable and has free libraries for everything. Colab lets you run it free in your browser — and errors are just messages to read and fix.

## Try it yourself

1. Open a new Colab notebook and name it `math-python-week1`.
2. Print your name, your town and one reason you want to learn AI — on three lines.
3. Calculate how many hours are in one year (`365 * 24`) and how many seconds (`365 * 24 * 60 * 60`).
4. Make one error on purpose, read the last line of the message, then fix it.
""",
            "quiz": [
                ("Why is Python the main language for AI?",
                 ["It is the oldest language", "It is readable and has many free libraries for maths, data and machine learning", "It only runs on phones", "It needs no computer"],
                 1, "Readability plus libraries like NumPy, Pandas and PyTorch make Python the standard for AI."),
                ("What is Google Colab?",
                 ["A paid antivirus", "A free website that runs Python notebooks in your browser", "A type of spreadsheet", "A phone game"],
                 1, "Colab runs Python on Google's computers, free, with the main data libraries already installed."),
                ("How do you run a cell in Colab?",
                 ["Press Shift + Enter or the ▶ button", "Restart the computer", "Close the tab", "Type RUN in capital letters"],
                 0, "Shift + Enter runs the current cell and shows its output below it."),
                ("What does `2 ** 3` give?",
                 ["6", "5", "8", "23"],
                 2, "`**` means power: 2 × 2 × 2 = 8."),
                ("What does Python do with a line that starts with `#`?",
                 ["Runs it twice", "Ignores it — it is a comment", "Deletes the notebook", "Prints it in red"],
                 1, "Comments are notes for people; Python skips them."),
                ("When you get an error, what should you read first?",
                 ["The first word only", "The last line of the error message", "Nothing — restart Colab", "The page title"],
                 1, "The last line usually names the error type and the reason."),
            ],
        },
        # ------------------------------------------------------------------ 2
        {
            "title": "Variables, Numbers and Text",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
            "content": r"""
**Learning objective:** Store values in variables, use the main data types (int, float, str, bool), do calculations, and build clear messages with f-strings.

## Variables are labelled boxes

A **variable** is a name that holds a value, so you can use it again.

```python
shop_name = "Ineza Mini-Market"
milk_price = 800          # RWF per litre
litres_sold = 45

total = milk_price * litres_sold
print(total)
```

The `=` sign means **"store the value on the right in the name on the left"**. It is not "equals" like in maths.

**Naming rules:** use letters, numbers and `_`; start with a letter; no spaces. Choose clear names: `litres_sold` is better than `x`.

## The four basic types

| Type | Name | Example | Used for |
|---|---|---|---|
| `int` | integer | `45`, `-3` | whole numbers: counts, quantities |
| `float` | decimal number | `3.5`, `0.18` | prices with decimals, measurements, probabilities |
| `str` | string (text) | `"Huye"` | names, places, messages |
| `bool` | boolean | `True`, `False` | yes/no facts |

Check a type with `type()`:

```python
print(type(45))
print(type(0.18))
print(type("Huye"))
print(type(True))
```

## Doing maths

```python
price = 7500
vat_rate = 0.18                 # Rwanda's standard VAT rate is 18%
vat = price * vat_rate
price_with_vat = price + vat
print(price_with_vat)           # 8850.0

print(17 // 5)   # whole-number division -> 3
print(17 % 5)    # remainder -> 2
print(round(3.14159, 2))   # 3.14
```

`//` and `%` are very useful: 17 eggs packed in trays of 5 gives 3 full trays and 2 eggs left over.

## Working with text

```python
first = "Aline"
last = "Uwase"
full = first + " " + last      # joining strings
print(full)
print(full.upper())            # ALINE UWASE
print(len(full))               # number of characters: 11
print("  kigali ".strip().title())   # Kigali
```

## f-strings: the best way to build messages

Put `f` before the quotes and variables inside `{ }`:

```python
customer = "Eric"
amount = 12500
print(f"Thank you {customer}, you paid {amount:,} RWF.")
```

`{amount:,}` adds thousands separators: `12,500`. Use `{value:.2f}` for two decimal places.

## Converting between types

Text that looks like a number is still text. Data often arrives as text, so you must convert it:

```python
quantity_text = "12"
quantity = int(quantity_text)     # text -> int
price = float("850.5")            # text -> float
print(quantity * price)
print(str(2026) + " budget")      # number -> text
```

`"12" + 3` gives an error, because Python will not mix text and numbers without being told.

## Key terms

- **Variable** — a name that stores a value.
- **int / float** — whole numbers / decimal numbers.
- **str** — text, always inside quotes.
- **bool** — `True` or `False`.
- **f-string** — a string starting with `f` that can include variables in `{ }`.
- **Type conversion** — changing a value's type with `int()`, `float()` or `str()`.

**Takeaway:** Variables store values; every value has a type. Do maths with numbers, join and clean text with string methods, and use f-strings for clear messages. Convert text to numbers before calculating.

## Try it yourself

1. Create variables for a product name, its price in RWF and the quantity sold.
2. Calculate the total, the 18% VAT and the total with VAT.
3. Print one sentence with an f-string, for example: *"5 bags of Rice 5kg cost 37,500 RWF (44,250 RWF with VAT)."*
4. A customer types `"  musanze  "`. Clean it to `"Musanze"` with string methods.
""",
            "quiz": [
                ("What does `=` do in `price = 800`?",
                 ["Checks if price equals 800", "Stores the value 800 in the variable named price", "Prints 800", "Deletes price"],
                 1, "In Python, `=` is assignment: it stores the value on the right in the name on the left."),
                ("Which type is the value `0.18`?",
                 ["int", "str", "float", "bool"],
                 2, "A number with a decimal point is a float."),
                ("What does `17 % 5` give?",
                 ["3", "2", "3.4", "85"],
                 1, "`%` gives the remainder: 17 = 3 × 5 + 2."),
                ("What does `f\"Total: {amount:,} RWF\"` do when amount is 12500?",
                 ["Prints 'Total: {amount:,} RWF'", "Prints 'Total: 12,500 RWF'", "Gives an error", "Prints 'Total: 12500.0 RWF'"],
                 1, "An f-string fills in the variable; `:,` adds thousands separators."),
                ("Why does `\"12\" + 3` give an error?",
                 ["12 is too big", "You cannot add text and a number without converting", "Python cannot add", "The quotes are wrong"],
                 1, "\"12\" is a string. Convert it with int(\"12\") before adding."),
                ("Which is the best variable name?",
                 ["x", "litres sold", "litres_sold", "1litres"],
                 2, "Clear words joined with underscores, starting with a letter, and no spaces."),
            ],
        },
        # ------------------------------------------------------------------ 3
        {
            "title": "Lists, Dictionaries and Loops",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=W8KRzm-HUcc",
            "content": r"""
**Learning objective:** Store many values in lists and dictionaries, and use `for` loops to process them one by one — the pattern behind all data work.

## Lists: many values in order

```python
daily_sales = [42000, 38500, 51000, 47200, 60300]   # RWF, Monday to Friday
print(daily_sales[0])     # first item -> 42000
print(daily_sales[-1])    # last item -> 60300
print(len(daily_sales))   # 5 days
print(sum(daily_sales))   # total for the week
print(max(daily_sales), min(daily_sales))
```

Python counts from **0**, so the first item is `[0]`. Negative numbers count from the end.

**Slicing** takes part of a list: `daily_sales[1:3]` gives items 1 and 2 (the end is not included).

Changing a list:

```python
daily_sales.append(55800)   # add Saturday
daily_sales[0] = 43000      # correct Monday
print(daily_sales)
```

## Dictionaries: values with names

A **dictionary** stores **key: value** pairs — like a real dictionary stores word: meaning.

```python
prices = {"Rice 5kg": 7500, "Sugar 1kg": 1600, "Milk 1L": 800}
print(prices["Sugar 1kg"])         # 1600
prices["Cooking oil 1L"] = 3200    # add a new product
prices["Milk 1L"] = 850            # update a price
print(prices.keys())
print("Bread" in prices)           # False
```

Use a dictionary when you look things up **by name**, and a list when **order** matters.

## for loops: do something for each item

```python
for amount in daily_sales:
    print(amount)
```

The **indented** lines (4 spaces) run once for every item. Indentation is how Python knows what is inside the loop.

A very common pattern is the **running total**:

```python
total = 0
for amount in daily_sales:
    total = total + amount
print(f"Week total: {total:,} RWF")
```

Looping over a dictionary:

```python
for product, price in prices.items():
    print(f"{product}: {price:,} RWF")
```

`range()` gives numbers to loop over: `range(5)` gives 0, 1, 2, 3, 4.

```python
for day in range(1, 8):
    print("Day", day)
```

## List comprehensions: a short way to build lists

```python
with_vat = [round(p * 1.18) for p in [7500, 1600, 800]]
print(with_vat)   # [8850, 1888, 944]
```

Read it as: *"for each p in the list, calculate p × 1.18"*. You will see this style often in data code.

## Why this matters for AI

A dataset is really a big list of examples, and each example is like a dictionary of features: `{"age": 34, "sales": 180000, "repaid": True}`. Training a model is, underneath, loops over these examples many times. NumPy and Pandas (Week 2) will do these loops for you — much faster — but the idea is the same.

## Key terms

- **List** — an ordered collection: `[1, 2, 3]`.
- **Index** — an item's position, starting at 0.
- **Dictionary** — key: value pairs: `{"Milk 1L": 800}`.
- **Loop** — code that repeats for each item.
- **Indentation** — the spaces that show which lines belong to a loop or block.
- **List comprehension** — a one-line way to build a new list from another.

**Takeaway:** Lists keep values in order, dictionaries find values by name, and `for` loops process each value. Data science is built on these three ideas.

## Try it yourself

1. Make a list of the marks of 6 students (out of 100). Print the highest, the lowest and the average (`sum(...) / len(...)`).
2. Use a loop to count how many students scored 50 or more.
3. Make a dictionary of 4 Rwandan districts and their population (look up rough numbers or invent them). Loop over it and print each district in a sentence.
4. Use a list comprehension to convert a list of prices in RWF to USD (choose an exchange rate and note the date you used).
""",
            "quiz": [
                ("What does `[10, 20, 30][0]` give?",
                 ["20", "10", "30", "An error"],
                 1, "Python counts from 0, so index 0 is the first item."),
                ("What does `[10, 20, 30][-1]` give?",
                 ["10", "30", "-1", "An error"],
                 1, "Negative indexes count from the end; -1 is the last item."),
                ("When should you use a dictionary instead of a list?",
                 ["When you look values up by name (key)", "Never", "Only for numbers", "When order is the only thing that matters"],
                 0, "Dictionaries map keys to values, so you can find a price by product name."),
                ("How does Python know which lines are inside a for loop?",
                 ["Curly brackets", "Indentation (spaces at the start of the line)", "The word END", "Capital letters"],
                 1, "Indented lines under the `for` line form the loop body."),
                ("What does `range(3)` give?",
                 ["1, 2, 3", "0, 1, 2", "0, 1, 2, 3", "3, 2, 1"],
                 1, "range(3) starts at 0 and stops before 3."),
                ("What does `[x * 2 for x in [1, 2, 3]]` give?",
                 ["[1, 2, 3, 1, 2, 3]", "[2, 4, 6]", "6", "[3, 4, 5]"],
                 1, "The list comprehension doubles each item."),
            ],
        },
        # ------------------------------------------------------------------ 4
        {
            "title": "Making Decisions and Writing Functions",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=q0bQrGhdPm4",
            "content": r"""
**Learning objective:** Use `if`, `elif` and `else` to make decisions in code, and write your own functions to reuse logic.

## Comparisons give True or False

```python
print(7500 > 5000)      # True
print(800 == 850)       # False  (== checks equality)
print("Huye" != "Musanze")   # True  (!= means "not equal")
```

Combine conditions with `and`, `or` and `not`:

```python
amount = 60000
is_member = True
print(amount > 50000 and is_member)   # True
```

## if, elif, else

```python
amount = 60000

if amount >= 100000:
    discount = 0.10
elif amount >= 50000:
    discount = 0.05
else:
    discount = 0

print(f"Discount: {discount:.0%}")
```

Python checks the conditions **from top to bottom** and runs only the **first** block that is True. `else` catches everything left. `{discount:.0%}` shows 0.05 as `5%`.

Decisions inside loops are very common:

```python
marks = [72, 45, 88, 39, 61]
for m in marks:
    if m >= 50:
        print(m, "pass")
    else:
        print(m, "fail")
```

## Functions: write once, use many times

A **function** is a named block of code that takes **inputs** (parameters) and **returns** an output.

```python
def price_with_vat(price, rate=0.18):
    # Return the price including VAT.
    return round(price * (1 + rate))

print(price_with_vat(7500))          # 8850
print(price_with_vat(1000, 0.0))     # 1000 (VAT-exempt item)
```

- `def` starts the function; the inputs go in brackets.
- `rate=0.18` is a **default value**, used when you do not give one.
- `return` sends the answer back. Without `return`, a function gives `None`.

A function that makes a decision:

```python
def grade(mark):
    if mark >= 80:
        return "A"
    elif mark >= 70:
        return "B"
    elif mark >= 60:
        return "C"
    elif mark >= 50:
        return "D"
    return "F"

for m in [91, 74, 55, 30]:
    print(m, grade(m))
```

## Why functions matter

- **No copy-paste mistakes** — fix the logic once and it is fixed everywhere.
- **Readable code** — `price_with_vat(7500)` explains itself.
- **Testable** — you can check a small function on its own.

In AI, almost everything is a function: a model is a function from features to a prediction; a loss is a function that measures error. In Week 4 you will write both yourself.

## A simple "model" as a function

```python
def loan_decision(monthly_sales, late_payments):
    if late_payments >= 3:
        return "refuse"
    if monthly_sales >= 150000:
        return "approve"
    return "review by officer"

print(loan_decision(180000, 0))
print(loan_decision(60000, 1))
print(loan_decision(250000, 4))
```

This is a hand-written **rule-based** model. Machine learning would *learn* the thresholds from past data instead of us choosing them.

## Key terms

- **Condition** — an expression that is True or False.
- **if / elif / else** — choose which block of code runs.
- **Function** — a named, reusable block of code: `def name(inputs):`.
- **Parameter** — an input name in the function definition.
- **Return value** — the result a function sends back.
- **Default value** — a parameter value used when none is given.

**Takeaway:** `if/elif/else` lets code make decisions; functions package logic so you can reuse, read and test it. A model, in the end, is a function.

## Try it yourself

1. Write `bmi(weight_kg, height_m)` that returns weight ÷ height². Test it with two people.
2. Write `bmi_category(value)` that returns "under", "normal", "over" or "obese" (use 18.5, 25 and 30 as limits).
3. Write `transport_fare(km, raining=False)` that returns 400 + 230 × km, plus 300 if it is raining. Test it for 5 km dry and 5 km in rain.
4. Loop over a list of 5 distances and print the fare for each.
""",
            "quiz": [
                ("What does `==` do?",
                 ["Stores a value", "Checks whether two values are equal", "Adds two numbers", "Starts a function"],
                 1, "`==` compares; `=` assigns."),
                ("With amount = 60000, which block runs? if amount >= 100000 … elif amount >= 50000 … else …",
                 ["The if block", "The elif block", "The else block", "All of them"],
                 1, "Python runs the first condition that is True: 60000 ≥ 50000."),
                ("What keyword starts a function definition?",
                 ["func", "def", "function", "return"],
                 1, "Functions start with `def name(parameters):`."),
                ("What does a function give back if it has no `return`?",
                 ["0", "None", "An error", "The last line"],
                 1, "Without a return statement, Python returns None."),
                ("In `def price_with_vat(price, rate=0.18):`, what is `rate=0.18`?",
                 ["A default value used when no rate is given", "A comment", "A loop", "An error"],
                 0, "Default values let callers skip that argument."),
                ("Why are functions useful?",
                 ["They make code slower", "They let you reuse, read and test logic without copy-paste", "They delete data", "They are only for games"],
                 1, "Functions package logic so it is written once and used many times."),
            ],
        },
        # ------------------------------------------------------------------ 5
        {
            "title": "Files, Modules and Libraries",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=eWRfhZUzrAc",
            "content": r"""
**Learning objective:** Read and write text and CSV files, use Python's built-in modules, and import the data libraries you will use for the rest of the course.

## Saving and reading a text file

```python
with open("notes.txt", "w") as f:
    f.write("Week 1 notes\n")
    f.write("Python is readable.\n")

with open("notes.txt") as f:
    text = f.read()
print(text)
```

- `"w"` means **write** (it replaces the file). `"a"` means **append** (add to the end). No letter means **read**.
- `with` closes the file for you when the block ends — always use it.
- In Colab, files appear in the **folder icon** on the left. They disappear when the session ends unless you download them or save to Google Drive.

## CSV files: tables in plain text

A **CSV** (comma-separated values) file is the most common way to share data. Each line is a row; commas separate the columns:

```text
product,price,quantity
Rice 5kg,7500,3
Milk 1L,800,10
```

Write and read one with the built-in `csv` module:

```python
import csv

rows = [
    ["product", "price", "quantity"],
    ["Rice 5kg", 7500, 3],
    ["Milk 1L", 800, 10],
    ["Sugar 1kg", 1600, 4],
]
with open("sales.csv", "w", newline="") as f:
    csv.writer(f).writerows(rows)

total = 0
with open("sales.csv") as f:
    for row in csv.DictReader(f):
        total += int(row["price"]) * int(row["quantity"])
print(f"Total sales: {total:,} RWF")
```

Notice `int(...)`: everything read from a CSV arrives as **text**. Next week, Pandas will read CSV files in one line and convert types for you.

## Modules: code other people wrote

A **module** is a file of ready-made Python code. Python includes many:

```python
import math
import random
import statistics

print(math.sqrt(144))                       # 12.0
print(round(math.pi, 4))                    # 3.1416
print(statistics.mean([72, 45, 88, 61]))    # 66.5
print(statistics.median([72, 45, 88, 61]))  # 66.5

random.seed(1)                    # same "random" numbers every run
print(random.randint(1, 6))       # roll a die
print(random.choice(["MoMo", "Cash", "Card"]))
```

`random.seed()` makes random results **repeatable**. AI researchers always set a seed so others can reproduce their results.

## Libraries: the AI toolkit

Bigger collections of modules are called **libraries** (or packages). These are the ones you will use:

| Library | Short name | What it does | Week |
|---|---|---|---|
| NumPy | `np` | Fast maths on arrays of numbers | 2–4 |
| Pandas | `pd` | Tables of data (like Excel in code) | 2, 4 |
| Matplotlib | `plt` | Charts and graphs | 2–4 |
| scikit-learn | `sklearn` | Ready-made machine-learning models | Next course |

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

print(np.__version__, pd.__version__)
```

The short names (`np`, `pd`, `plt`) are a convention — every tutorial uses them, so you should too.

On your own computer you install a library once with `pip install pandas` in a terminal. In Colab they are already installed; if one is missing, run `!pip install name` in a cell.

## Key terms

- **File mode** — `"r"` read, `"w"` write (replace), `"a"` append.
- **CSV** — a text file where commas separate columns.
- **Module** — a file of reusable Python code (`math`, `random`, `csv`).
- **Library / package** — a larger collection of modules (NumPy, Pandas).
- **import** — load a module or library so you can use it.
- **Seed** — a starting value that makes random results repeatable.

**Takeaway:** Use `with open(...)` for files and the `csv` module for simple tables. Import modules instead of writing everything yourself — and meet NumPy, Pandas and Matplotlib, your tools for the rest of the course.

## Try it yourself

1. Write a CSV file `students.csv` with columns `name, district, mark` and 5 rows.
2. Read it back and print the average mark and the name of the top student.
3. Use `random` with `seed(7)` to choose 3 random students for a presentation.
4. Import NumPy and Pandas and print their versions.
""",
            "quiz": [
                ("What does the mode `\"a\"` do in `open(\"log.txt\", \"a\")`?",
                 ["Reads the file", "Adds new text to the end of the file", "Deletes the file", "Replaces the file"],
                 1, "\"a\" means append: the new text goes after what is already there."),
                ("Why use `with open(...) as f:`?",
                 ["It makes the file bigger", "It closes the file automatically when the block ends", "It encrypts the file", "It is required for printing"],
                 1, "The with-block guarantees the file is closed, even if an error happens."),
                ("A value read from a CSV with the csv module is…",
                 ["Always an int", "Text (a string) until you convert it", "Always a float", "A list"],
                 1, "CSV files are text; convert with int() or float() before doing maths."),
                ("What does `random.seed(1)` do?",
                 ["Plants a tree", "Makes the random results repeatable", "Stops randomness forever", "Deletes random numbers"],
                 1, "The same seed gives the same sequence of random numbers each run."),
                ("Which library is used for tables of data, like Excel in code?",
                 ["Matplotlib", "Pandas", "math", "csv"],
                 1, "Pandas provides DataFrames — tables with rows and columns."),
                ("What is the usual short name for NumPy?",
                 ["nu", "np", "num", "py"],
                 1, "By convention: import numpy as np."),
            ],
        },
        # ------------------------------------------------------------------ 6
        {
            "title": "Week 1 Project: A Shop Sales Calculator",
            "minutes": 60,
            "video": "https://www.youtube.com/watch?v=UmNKiV7Lekk",
            "content": r"""
**Learning objective:** Combine variables, lists, dictionaries, loops, decisions, functions and files into one small program that solves a real problem.

## The task

A small shop in Kigali records each sale by hand. The owner wants a simple program that:

1. calculates each sale's total with 18% VAT,
2. gives a 5% discount on sales of 50,000 RWF or more,
3. prints a daily report (total, number of sales, best-selling product),
4. saves the sales to a CSV file.

You will build it step by step. Write each step in its own Colab cell and run it before moving on.

## Step 1 — The data

```python
prices = {"Rice 5kg": 7500, "Cooking oil 1L": 3200, "Sugar 1kg": 1600,
          "Milk 1L": 800, "Airtime 1000": 1000}

sales = [
    {"product": "Rice 5kg", "quantity": 4, "payment": "MoMo"},
    {"product": "Milk 1L", "quantity": 6, "payment": "Cash"},
    {"product": "Cooking oil 1L", "quantity": 2, "payment": "MoMo"},
    {"product": "Rice 5kg", "quantity": 7, "payment": "Card"},
    {"product": "Sugar 1kg", "quantity": 3, "payment": "Cash"},
    {"product": "Airtime 1000", "quantity": 5, "payment": "MoMo"},
]
```

## Step 2 — Functions for one sale

```python
VAT = 0.18

def sale_total(product, quantity):
    # Price x quantity, plus VAT, minus 5% if the sale is 50,000 RWF or more.
    subtotal = prices[product] * quantity
    total = subtotal * (1 + VAT)
    if total >= 50000:
        total = total * 0.95
    return round(total)

print(sale_total("Rice 5kg", 4))   # 35400
print(sale_total("Rice 5kg", 7))   # 58852 (discount applied)
```

## Step 3 — The daily report

```python
def daily_report(sales):
    grand_total = 0
    quantity_by_product = {}
    for s in sales:
        total = sale_total(s["product"], s["quantity"])
        s["total"] = total
        grand_total += total
        quantity_by_product[s["product"]] = quantity_by_product.get(s["product"], 0) + s["quantity"]

    best = max(quantity_by_product, key=quantity_by_product.get)
    momo = sum(1 for s in sales if s["payment"] == "MoMo")

    print("=== DAILY REPORT ===")
    print(f"Sales recorded : {len(sales)}")
    print(f"Total income   : {grand_total:,} RWF")
    print(f"Best seller    : {best} ({quantity_by_product[best]} units)")
    print(f"Paid by MoMo   : {momo} of {len(sales)}")
    return grand_total

daily_report(sales)
```

New tools here:
- `dict.get(key, 0)` returns 0 when the key is not there yet — perfect for counting.
- `max(d, key=d.get)` finds the key with the largest value.
- `sum(1 for s in sales if ...)` counts items that meet a condition.

## Step 4 — Save to CSV

```python
import csv

with open("sales_today.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["product", "quantity", "payment", "total"])
    writer.writeheader()
    writer.writerows(sales)

print(open("sales_today.csv").read())
```

## Step 5 — Make it your own (required)

Add **at least two** of these improvements:

- A function `add_sale(product, quantity, payment)` that refuses unknown products with a clear message.
- A report line showing income **by payment method**.
- A loyalty rule: MoMo payments above 20,000 RWF get an extra 1% off.
- Read the sales from a CSV file instead of typing them in the code.

## Checklist

- Every function has a clear name and a one-line comment explaining it.
- You tested each function with at least two inputs, including an edge case (for example, exactly 50,000 RWF).
- The report prints neatly with thousands separators.
- The CSV file opens correctly (download it from the Colab folder and open it in Excel or Google Sheets).

**Takeaway:** Real programs are small pieces — data, functions, loops and decisions — joined together. Build one step at a time and test each step before moving on.

## Try it yourself

Complete Steps 1–5 in one notebook. Then share the notebook (Colab → Share → "Anyone with the link can view") with a classmate and ask them to find one bug or one way to make the report clearer.
""",
            "quiz": [
                ("What does `quantity_by_product.get(product, 0)` return when the product is not in the dictionary yet?",
                 ["An error", "0", "None", "The product name"],
                 1, "get() returns the default value (0) instead of raising an error."),
                ("A sale's total with VAT is exactly 50,000 RWF. With the rule `if total >= 50000`, is the discount applied?",
                 ["Yes, because >= includes 50,000", "No", "Only on Mondays", "It causes an error"],
                 0, ">= means 'greater than or equal to', so 50,000 qualifies. Testing such edge cases is important."),
                ("What does `max(d, key=d.get)` return?",
                 ["The largest value", "The key whose value is largest", "The number of keys", "The first key"],
                 1, "It compares keys by their values and returns the key with the biggest value."),
                ("Why build the program step by step in separate cells?",
                 ["Colab requires it", "So you can test each part before adding the next", "To make it longer", "To hide errors"],
                 1, "Small tested steps make bugs easy to find."),
                ("What does `csv.DictWriter` write?",
                 ["Dictionaries as rows, using the fieldnames as columns", "Only numbers", "Pictures", "A PDF"],
                 0, "DictWriter turns each dictionary into a CSV row with the given columns."),
                ("Which is a good test case for the discount rule?",
                 ["Only one random sale", "A sale exactly at the 50,000 RWF limit, plus one below and one above", "No tests are needed", "Only very small sales"],
                 1, "Testing at, below and above a limit catches most mistakes in conditions."),
            ],
        },
    ],
}
