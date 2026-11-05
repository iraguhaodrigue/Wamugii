# Course 5 – Deep Learning & Neural Networks

This update adds the full Course 5: 24 lessons over 4 weeks (about 23 hours).

- **Week 1 · Neural Networks from Scratch** – neurons, activations, loss, gradient descent,
  backpropagation by hand in NumPy, then PyTorch tensors and autograd. Project: read handwritten digits.
- **Week 2 · Training Deep Networks Well** – nn.Module and the training loop, SGD/momentum/Adam,
  dropout, weight decay, early stopping, batch norm, vanishing gradients, DataLoaders.
  Project: a neural network for loan risk compared fairly with logistic regression.
- **Week 3 · Computer Vision with CNNs** – convolutions, building a CNN, data augmentation,
  transfer learning with a pretrained ResNet, saliency maps and trusting image models.
  Project: an image classifier from folders (ImageFolder + ResNet).
- **Week 4 · Sequences, Attention and Generative Models** – tokens and embeddings, LSTM forecasting,
  attention and a small transformer, autoencoders, deploying a model behind a FastAPI endpoint.
  Final project + certificate.

Every lesson has a short video, "Go deeper" full lectures (3Blue1Brown, StatQuest, MIT 6.S191,
Andrej Karpathy, freeCodeCamp, PyCon/PyData talks), notes with ready-to-run code, a PDF handout,
a 6-question quiz, and the course has a 196-question final-exam bank.

All code was run and checked with PyTorch (CPU). The numbers in the notes are the ones the code prints.
Datasets are built into scikit-learn or made with code, so nothing needs downloading – except the
pretrained ResNet weights (about 45 MB), which Colab downloads automatically.

## Deploy

No database change this time (no new migration).

On your computer, in the repo root:

```bash
unzip -o wamugii-deep-learning-course.zip
git add -A
git commit -m "feat: full Deep Learning & Neural Networks course (Course 5)"
git push
```

On the droplet:

```bash
cd /opt/wamugii && git checkout -- wamugii-frontend/package-lock.json && git pull

# backend: the course content is inside the backend image, so rebuild it
# (use the next version number, e.g. v6 if you used v5 last time)
cd /opt/wamugii/wamugii-backend
docker build -t wamugii-backend:v6 .
docker stop wamugii-backend && docker rm wamugii-backend
docker run -d --name wamugii-backend --network host --restart unless-stopped \
  --env-file /opt/wamugii.env -v wamugii-uploads:/code/uploads \
  wamugii-backend:v6 uvicorn app.main:app --host 127.0.0.1 --port 8001

# safe to run even if already up to date
docker exec wamugii-backend alembic upgrade head

# load Course 5 (lessons, PDFs, lectures, exam bank)
docker exec wamugii-backend python -m app.seed_course_content deep_learning_neural_networks

# frontend (home page card + course page)
/opt/redeploy-wamugii.sh
```

The old short 9-lesson version of the course is hidden; students keep their enrolment.
