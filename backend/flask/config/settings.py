"""Configuration settings for the Flask application."""
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s: %(levelname)s: %(message)s',
)
logger = logging.getLogger("config.settings")

# Create a faculty skipping logger that outputs to a file
skipped_faculty_logger = logging.getLogger("skipped_faculty")
skipped_faculty_logger.setLevel(logging.INFO)

# Create a file handler for the faculty skipping logs
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)  # Create logs directory if it doesn't exist
faculty_log_file = os.path.join(log_dir, 'skipped_faculty.log')

# Create and configure file handler
file_handler = logging.FileHandler(faculty_log_file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add handler to logger
skipped_faculty_logger.addHandler(file_handler)

# Make sure skipped_faculty_logger doesn't propagate to root logger
skipped_faculty_logger.propagate = False

# API endpoints
FACULTY_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/facultati.php?json"
GROUPS_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/subgrupe.php?json"
ROOMS_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/sali.php?json"
FACULTY_STAFF_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/cadre.php?json"
GROUP_SUBJECTS_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/orarSPG.php?ID={group_id}&mod=grupa&json"

# FastAPI service URL
FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://localhost:8000")

# Define target faculties to include in synchronization
TARGET_FACULTIES = [
    "Facultatea de Inginerie Electrică şi Ştiinţa Calculatoarelor",  # FIESC
    "Facultatea de Ştiinţe ale Educaţiei",                          # PEDA
    "Facultatea de Economie, Administrație și Afaceri",               # FEAA
    "Facultatea de Silvicultură",                                    # FIS
    "Departamentul de Specialitate cu Profil Psihopedagogic",
    "Facultatea de Medicină și Științe Biologice",
    "Facultatea de Inginerie Mecanică, Autovehicule şi Robotică",
    "Facultatea de Inginerie Alimentară"
]

# Special departments that should always be included regardless of faculty
SPECIAL_DEPARTMENTS = ["Exterior"]

