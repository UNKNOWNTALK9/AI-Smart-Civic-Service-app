from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "civic_services.db"
DATASET_PATH = DATA_DIR / "complaints_dataset.csv"

APP_TITLE = "AI Smart Civic Services"
WINDOW_SIZE = "1280x780"
MIN_SIZE = (1080, 680)

CATEGORIES = ["Road", "Water", "Drainage", "Waste", "Electricity", "Streetlight", "Safety", "Other"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["Open", "Assigned", "In Progress", "Resolved", "Reopened"]

DEPARTMENTS = {
    "Road": "Road & Infrastructure",
    "Water": "Water & Sanitation",
    "Drainage": "Water & Sanitation",
    "Waste": "Waste Management",
    "Electricity": "Electricity Department",
    "Streetlight": "Municipal Services",
    "Safety": "Public Safety",
    "Other": "Municipal Services",
}
