"""Services for fetching data from external APIs."""
import requests
from config.settings import (
    FACULTY_ENDPOINT, 
    GROUPS_ENDPOINT, 
    ROOMS_ENDPOINT,
    FACULTY_STAFF_ENDPOINT,
    logger
)

def fetch_faculties():
    """Fetch faculty data from USV API"""
    logger.info("Fetching faculties from USV API")
    response = requests.get(FACULTY_ENDPOINT)
    response.raise_for_status()  # Raise exception for 4XX/5XX responses
    return response.json()

def fetch_groups():
    """Fetch group data from USV API"""
    logger.info("Fetching groups from USV API")
    response = requests.get(GROUPS_ENDPOINT)
    response.raise_for_status()  # Raise exception for 4XX/5XX responses
    return response.json()

def fetch_rooms():
    """Fetch room data from USV API"""
    logger.info("Fetching rooms from USV API")
    response = requests.get(ROOMS_ENDPOINT)
    response.raise_for_status()  # Raise exception for 4XX/5XX responses
    return response.json()

def fetch_faculty_staff():
    """Fetch faculty staff data from USV API"""
    logger.info("Fetching faculty staff from USV API")
    response = requests.get(FACULTY_STAFF_ENDPOINT)
    response.raise_for_status()  # Raise exception for 4XX/5XX responses
    return response.json()
