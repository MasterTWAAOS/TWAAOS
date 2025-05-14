"""Services for fetching data from external APIs using async patterns."""
import httpx
from config.settings import (
    FACULTY_ENDPOINT, 
    GROUPS_ENDPOINT, 
    ROOMS_ENDPOINT,
    FACULTY_STAFF_ENDPOINT,
    GROUP_SUBJECTS_ENDPOINT,
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

async def fetch_group_subjects(group_id):
    """Fetch subject data for a specific group from USV API
    
    Args:
        group_id (str): The ID of the group to fetch subjects for
        
    Returns:
        list: The list of subjects for the group
    """
    logger.info(f"Fetching subjects for group ID {group_id} from USV API")
    endpoint = GROUP_SUBJECTS_ENDPOINT.format(group_id=group_id)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(endpoint, timeout=60)  # Longer timeout for subject data
            response.raise_for_status()
            data = response.json()
            
            # The API returns a list where the first element is the array of subjects
            # and the second element is a dictionary mapping activity IDs to group names
            if data and isinstance(data, list) and len(data) > 0:
                return data
            return [[], {}]  # Return empty data structure if no data
            
        except Exception as e:
            logger.error(f"Error fetching subjects for group {group_id}: {str(e)}")
            return [[], {}]  # Return empty data structure on error
