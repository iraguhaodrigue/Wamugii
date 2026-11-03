"""Math & Python for AI -- Week 2: Working with Data. Original WAMUGII content."""

# The practice dataset used in Week 2. It is simulated (invented) so every
# student gets exactly the same numbers without downloading anything.
SHOP_DATA = r"""
```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
n = 200
prices = {"Rice 5kg": 7500, "Cooking oil 1L": 3200, "Sugar 1kg": 1600,
          "Milk 1L": 800, "Airtime 1000": 1000}
products = rng.choice(list(prices), size=n, p=[0.2, 0.15, 0.2, 0.3, 0.15])
sales = pd.DataFrame({
    "date": pd.to_datetime("2026-01-01") + pd.to_timedelta(rng.integers(0, 181, n), unit="D"),
    "district": rng.choice(["Gasabo", "Kicukiro", "Nyarugenge"], size=n),
    "product": products,
    "quantity": rng.integers(1, 7, n),
    "payment": rng.choice(["MoMo", "Cash", "Card"], size=n, p=[0.55, 0.35, 0.10]),
})
sales["unit_price"] = sales["product"].map(prices)
sales["total"] = sales["quantity"] * sales["unit_price"]
sales = sales.sort_values("date").reset_index(drop=True)
```
""".strip()

WEEK2 = {
    "title": "Week 2 · Working with Data",
    "lessons": [
        # ------------------------------------------------------------------ 7
        {
            "title": "NumPy: Fast Maths on Arrays",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=GB9ByFAIAH4",
            "content": r"""
**Learning objective:** Create NumPy arrays, do maths on whole arrays at once, filter with conditions, and work with 2-D arrays — the format of almost all AI data.

## Why NumPy?

A Python list is flexible but slow for maths. **NumPy** stores numbers in an **array**: one block of memory, all the same type. Maths on arrays runs in fast compiled code — often 50–100 times faster than a loop. Every AI library (Pandas, scikit-learn, PyTorch) is built on this idea.

```python
import numpy as np

prices = np.array([7500, 3200, 1600, 800, 1000])
print(prices * 1.18)      # VAT on every price at once
print(prices.sum(), prices.mean(), prices.max())
```

No loop needed. Doing the same operation on every element at once is called **vectorisation**.

## Creating arrays

```python
a = np.array([2, 4, 6])
zeros = np.zeros(5)                 # [0. 0. 0. 0. 0.]
ones = np.ones(3)
steps = np.arange(0, 10, 2)          # [0 2 4 6 8]
grid = np.linspace(0, 1, 5)          # 5 evenly spaced values from 0 to 1
print(a.dtype, a.shape)              # int64 (3,)
```

## Maths between arrays

Arrays of the same shape combine **element by element**:

```python
quantity = np.array([4, 2, 6, 10, 5])
unit_price = np.array([7500, 3200, 1600, 800, 1000])
totals = quantity * unit_price
print(totals)                         # [30000  6400  9600  8000  5000]
print(totals.sum())                   # 59000
print(np.round(totals / totals.sum() * 100, 1))   # share of income in %
```

## Indexing, slicing and filtering

```python
print(totals[0], totals[-1])     # first and last
print(totals[1:3])               # items 1 and 2

big = totals > 8000              # a True/False array
print(big)                        # [ True False  True False False]
print(totals[big])               # only the big sales
print((totals > 8000).sum())     # how many are big -> 2
```

Filtering with a True/False array is called **boolean indexing**. It is the NumPy way to say *"give me the rows where…"*.

## 2-D arrays: rows and columns

AI data is usually a **table**: one row per example, one column per feature.

```python
# columns: size_m2, bedrooms, age_years  (three houses)
houses = np.array([
    [120, 3, 10],
    [80, 2, 25],
    [200, 4, 3],
])
print(houses.shape)          # (3, 3) -> 3 rows, 3 columns
print(houses[0])             # first house
print(houses[:, 0])          # the size column
print(houses.mean(axis=0))   # average of each column
```

`axis=0` means *"go down the rows"* (one answer per column); `axis=1` means *"go across the columns"* (one answer per row).

## Random numbers for simulations

```python
rng = np.random.default_rng(42)          # a seeded random generator
dice = rng.integers(1, 7, size=10000)     # roll a die 10,000 times
print(dice.mean())                         # close to 3.5
heights = rng.normal(165, 8, size=1000)   # 1,000 simulated heights in cm
print(heights.mean().round(1), heights.std().round(1))
```

Simulation with random numbers is a powerful way to understand probability (Week 3).

## Key terms

- **Array** — a NumPy grid of numbers of one type.
- **Vectorisation** — doing an operation on a whole array at once, without a loop.
- **Shape** — the size of each dimension, e.g. `(3, 3)`.
- **Boolean indexing** — selecting elements with a True/False array.
- **axis** — the direction of a calculation: `axis=0` down columns, `axis=1` across rows.

**Takeaway:** NumPy arrays let you do maths on thousands of numbers in one line. Learn shape, vectorised maths, boolean filtering and `axis` — they appear in every AI library.

## Try it yourself

1. Create an array of 7 daily temperatures in Kigali (invent them). Print the mean, the highest and how many days were above 26 °C.
2. Convert the temperatures to Fahrenheit in one line (`F = C × 9/5 + 32`).
3. Make a 2-D array with the marks of 4 students in 3 subjects. Print each subject's average (`axis=0`) and each student's average (`axis=1`).
4. Simulate 10,000 coin flips with `rng.integers(0, 2, 10000)` and print the share of heads.
""",
            "quiz": [
                ("What is vectorisation?",
                 ["Drawing arrows", "Doing an operation on a whole array at once, without a Python loop", "Converting text to numbers", "Saving a file"],
                 1, "NumPy applies the operation to every element in fast compiled code."),
                ("What does `np.array([1, 2, 3]) * 2` give?",
                 ["[1, 2, 3, 1, 2, 3]", "[2, 4, 6]", "12", "An error"],
                 1, "Arrays multiply element by element; lists would repeat instead."),
                ("An array has shape (3, 4). What does that mean?",
                 ["3 rows and 4 columns", "4 rows and 3 columns", "12 rows", "3 numbers"],
                 0, "Shape lists rows first, then columns."),
                ("What does `totals[totals > 8000]` return?",
                 ["True/False values", "Only the elements greater than 8000", "The number 8000", "The positions of big values"],
                 1, "Boolean indexing keeps the elements where the condition is True."),
                ("In a 2-D table of features, what does `.mean(axis=0)` give?",
                 ["The mean of each column", "The mean of each row", "One overall number", "The shape"],
                 0, "axis=0 goes down the rows, giving one mean per column (feature)."),
                ("Why use `np.random.default_rng(42)`?",
                 ["To get truly unpredictable numbers every time", "To create a seeded generator so results can be repeated", "To round numbers", "To sort arrays"],
                 1, "A seed makes simulations reproducible."),
            ],
        },
        # ------------------------------------------------------------------ 8
        {
            "title": "Pandas: Tables of Data",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=ZyhVh-qRZPA",
            "content": r"""
**Learning objective:** Load data into a Pandas DataFrame, inspect it, select columns and rows, filter, sort and create new columns.

## A DataFrame is a table

**Pandas** is like Excel inside Python. Its main object, the **DataFrame**, is a table with named columns. Each column is a **Series**.

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Aline", "Eric", "Grace", "Jean"],
    "district": ["Gasabo", "Huye", "Gasabo", "Musanze"],
    "mark": [78, 54, 91, 66],
})
print(df)
```

## The data for this week

This week we use 200 sales from an invented Kigali shop. Run this setup cell at the start of every Week 2 lesson:

{SHOP}

The data is **simulated**: it looks realistic, and everyone gets the same numbers.

## Look before you touch

Always inspect new data first:

```python
print(sales.head())        # first 5 rows
print(sales.shape)         # (rows, columns)
sales.info()               # column names, types, missing values
print(sales.describe())    # count, mean, min, max of number columns
```

To read a real file you would use `pd.read_csv("file.csv")` or `pd.read_excel("file.xlsx")`. In Colab, upload the file with the folder icon first.

## Selecting columns and rows

```python
print(sales["product"].head())                  # one column (a Series)
print(sales[["product", "total"]].head())       # several columns
print(sales.loc[0])                              # row with label 0
print(sales.iloc[:3])                            # first 3 rows by position
```

## Filtering rows

```python
momo = sales[sales["payment"] == "MoMo"]
print(len(momo))

big_rice = sales[(sales["product"] == "Rice 5kg") & (sales["quantity"] >= 5)]
print(big_rice.head())

kigali_east = sales[sales["district"].isin(["Gasabo", "Kicukiro"])]
```

Use `&` for "and" and `|` for "or", with **brackets around each condition**.

## Sorting

```python
top = sales.sort_values("total", ascending=False).head(5)
print(top[["date", "product", "quantity", "total"]])
```

## New columns

```python
sales["total_with_vat"] = (sales["total"] * 1.18).round()
sales["month"] = sales["date"].dt.month
sales["big_sale"] = sales["total"] >= 20000
print(sales.head())
```

Each new column is calculated for all 200 rows at once — vectorised, like NumPy.

## Quick counts

```python
print(sales["payment"].value_counts())
print(sales["product"].value_counts(normalize=True).round(2))   # shares
print(sales["total"].sum())
```

## Key terms

- **DataFrame** — a Pandas table with named columns.
- **Series** — one column of a DataFrame.
- **head / info / describe** — the first three things to run on new data.
- **loc / iloc** — select rows by label / by position.
- **Filter** — keep rows that meet a condition, e.g. `df[df["mark"] >= 50]`.
- **value_counts** — count how often each value appears.

**Takeaway:** Load data into a DataFrame, inspect it with head, info and describe, then select, filter, sort and add columns. These few commands cover most everyday data work.

## Try it yourself

Using the `sales` DataFrame:

1. How many sales were paid by Card?
2. Show the 5 smallest sales by `total`.
3. Create a column `price_band` that is `"high"` when `unit_price` ≥ 3000 and `"low"` otherwise. (Hint: `np.where(condition, "high", "low")`.)
4. What share of all sales happened in Nyarugenge?
""".replace("{SHOP}", SHOP_DATA),
            "quiz": [
                ("What is a Pandas DataFrame?",
                 ["A picture frame", "A table of data with named columns", "A type of loop", "A chart"],
                 1, "A DataFrame is a table; each column is a Series."),
                ("Which command shows the column types and missing values?",
                 ["df.head()", "df.info()", "df.sort_values()", "df.plot()"],
                 1, "info() lists each column's type and how many non-missing values it has."),
                ("How do you keep only rows where payment is MoMo?",
                 ["sales[\"MoMo\"]", "sales[sales[\"payment\"] == \"MoMo\"]", "sales.MoMo()", "sales.loc[\"MoMo\"]"],
                 1, "Put a True/False condition inside the brackets to filter rows."),
                ("How do you combine two filter conditions with 'and' in Pandas?",
                 ["Use the word and", "Use & with brackets around each condition", "Use +", "Use a comma"],
                 1, "Pandas needs & (and) or | (or), with each condition in brackets."),
                ("What does `sales[\"payment\"].value_counts()` show?",
                 ["The total income", "How many sales used each payment method", "The first 5 rows", "The column type"],
                 1, "value_counts counts how often each value appears."),
                ("What does `sales.sort_values(\"total\", ascending=False).head(5)` give?",
                 ["The 5 smallest sales", "The 5 largest sales", "5 random sales", "The first 5 rows unsorted"],
                 1, "Sorting descending puts the largest totals first; head(5) keeps five."),
            ],
        },
        # ------------------------------------------------------------------ 9
        {
            "title": "Cleaning Messy Data",
            "minutes": 50,
            "video": "https://www.youtube.com/watch?v=iYie42M1ZyU",
            "content": r"""
**Learning objective:** Find and fix the most common data problems — missing values, duplicates, wrong types, messy text and impossible values — and document what you changed.

## Real data is always messy

Data typed by people, exported from systems or joined from several sources is never perfect. Data scientists often spend more time **cleaning** data than modelling it. A model trained on dirty data learns dirty patterns.

## A messy dataset

Run this cell. It builds a small file the way it might arrive from a shop's records:

```python
import numpy as np
import pandas as pd

raw = pd.DataFrame({
    "date": ["2026-03-01", "2026-03-01", "2026-03-02", "2026-03-02", "2026-03-03",
             "2026-03-03", "2026-03-04", "not recorded", "2026-03-05", "2026-03-05"],
    "district": ["Gasabo", "gasabo ", "Kicukiro", "KICUKIRO", "Nyarugenge",
                 "Gasabo", None, "Kicukiro", "Nyarugenge", "Nyarugenge"],
    "product": ["Rice 5kg", "Rice 5kg", "Milk 1L", "Sugar 1kg", "Milk 1L",
                "Airtime 1000", "Milk 1L", "Rice 5kg", "Sugar 1kg", "Sugar 1kg"],
    "quantity": ["4", "4", "6", "two", "3", "5", "2", "1", "-3", "2"],
    "unit_price": [7500, 7500, 800, 1600, 800, 1000, 800, 7500, 1600, None],
})
print(raw)
```

## Step 1 — Inspect

```python
raw.info()
print(raw.isna().sum())          # missing values per column
print(raw["district"].unique())  # spelling variants
```

## Step 2 — Remove exact duplicates

```python
print(raw.duplicated().sum())    # 0: the copies only match after cleaning
df = raw.copy()
df["district"] = df["district"].str.strip().str.title()   # fix text first
df = df.drop_duplicates()
print(len(raw), "->", len(df))
```

Clean the text **before** dropping duplicates: `"Gasabo"` and `"gasabo "` only look the same after cleaning.

## Step 3 — Fix types

```python
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df.info()
```

`errors="coerce"` turns values that cannot be converted (`"two"`, `"not recorded"`) into **missing** (`NaN` / `NaT`) instead of crashing. Now you can decide what to do with them.

## Step 4 — Impossible values

```python
print(df[df["quantity"] <= 0])
df.loc[df["quantity"] <= 0, "quantity"] = np.nan    # a sale cannot be negative
```

Ask: *is this value possible in the real world?* Negative quantities, ages of 340, or prices of 0 for paid items are errors.

## Step 5 — Handle missing values

There is no single right answer. Options:

| Option | Code | When it makes sense |
|---|---|---|
| Drop the rows | `df.dropna(subset=["quantity"])` | Few rows affected, and the value is essential |
| Fill with a fixed value | `df["district"].fillna("Unknown")` | Categories, where "unknown" is honest |
| Fill from known facts | look up the product's price | The correct value can be recovered |
| Fill with mean/median | `df["x"].fillna(df["x"].median())` | Numbers, when few are missing — use with care |

```python
prices = {"Rice 5kg": 7500, "Milk 1L": 800, "Sugar 1kg": 1600, "Airtime 1000": 1000}
df["unit_price"] = df["unit_price"].fillna(df["product"].map(prices))
df["district"] = df["district"].fillna("Unknown")
df = df.dropna(subset=["quantity", "date"])
df["quantity"] = df["quantity"].astype(int)
df["total"] = df["quantity"] * df["unit_price"]
print(df)
```

## Step 6 — Write a cleaning log

Professionals record every change, so others can check and repeat it:

```text
- Standardised district names (strip spaces, Title Case): 2 values changed
- Removed 1 exact duplicate row
- quantity "two" and date "not recorded" could not be read -> rows dropped (2)
- quantity -3 is impossible -> row dropped (1)
- 1 missing unit_price filled from the official price list
- 1 missing district set to "Unknown"
```

## Key terms

- **Missing value (NaN)** — an empty cell; `isna()` finds them.
- **Duplicate** — a row that appears more than once.
- **Type conversion** — e.g. `pd.to_numeric`, `pd.to_datetime`.
- **coerce** — turn unreadable values into missing instead of failing.
- **Imputation** — filling missing values with an estimate.
- **Cleaning log** — a written record of every cleaning step.

**Takeaway:** Inspect, standardise text, remove duplicates, fix types, remove impossible values, handle missing values thoughtfully — and write down every step.

## Try it yourself

1. Run all the steps and check that the final table has no missing values (`df.isna().sum()`).
2. Change one decision: instead of dropping the row with quantity `"two"`, set it to 2. How does the total income change?
3. Write your own cleaning log for your version, in plain sentences.
""",
            "quiz": [
                ("Why clean district text before removing duplicates?",
                 ["It makes the file smaller", "Rows like 'Gasabo' and 'gasabo ' only match after cleaning", "Duplicates cannot be removed otherwise", "Pandas requires it"],
                 1, "Standardising text first lets drop_duplicates see that the rows are the same."),
                ("What does `pd.to_numeric(col, errors=\"coerce\")` do with the text 'two'?",
                 ["Converts it to 2", "Turns it into a missing value (NaN)", "Crashes the program", "Deletes the column"],
                 1, "coerce turns values that cannot be converted into NaN, so you can decide what to do."),
                ("A sale has quantity -3. What should you do?",
                 ["Keep it — all data is correct", "Treat it as an impossible value: fix it if possible, otherwise remove it", "Multiply all quantities by -1", "Ignore the whole dataset"],
                 1, "Values that cannot happen in the real world are errors."),
                ("Which method counts missing values in each column?",
                 ["df.count_na()", "df.isna().sum()", "df.missing()", "df.describe()"],
                 1, "isna() marks missing cells; sum() counts them per column."),
                ("When is filling a missing category with 'Unknown' a good choice?",
                 ["When the true value cannot be recovered and honesty matters", "Always for numbers", "Never", "Only for dates"],
                 0, "'Unknown' keeps the row while being honest about the gap."),
                ("Why write a cleaning log?",
                 ["To make the notebook longer", "So others can check and repeat every change made to the data", "Because Pandas needs it", "To hide mistakes"],
                 1, "Documented cleaning is transparent and reproducible."),
            ],
        },
        # ------------------------------------------------------------------ 10
        {
            "title": "Grouping and Summarising Data",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=tRKeLrwfUgU",
            "content": r"""
**Learning objective:** Answer business questions with `groupby`, aggregation functions and pivot tables, and combine tables with `merge`.

## From rows to answers

200 rows of sales do not answer a manager's questions. Questions like *"Which district earns most?"* or *"How does MoMo use change by month?"* need **summaries**. Pandas does this with **split → apply → combine**:

1. **Split** the rows into groups (e.g. by district).
2. **Apply** a calculation to each group (e.g. sum of totals).
3. **Combine** the results into a new table.

Run the setup cell first:

{SHOP}

## groupby

```python
by_district = sales.groupby("district")["total"].sum()
print(by_district)
print(by_district.sort_values(ascending=False))
```

Several measures at once with `agg`:

```python
summary = sales.groupby("product").agg(
    sales_count=("total", "size"),
    units=("quantity", "sum"),
    income=("total", "sum"),
    average_sale=("total", "mean"),
).round(0)
print(summary.sort_values("income", ascending=False))
```

Common aggregation functions: `sum`, `mean`, `median`, `min`, `max`, `count`, `size`, `nunique`.

## Grouping by more than one column

```python
sales["month"] = sales["date"].dt.month
monthly = sales.groupby(["month", "payment"])["total"].sum().unstack()
print(monthly)
```

`unstack()` turns the second group level into columns — a quick way to make a readable table.

## Pivot tables

If you know Excel pivot tables, Pandas has the same tool:

```python
pivot = sales.pivot_table(index="district", columns="payment",
                          values="total", aggfunc="sum", margins=True)
print(pivot)
```

`margins=True` adds an **All** row and column with totals.

## Shares and percentages

```python
share = (sales.groupby("payment")["total"].sum() / sales["total"].sum() * 100).round(1)
print(share)
```

## Combining tables with merge

Data often lives in separate tables. A **merge** joins them on a shared column:

```python
managers = pd.DataFrame({
    "district": ["Gasabo", "Kicukiro", "Nyarugenge"],
    "manager": ["Aline", "Eric", "Grace"],
})
report = by_district.reset_index().merge(managers, on="district")
print(report)
```

This is the same idea as `VLOOKUP` in Excel, or a `JOIN` in SQL.

## Asking good questions

A summary is only useful if it answers a real question. Before grouping, write the question in one sentence:

- *Which product brings the most income?* → group by product, sum total.
- *Do Card customers spend more per sale?* → group by payment, mean total.
- *Is business growing?* → group by month, sum total.

## Key terms

- **groupby** — split rows into groups by a column.
- **Aggregation** — a calculation that turns many values into one (sum, mean…).
- **agg** — apply several named aggregations at once.
- **Pivot table** — a grid summary with groups in rows and columns.
- **merge** — join two tables on a shared column.

**Takeaway:** Write the question first, then group, aggregate and combine. groupby, agg, pivot_table and merge turn raw rows into answers a manager can use.

## Try it yourself

1. Which month had the highest income? Which had the lowest?
2. What is the average sale amount for each payment method? Do Card customers spend more?
3. Make a pivot table of units sold: products in rows, districts in columns.
4. Write three sentences a shop manager could act on, based on your results.
""".replace("{SHOP}", SHOP_DATA),
            "quiz": [
                ("What are the three steps of groupby?",
                 ["Load, save, print", "Split, apply, combine", "Sort, filter, plot", "Clean, train, test"],
                 1, "Rows are split into groups, a calculation is applied to each, and the results are combined."),
                ("Which code gives total income per district?",
                 ["sales[\"district\"].sum()", "sales.groupby(\"district\")[\"total\"].sum()", "sales.sum(\"district\")", "sales.sort_values(\"district\")"],
                 1, "Group by district, select the total column, then sum."),
                ("What does `agg(units=(\"quantity\", \"sum\"))` create?",
                 ["A column named units with the sum of quantity for each group", "A new file", "A chart", "An error"],
                 0, "Named aggregation creates a column with the chosen calculation."),
                ("What does `margins=True` add to a pivot table?",
                 ["Colours", "Total rows and columns (All)", "Missing values", "A title"],
                 1, "Margins add overall totals."),
                ("What does `merge` do?",
                 ["Deletes duplicate columns", "Joins two tables using a shared column", "Sorts a table", "Splits a table in two"],
                 1, "merge works like VLOOKUP or a SQL JOIN."),
                ("What should you do before writing a groupby?",
                 ["Write the business question in one sentence", "Delete half the data", "Draw a chart", "Nothing"],
                 0, "A clear question tells you what to group by and what to calculate."),
            ],
        },
        # ------------------------------------------------------------------ 11
        {
            "title": "Charts with Matplotlib",
            "minutes": 45,
            "video": "https://www.youtube.com/watch?v=a9UrKTVEeZA",
            "content": r"""
**Learning objective:** Choose the right chart for a question, draw line, bar, histogram and scatter charts with Matplotlib, and label them so anyone can read them.

## Pick the chart from the question

| Question | Chart |
|---|---|
| How does a value change over time? | **Line** chart |
| How do categories compare? | **Bar** chart |
| How are values spread out? | **Histogram** |
| Are two numbers related? | **Scatter** plot |

Pie charts are hard to read when there are more than 2–3 slices; a bar chart is almost always clearer.

Run the setup cell first:

{SHOP}

```python
import matplotlib.pyplot as plt
```

## Line chart — change over time

```python
monthly = sales.groupby(sales["date"].dt.month)["total"].sum()

plt.figure(figsize=(8, 4))
plt.plot(monthly.index, monthly.values, marker="o")
plt.title("Monthly income, January–June 2026")
plt.xlabel("Month")
plt.ylabel("Income (RWF)")
plt.grid(alpha=0.3)
plt.show()
```

## Bar chart — compare categories

```python
by_product = sales.groupby("product")["total"].sum().sort_values()

plt.figure(figsize=(8, 4))
plt.barh(by_product.index, by_product.values, color="#1f8a9e")
plt.title("Income by product")
plt.xlabel("Income (RWF)")
plt.tight_layout()
plt.show()
```

Horizontal bars (`barh`) make long labels easy to read. Sorting the bars makes the ranking obvious.

## Histogram — the spread of values

```python
plt.figure(figsize=(8, 4))
plt.hist(sales["total"], bins=20, color="#7c5cbf", edgecolor="white")
plt.title("How big are our sales?")
plt.xlabel("Sale total (RWF)")
plt.ylabel("Number of sales")
plt.show()
```

A histogram puts values into **bins** and counts how many fall in each. It shows whether most sales are small, whether there are a few very big ones, and where the middle is.

## Scatter plot — relationships

```python
plt.figure(figsize=(6, 4))
plt.scatter(sales["quantity"], sales["total"], alpha=0.5)
plt.title("Quantity vs sale total")
plt.xlabel("Quantity")
plt.ylabel("Total (RWF)")
plt.show()
```

Scatter plots are how you first spot patterns that a model could learn (Week 4).

## Several charts together

```python
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
sales["payment"].value_counts().plot(kind="bar", ax=axes[0], title="Sales by payment")
sales.groupby("district")["total"].mean().plot(kind="bar", ax=axes[1], title="Average sale by district")
plt.tight_layout()
plt.show()
```

Pandas columns have a built-in `.plot()` that uses Matplotlib underneath.

## Save a chart

```python
plt.figure(figsize=(8, 4))
plt.plot(monthly.index, monthly.values, marker="o")
plt.title("Monthly income")
plt.savefig("monthly_income.png", dpi=150, bbox_inches="tight")
```

Download it from the Colab folder to use in a report or slide.

## Rules for honest, clear charts

1. A **title** that says what the chart shows.
2. **Axis labels with units** (RWF, %, km).
3. Bar charts start at **zero** — a cut axis exaggerates differences.
4. One message per chart.
5. Mention the data source and period.

## Key terms

- **Line / bar / histogram / scatter** — the four core chart types.
- **Bins** — the ranges a histogram counts values into.
- **Figure / axes** — the whole picture / one chart inside it.
- **subplots** — several charts in one figure.
- **savefig** — save a chart as an image file.

**Takeaway:** Choose the chart from the question: line for time, bar for comparison, histogram for spread, scatter for relationships. Always add a title, axis labels and units.

## Try it yourself

1. Draw a bar chart of the number of sales per district.
2. Draw a line chart of monthly MoMo income and monthly Cash income on the same axes (call `plt.plot` twice and add `plt.legend()`).
3. Draw a histogram of `quantity`. What is the most common quantity?
4. Save your best chart as a PNG and write a one-sentence caption for it.
""".replace("{SHOP}", SHOP_DATA),
            "quiz": [
                ("Which chart shows how income changes month by month?",
                 ["Pie chart", "Line chart", "Histogram", "Scatter plot"],
                 1, "Line charts show change over time."),
                ("Which chart shows how sale amounts are spread out?",
                 ["Histogram", "Line chart", "Pie chart", "Table"],
                 0, "A histogram counts values in bins to show their distribution."),
                ("Which chart helps you see if two numbers are related?",
                 ["Bar chart", "Scatter plot", "Pie chart", "Histogram"],
                 1, "Scatter plots show one variable against another."),
                ("Why should a bar chart start at zero?",
                 ["It looks nicer", "Cutting the axis exaggerates differences and can mislead", "Matplotlib needs it", "It does not matter"],
                 1, "Bar length shows size; a cut axis makes small differences look big."),
                ("What does `plt.savefig(\"chart.png\")` do?",
                 ["Deletes the chart", "Saves the chart as an image file", "Prints the data", "Changes colours"],
                 1, "savefig writes the current figure to a file."),
                ("Which is NOT one of the rules for a clear chart?",
                 ["A title", "Axis labels with units", "As many messages as possible in one chart", "Mention the data source"],
                 2, "One clear message per chart is easier to read."),
            ],
        },
        # ------------------------------------------------------------------ 12
        {
            "title": "Week 2 Project: Explore a Dataset",
            "minutes": 75,
            "video": "https://www.youtube.com/watch?v=r-uOLxNrNk8",
            "content": r"""
**Learning objective:** Carry out a complete exploratory data analysis (EDA): load, inspect, clean, summarise and chart a dataset, then report three findings in plain language.

## The dataset: moto taxi trips in Kigali

You are an analyst for a (fictional) moto-taxi company. It wants to understand its trips before building a fare-prediction model in Week 4. The data is **simulated** for practice — realistic, but invented. Run this cell:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
n = 300
distance = rng.uniform(1, 15, n).round(1)
rain = rng.random(n) < 0.25
hour = rng.integers(6, 23, n)
fare = (400 + 230 * distance + np.where(rain, 300, 0) + rng.normal(0, 150, n)).round(-1)
minutes = (distance * 2.8 + rng.normal(0, 3, n) + np.where(rain, 4, 0)).clip(3).round()
trips = pd.DataFrame({
    "distance_km": distance,
    "minutes": minutes,
    "fare_rwf": fare,
    "hour": hour,
    "raining": rain,
    "district": rng.choice(["Gasabo", "Kicukiro", "Nyarugenge"], size=n),
})
# a few realistic data problems
trips.loc[[5, 77, 140], "fare_rwf"] = np.nan
trips.loc[200, "distance_km"] = 150.0
trips = pd.concat([trips, trips.iloc[[10, 11]]], ignore_index=True)
```

## Part 1 — Inspect (Lesson 8)

Run `head()`, `shape`, `info()` and `describe()`. Write down: how many trips, which columns, which types, and anything that looks strange.

## Part 2 — Clean (Lesson 9)

Find and handle:
- the duplicate rows,
- the missing fares,
- the impossible distance.

Write a short cleaning log (what you changed and why).

## Part 3 — Summarise (Lesson 10)

Answer with code:
1. What is the average fare and the average distance?
2. How much more is the average fare when it is raining?
3. Which district has the longest average trip?
4. Which hours of the day are busiest?

## Part 4 — Chart (Lesson 11)

Make at least three clear charts, each with a title and labelled axes:
- a histogram of fares,
- a scatter plot of distance vs fare (colour rainy trips differently: `c=trips["raining"]`),
- a bar chart of trips per hour.

## Part 5 — Report

Write a half-page report for the company's manager:

- **Three findings**, each with a number (for example, *"Rainy trips cost about 300 RWF more on average."*).
- **One chart** that best supports your findings.
- **One question** the data cannot answer yet, and what data would be needed.

## Example code to get started

```python
clean = trips.drop_duplicates()
clean = clean[clean["distance_km"] <= 40]
clean = clean.dropna(subset=["fare_rwf"])
print(len(trips), "->", len(clean))
print(clean.groupby("raining")["fare_rwf"].mean().round())
```

## Checklist

- Every step has its own cell with a short text note above it.
- The cleaning log lists every change.
- Charts have titles, axis labels and units.
- Findings use simple English and real numbers from your analysis.

**Takeaway:** Exploratory data analysis is a loop of looking, cleaning, summarising and charting. It always comes before modelling — it tells you whether the data can answer the question at all.

## Try it yourself

Complete Parts 1–5 in one Colab notebook. In Week 4 you will build a model that predicts `fare_rwf` from `distance_km` using this same data, so keep your notebook.
""",
            "quiz": [
                ("What is exploratory data analysis (EDA)?",
                 ["Training a neural network", "Looking at, cleaning, summarising and charting data to understand it before modelling", "Deleting old data", "Publishing a website"],
                 1, "EDA is how you understand a dataset before building models."),
                ("A trip has distance_km = 150 inside Kigali. What is it most likely to be?",
                 ["A normal trip", "A data error (impossible value) to fix or remove", "A long-distance record to celebrate", "A missing value"],
                 1, "150 km is impossible for a city moto trip, so treat it as an error."),
                ("Which chart best shows whether fare rises with distance?",
                 ["Pie chart", "Scatter plot", "Histogram of hours", "Table of districts"],
                 1, "A scatter plot shows the relationship between two numbers."),
                ("Which code compares average fares for rainy and dry trips?",
                 ["clean[\"fare_rwf\"].sum()", "clean.groupby(\"raining\")[\"fare_rwf\"].mean()", "clean.sort_values(\"raining\")", "clean[\"raining\"].plot()"],
                 1, "Group by the raining column and take the mean fare of each group."),
                ("What makes a good finding in the report?",
                 ["A vague feeling", "A clear statement backed by a number from the analysis", "A long list of all columns", "Only a chart without words"],
                 1, "Findings should be specific and supported by evidence."),
                ("Why is EDA done before building a model?",
                 ["It is not needed", "It shows whether the data is clean and able to answer the question", "Models cannot read clean data", "To make the notebook longer"],
                 1, "Understanding the data first avoids training a model on errors."),
            ],
        },
    ],
}
