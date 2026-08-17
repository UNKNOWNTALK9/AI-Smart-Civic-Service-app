# AI Smart Civic Services — Enhanced Edition

A Python-only desktop civic complaint platform built with Tkinter, SQLite and real scikit-learn models.

## Features
- Modern responsive Tkinter GUI
- Citizen registration/login with hashed passwords
- Complaint submission and tracking
- Real TF-IDF + Logistic Regression / Naive Bayes classification
- Real ML priority prediction
- Actual confidence when probabilities are supported
- Automatic summary and department recommendation
- SQLite persistence and complaint history
- Admin complaint management
- Analytics and data-driven insights
- Model comparison and evaluation
- Optional image attachment
- Automatic model/database initialization

## Run
```bash
pip install -r requirements.txt
python main.py
```

Python 3.10+ recommended.

## Demo admin
Email: `admin@civic.local`
Password: `Admin@123`

## Dataset
`data/complaints_dataset.csv` is a synthetic dataset. Its synthetic nature must be considered when interpreting model performance.

## Architecture
GUI → Services → AI → SQLite, with AI training/evaluation kept separate from the interface.

## Limitations
The model learns only from the supplied synthetic dataset. Real deployment requires representative local data, multilingual support, monitoring, human review, privacy controls, and periodic retraining.


## UI/UX v3 Neon Motion Update
- Modern, readable Segoe UI headings (no italic/decorative fonts).
- Neon cyan/blue/purple borders and accent system.
- Animated pulsing borders on key cards.
- Animated glowing headings.
- Button hover transitions.
- Dark professional civic-service visual theme.
- Focus highlights on form fields.
- Consistent dashboard, authentication, registration and admin styling.
- Animations use standard Tkinter `after()` only; no extra GUI dependency.
