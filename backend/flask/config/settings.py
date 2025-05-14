"""Configuration settings for the Flask application."""
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API endpoints
FACULTY_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/facultati.php?json"
GROUPS_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/subgrupe.php?json"
ROOMS_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/sali.php?json"
FACULTY_STAFF_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/cadre.php?json"
GROUP_SUBJECTS_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/orarSPG.php?ID={group_id}&mod=grupa&json"

# FastAPI service URL
FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://localhost:8000")

# Target faculty name to filter by
TARGET_FACULTY_NAME = "Facultatea de Inginerie Electrică şi Ştiinţa Calculatoarelor"
