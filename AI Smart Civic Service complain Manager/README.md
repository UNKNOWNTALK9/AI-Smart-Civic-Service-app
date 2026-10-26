# 🏛️ AI Smart Civic Services
## Intelligent Civic Complaint Management Platform

AI Smart Civic Services is a Python-based desktop application designed to improve how citizens submit, track, and manage civic complaints. The platform combines a modern Tkinter graphical interface, SQLite database storage, and real machine-learning models built with scikit-learn to classify complaints, predict their priority, and recommend the appropriate department.

My goal is to make civic complaint management more organized, transparent, and data-driven through automation, intelligent classification, and a user-friendly interface.

## 🚀 Key Features

### 1. Modern Desktop GUI
- Built with Python and Tkinter.
- Responsive layouts that adapt to available window space.
- Professional dark theme with neon cyan, blue, and purple accents.
- Consistent styling across authentication, registration, citizen dashboards, and admin panels.
- Animated interface elements using Tkinter's built-in `after()` method.
- Clear navigation, readable typography, and interactive form controls.

### 2. Citizen Registration and Authentication
- Citizen account registration and login.
- Password hashing instead of storing passwords as plain text.
- Account-based access to complaint submission and tracking.
- Separation between citizen and administrator functionality.

Password hashing helps protect stored credentials, but production deployment should also implement appropriate password policies, login rate limiting, secure account recovery, and session management.

### 3. Complaint Submission
Citizens can submit civic complaints through the graphical interface.

Complaint information may include:
- Complaint title and description.
- Relevant civic issue category.
- Recommended department.
- Predicted priority.
- Submission date and complaint status.
- Optional image attachment.

The exact fields depend on the implemented submission form.

### 4. Real Machine-Learning Complaint Classification
The application uses scikit-learn models to classify complaint descriptions into relevant categories.

The classification pipeline uses:

- **TF-IDF Vectorization:** Converts complaint text into numerical features based on word importance.
- **Logistic Regression:** A supervised learning model for text classification.
- **Multinomial Naive Bayes:** A probabilistic classification algorithm commonly used for text data.
- **Model Comparison:** Evaluates the implemented candidate models to compare their classification performance.

The selected model can help determine which civic issue category best matches a submitted complaint.

Possible categories depend on the labels included in the training dataset.

### 5. Machine-Learning Priority Prediction
The platform includes a separate machine-learning feature for predicting complaint priority.

Based on the available training labels and implemented pipeline, the system can estimate a priority level such as low, medium, or high.

Priority prediction can help administrators organize their workload. However, the predicted level is a recommendation rather than an official assessment of urgency. Safety-critical complaints should receive appropriate human review.

### 6. Prediction Confidence
When the selected model supports probability estimates, the application can display the model's predicted probabilities or a confidence indicator.

- Probability-based output is available only when supported by the selected model and configuration.
- Some models may require probability calibration or additional configuration.
- A high predicted probability does not guarantee that a classification is correct.
- Confidence scores should be evaluated against held-out data before being used for real civic decisions.

### 7. Automatic Complaint Summary
The application provides an automatic summary of complaint descriptions to make lengthy submissions easier to review.

The summary helps administrators understand the main issue without reading the entire complaint immediately. The summary method should be documented according to the implementation, such as extractive text processing or a separate summarization model.

### 8. Department Recommendation
Based on the predicted complaint category and the application's configured category-to-department mapping, the system recommends an appropriate department.

This can help route complaints to the correct administrative team and reduce manual sorting.

Department recommendations should remain reviewable so administrators can correct incorrect assignments.

### 9. Complaint Tracking and History
- Store complaints in an SQLite database.
- Maintain complaint records across application restarts.
- Allow citizens to review their complaint history.
- Display available complaint status information.
- Support administrator review and management of submitted complaints.

Complaint tracking improves organization and gives citizens a clearer view of the progress recorded in the system.

### 10. Administrator Dashboard
The administrative interface supports complaint oversight and management.

Depending on the implemented workflows, administrators can:
- View submitted complaints.
- Review complaint descriptions and attached images.
- Inspect predicted categories and priority levels.
- Review department recommendations.
- Manage complaint records and statuses.
- Examine complaint statistics and analytical summaries.

Administrative actions should be protected by server-side or application-level authorization checks, not simply by hiding interface elements.

### 11. Analytics and Data-Driven Insights
The application includes analytical features for understanding complaint data.

Potential insights include:
- Total number of complaints.
- Distribution of complaints by category.
- Priority-level distribution.
- Department-wise complaint counts.
- Complaint status summaries.
- Patterns in submitted complaints.

The accuracy of these insights depends on the quality, completeness, and consistency of the stored records.

### 12. Model Evaluation and Comparison
The project supports model comparison and evaluation to help assess the performance of the implemented machine-learning models.

Relevant evaluation metrics may include:
- Accuracy.
- Precision.
- Recall.
- F1-score.
- Confusion matrix.

For imbalanced complaint categories, precision, recall, and F1-score can provide more useful information than accuracy alone.

Training and evaluation are kept separate from the graphical interface to improve maintainability and avoid unnecessary model training during routine GUI operations.

### 13. Optional Image Attachments
Citizens can optionally attach images to support their complaints.

Images may help administrators understand visible civic problems, such as damaged infrastructure or waste accumulation.

Image attachments are supporting evidence only; the described text-classification models should not be represented as image-recognition models unless a separate image-analysis component is implemented.

### 14. Automatic Initialization
The application initializes the required database structures and machine-learning resources through its startup workflow.

This helps simplify initial setup and reduces the need for manual database preparation.

The exact initialization process depends on the implemented database and model-training logic.

## 🎨 UI/UX Design

The interface uses a modern dark visual theme designed for readability and a consistent experience across the application.

### Visual Design
- Dark professional civic-service theme.
- Neon cyan, blue, and purple accent colors.
- Clear, readable Segoe UI headings.
- Consistent spacing and alignment.
- High-contrast borders and interface elements.
- Structured dashboards and information cards.

### Animations and Interactions
- Animated pulsing borders on selected cards.
- Glowing heading effects.
- Button hover transitions.
- Focus highlights on input fields.
- Consistent visual feedback across login, registration, citizen, and admin screens.

Animations use Tkinter's standard `after()` scheduling mechanism and do not require an additional GUI animation dependency.

The interface should also remain usable when animations are disabled or when running on systems with limited resources.

## 🛠️ Technology Stack

### Frontend and Desktop Interface
- **Tkinter:** Desktop graphical user interface.
- **ttk:** Native themed widgets where appropriate.
- **Segoe UI:** Readable interface typography.
- **Tkinter `after()`:** Lightweight scheduled UI animations.

### Backend and Application Logic
- **Python:** Core programming language.
- **SQLite:** Persistent relational data storage.
- **Authentication module:** Registration and login handling.
- **Complaint management module:** Submission, tracking, and administrative workflows.
- **Analytics module:** Complaint statistics and data-driven insights.

### Artificial Intelligence and Machine Learning
- **scikit-learn:** Machine-learning algorithms and evaluation.
- **TF-IDF Vectorizer:** Text feature extraction.
- **Logistic Regression:** Supervised complaint classification.
- **Multinomial Naive Bayes:** Alternative text classification model.
- **Model evaluation utilities:** Performance comparison and validation.

### Data Management
- **CSV:** Storage format for the supplied synthetic training dataset.
- **SQLite:** Application records and complaint history.
- **Image files:** Optional complaint attachments.

## 🧱 System Architecture

The application separates the graphical interface, business logic, machine-learning functionality, and persistent storage.

```text
                 CITIZEN / ADMIN
                        |
                        v
                 TKINTER GUI
                        |
                        v
               APPLICATION SERVICES
                 /            \
                v              v
       COMPLAINT MANAGEMENT   ANALYTICS
                |
                v
          AI / ML SERVICES
          /      |       \
         v       v        v
       TF-IDF  PRIORITY  SUMMARY &
         |     MODEL     DEPARTMENT
         v
    CLASSIFICATION
                |
                v
           SQLITE DATABASE

     MODEL TRAINING AND EVALUATION
              SEPARATE
         FROM GUI OPERATIONS
```

This separation makes the code easier to maintain, test, and extend without placing all application logic inside the interface.

## 📋 Requirements

- Windows, Linux, or another platform supported by the installed Python and Tkinter environment.
- Python 3.10 or later recommended.
- Tkinter support.
- Packages listed in `requirements.txt`.
- The supplied complaint dataset for the initial training workflow.

## ⚙️ Installation and Setup

### Step 1: Open the project directory

Open a terminal in the folder containing `main.py` and `requirements.txt`.

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the application

```bash
python main.py
```

The application should initialize the required resources and open the desktop interface, provided that the required dependencies, dataset, and project files are available.

### Optional: Create a virtual environment

Using a virtual environment helps isolate the project's dependencies.

```bash
python -m venv .venv
```

On Windows, activate it with:

```bash
.venv\Scripts\activate
```

Then install the requirements and launch the application.

## 🔐 Demo Administrator Account

Use the following credentials to test the administrator interface:

| Field | Value |
|---|---|
| Email | `admin@civic.local` |
| Password | `Admin@123` |

These are demonstration credentials. Before real deployment, replace default accounts and ensure that credentials are securely managed.

## 📊 Dataset and Model Training

The project includes the dataset:

`data/complaints_dataset.csv`

The supplied dataset is synthetic, meaning it contains generated or simulated complaint examples rather than a fully representative collection of real local civic complaints.

This distinction is important when interpreting model evaluation results.

### Dataset Limitations
- Synthetic examples may not reflect real citizen language.
- Local spellings, abbreviations, and multilingual expressions may be underrepresented.
- Complaint categories may not reflect actual municipal workloads.
- Model scores on synthetic test data may not generalize to real submissions.

For meaningful real-world evaluation, the system needs representative local complaint data, suitable privacy protections, and a separate test dataset that was not used during training or model selection.

## ⚠️ Privacy, Security, and Responsible AI

Civic complaints may contain names, addresses, photographs, or other sensitive information.

Before deploying the platform in a real civic-service environment, I would prioritize:

- Secure password hashing and account management.
- Role-based access controls.
- Input validation and safe file-upload handling.
- Appropriate protection for complaint records and attachments.
- Data minimization and retention policies.
- Human review of predicted categories and priority levels.
- Evaluation across relevant complaint types and languages.
- Monitoring for classification errors and changing data patterns.
- Periodic retraining using approved, representative data.

Machine-learning outputs should assist civic staff rather than replace human judgment, particularly for urgent or safety-related complaints.

## ⚠️ Current Limitations

- The models learn from the supplied synthetic dataset.
- Predictions may be inaccurate for unfamiliar or ambiguous complaints.
- Confidence values are available only when supported by the selected model.
- Real-world performance has not been established solely by synthetic-data evaluation.
- Multilingual classification requires appropriate training data and evaluation.
- Automatic summaries and department recommendations depend on their implemented logic and configured mappings.
- The application is a desktop platform and does not automatically provide a public cloud service or mobile application.

## 🔮 Future Improvements

Possible future enhancements include:

- Training on representative and appropriately anonymized local civic complaint data.
- Multilingual complaint classification.
- Improved complaint summarization.
- More detailed department routing rules.
- Complaint urgency detection and escalation workflows.
- Notifications about complaint status changes.
- More comprehensive analytics dashboards.
- Model drift monitoring and periodic retraining.
- Automated tests for authentication, database operations, and AI pipelines.
- Secure deployment with backups and audit logs.
- Accessibility improvements and optional reduced-motion settings.

These improvements are potential extensions rather than claims about existing functionality.

## 🎯 Project Objective

My objective is to develop an intelligent civic complaint management platform that combines desktop application development, secure data storage, machine learning, and practical analytics.

Through this project, I aim to demonstrate how text classification and data-driven prioritization can support the organization of civic complaints while keeping administrators involved in important decisions.

## 👨‍💻 Project Information

- **Project Name:** AI Smart Civic Services
- **Category:** AI-Powered Desktop Application
- **Programming Language:** Python
- **GUI Framework:** Tkinter
- **Database:** SQLite
- **Machine-Learning Library:** scikit-learn
- **Text Processing:** TF-IDF
- **Classification Models:** Logistic Regression and Naive Bayes
- **Interface Theme:** Dark UI with neon accents
- **Primary Purpose:** Civic Complaint Management and Intelligent Classification

---

*AI Smart Civic Services is a civic technology project intended to demonstrate complaint management, machine-learning classification, and data-driven administration. Reliable real-world use requires representative data, appropriate security controls, ongoing evaluation, and human oversight.*
