"""
Deep Learning & Neural Networks -- full 4-week course (24 lessons, about 22 hours).

Original WAMUGII TECH SOLUTIONS content. Load or update it with:

    docker exec wamugii-backend python -m app.seed_course_content deep_learning_neural_networks

It replaces the short 9-lesson version created by seed_ai_c4_deep_learning.py:
the old lessons are hidden, students keep their enrolment.
"""

from app.course_content.dl_exam import EXAM
from app.course_content.dl_week1 import WEEK1
from app.course_content.dl_week2 import WEEK2
from app.course_content.dl_week3 import WEEK3
from app.course_content.dl_week4 import WEEK4
from app.course_content.lectures import attach

COURSE = {
    "slug": "deep-learning-neural-networks",
    "title": "Deep Learning & Neural Networks",
    "category": "Artificial Intelligence",
    "display_order": 5,
    "is_free": True,
    "description": (
        "A complete 4-week, hands-on course in deep learning with Python and PyTorch — "
        "explained in simple English, with every line of code tested. Week 1: neurons, "
        "activations, loss, gradient descent and backpropagation — you build a network from "
        "scratch, then with PyTorch autograd. Week 2: training deep networks well — nn.Module, "
        "optimisers (SGD, momentum, Adam), dropout, weight decay, early stopping, batch "
        "normalisation and DataLoaders. Week 3: computer vision with CNNs — convolutions, data "
        "augmentation, transfer learning with pretrained ResNets, and how to trust image models. "
        "Week 4: embeddings, LSTMs, attention and transformers, autoencoders and generative "
        "models, and deploying models responsibly behind an API.\n\n"
        "Free in Google Colab, with a free GPU — nothing to install. 24 lessons, each with a "
        "short video, full lectures to go deeper, notes with ready-to-run code, a downloadable "
        "handout and a quiz, plus a project every week, a final exam and a certificate. Built "
        "by WAMUGII TECH SOLUTIONS for students and professionals in Rwanda and beyond."
    ),
    "modules": [WEEK1, WEEK2, WEEK3, WEEK4],
    # Final exam: these questions plus every lesson-quiz question (as single answer).
    "exam": EXAM,
}

# "Go deeper" full lectures under the short videos (see lectures.py).
attach(COURSE, {
    "What Deep Learning Is — and Your First Neuron": ["mit_dl", "cs50_nn"],
    "Activation Functions and the Forward Pass": ["3b1b_nn", "mit_dl"],
    "Loss Functions and Gradient Descent": ["karpathy_micrograd", "mit_dl"],
    "Backpropagation: How Networks Learn": ["3b1b_backprop_calc", "karpathy_micrograd"],
    "PyTorch: Tensors and Autograd": ["pytorch_autograd_talk", "fcc_pytorch"],
    "Week 1 Project: Read Handwritten Digits": ["karpathy_micrograd", "fcc_pytorch"],
    "Building Models with nn.Module and the Training Loop": ["fcc_pytorch", "pytorch_image_talk"],
    "Optimisers: SGD, Momentum and Adam": ["cs50_nn", "fcc_pytorch"],
    "Overfitting: Dropout, Weight Decay and Early Stopping": ["mit_dl"],
    "Initialisation, Batch Norm and Vanishing Gradients": ["karpathy_micrograd", "mit_dl"],
    "Datasets, DataLoaders and Tabular Data": ["pytorch_image_talk"],
    "Week 2 Project: A Neural Network for Loan Risk": ["mit_dl", "pytorch2_talk"],
    "Images as Numbers and Convolutions": ["mit_cnn_2024", "cs50_nn"],
    "Building a CNN in PyTorch": ["computerphile_cnn", "keras_cnn_talk"],
    "Data Augmentation: More Data for Free": ["mit_cnn_2023", "fcc_pytorch"],
    "Transfer Learning: Standing on Big Models": ["mit_cnn_2024", "fcc_pytorch"],
    "Understanding and Trusting Image Models": ["cc_bias", "mit_wild_2024"],
    "Week 3 Project: An Image Classifier from Folders": ["pytorch_image_talk", "fcc_pytorch"],
    "Text as Numbers: Tokens and Embeddings": ["embeddings_talk", "cs50_language"],
    "Recurrent Networks and LSTMs for Sequences": ["mit_rnn_2024", "rnn_talk", "conv1d_ts_talk"],
    "Attention and Transformers": ["karpathy_gpt", "mit_rnn_2024", "karpathy_llm"],
    "Autoencoders and Generative Models": ["gans_talk"],
    "Deploying Deep Learning Responsibly": ["deploy_nlp_talk", "pytorch2_talk", "mit_wild_2024"],
    "Final Project: A Deep-Learning System and Certificate": ["fcc_pytorch", "mit_dl"],
})
