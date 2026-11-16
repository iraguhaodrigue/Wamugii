# "Open in Google Colab" for every coding lesson

Every lesson of the 5 coding courses now has an **Open in Colab** button. One click opens the whole lesson as a Google Colab notebook: the lesson text plus every code example, in order, ready to run. It is free, there is nothing to install, and Colab gives a free GPU for the deep-learning lessons.

## What students see

- **A bar at the top of every coding lesson:**
  "Prefer a notebook? Run this whole lesson in Google Colab" → **Open in Colab**.
- **Examples that cannot run in the browser** (PyTorch, API keys, servers) now say **"Open this lesson in Google Colab"**. That link opens the lesson's own notebook, not an empty Colab.
- **Inside each notebook:**
  - a short "How to use" note: run the cells in order, or **Runtime → Run all**; **File → Save a copy in Drive** keeps your work;
  - for GPU lessons: how to switch on the free T4 GPU;
  - for lessons that call an AI model: how to add an API key safely with Colab's **Secrets** (the key icon);
  - a link back to the course on the website, for the quiz and the certificate.

## Part 1: the notebooks repository (github.com/wamugii/notebooks)

The zip contains a folder **`wamugii-notebooks`** with:

- `README.md`: a table of all 120 lessons with an **Open in Colab** badge each (it becomes the repository's home page);
- `math-python-for-ai/lesson-01.ipynb` … `lesson-24.ipynb`, and the same for the other 4 courses (120 notebooks).

**Put them on GitHub** (the repository is still empty):

```
git clone https://github.com/wamugii/notebooks.git
cd wamugii-notebooks
# copy everything from the zip's wamugii-notebooks folder into here, then:
git add -A
git commit -m "Lesson notebooks for the WAMUGII AI Program"
git branch -M main
git push -u origin main
```

**Check it works:** open https://github.com/wamugii/notebooks. You should see the table; click any **Open in Colab** badge and the lesson opens in Colab.

The repository must stay **public** (Colab can only open public GitHub notebooks), and it must use the branch **`main`**. It contains only lesson content: no site code, keys or student data.

## Part 2: the website (the `wamugii` repository)

Apply this **after** the previous course-upgrade patch (handbook, Run Python, reviews), from the repo root:

```
git apply --3way wamugii-open-in-colab.patch
git add -A
git commit -m "feat: Open in Google Colab for every coding lesson"
git push
```

Then deploy the frontend as usual. **No backend change, no migration, no re-seed.**

Changed files:

| File | Change |
|---|---|
| `wamugii-frontend/src/lib/python/colab.ts` | **New.** Builds the Colab link for a lesson |
| `wamugii-frontend/src/components/courses/LessonContent.tsx` | The "Open in Colab" bar |
| `wamugii-frontend/src/components/courses/PythonRunner.tsx` | Colab-only examples link to the lesson notebook |
| `wamugii-frontend/src/pages/client/CoursePlayer.tsx` | Passes the lesson's Colab link |
| `wamugii-frontend/src/pages/public/CourseDetail.tsx`, `src/components/courses/CourseFaq.tsx` | Text mentions Colab |
| `wamugii-backend/scripts/course_make_notebooks.py` | **New.** Generates the notebooks from the lessons |

## When you change a lesson later

Rebuild the notebooks, then push the notebooks repository:

```
cd wamugii-backend
python scripts/course_make_notebooks.py ../../wamugii-notebooks    # path to your notebooks clone
cd ../../wamugii-notebooks && git add -A && git commit -m "Update notebooks" && git push
```

To use a different repository, set `VITE_COLAB_REPO=owner/repo` when building the frontend.

## Tested

- All 120 notebooks are valid notebook files.
- I ran every notebook from top to bottom on a computer with the same libraries as Colab (no GPU, no API keys). The results are in the table below.

| Course | Notebooks | Ran with no errors | The others, and why |
|---|---|---|---|
| Math & Python for AI | 24 | 22 | Lesson 1 shows a deliberate "missing bracket" error. Lesson 24 is the final project: the student writes Part 1 in the empty cell provided |
| Machine Learning Fundamentals | 24 | 24 | — |
| Responsible AI & Deployment | 24 | 24 | — |
| Deep Learning & Neural Networks | 24 | 22 | Lessons 16 and 18 download pretrained models from the internet (my test computer is offline; Colab is online) |
| Modern AI: LLMs & Generative AI | 24 | 9 | 15 lessons call an AI model, so they need the student's API key (added in Colab Secrets), and lesson 22 downloads a small model from the internet. The code itself runs fine |
| **Total** | **120** | **101** | All 19 others are expected, as explained above |
