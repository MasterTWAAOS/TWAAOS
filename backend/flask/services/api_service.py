"""Services for fetching data from external APIs using async patterns."""
import httpx
from config.settings import (
    FACULTY_ENDPOINT, 
    GROUPS_ENDPOINT, 
    ROOMS_ENDPOINT,
    FACULTY_STAFF_ENDPOINT,
    logger
)

async def fetch_faculties():
    """Fetch faculty data from USV API using async HTTP requests"""
    logger.info("Fetching faculties from USV API")
    async with httpx.AsyncClient() as client:
        response = await client.get(FACULTY_ENDPOINT, timeout=30)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()

async def fetch_groups():
    """Fetch group data from USV API using async HTTP requests"""
    logger.info("Fetching groups from USV API")
    async with httpx.AsyncClient() as client:
        response = await client.get(GROUPS_ENDPOINT, timeout=30)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()

async def fetch_rooms():
    """Fetch room data from USV API using async HTTP requests"""
    logger.info("Fetching rooms from USV API")
    async with httpx.AsyncClient() as client:
        response = await client.get(ROOMS_ENDPOINT, timeout=30)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()

async def fetch_faculty_staff():
    """Fetch faculty staff data from USV API using async HTTP requests"""
    logger.info("Fetching faculty staff from USV API")
    async with httpx.AsyncClient() as client:
        response = await client.get(FACULTY_STAFF_ENDPOINT, timeout=30)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
