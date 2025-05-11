"""Services for storing data in the FastAPI database."""
import requests
from config.settings import logger, FASTAPI_BASE_URL

def store_groups_in_db(groups):
    """Send groups to FastAPI endpoint for storage"""
    results = []
    success_count = 0
    error_count = 0
    
    logger.info(f"Starting to store {len(groups)} groups in database")
    
    for i, group in enumerate(groups):
        try:
            # Log the group data being sent
            if i < 3:  # Log only first 3 groups to avoid log spam
                logger.info(f"Sending group data: {group}")
                
            # Make the API request
            response = requests.post(
                f"{FASTAPI_BASE_URL}/groups", 
                json=group
            )
            response.raise_for_status()
            
            # Process successful response
            group_id = response.json().get("id")
            success_count += 1
            
            # Log success
            if i < 3:  # Log only first 3 responses to avoid log spam
                logger.info(f"Successfully created group: '{group['name']}' with ID {group_id}")
                
            results.append({
                "group": group["name"],
                "status": "success",
                "id": group_id
            })
        except Exception as e:
            error_count += 1
            error_msg = str(e)
            
            # Log the error with request details
            logger.error(f"Error creating group '{group['name']}': {error_msg}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}, Content: {e.response.text}")
                
            results.append({
                "group": group["name"],
                "status": "error",
                "message": error_msg
            })
    
    # Log summary of results
    logger.info(f"Group synchronization completed: {success_count} succeeded, {error_count} failed")
    
    return results

def store_rooms_in_db(rooms):
    """Send rooms to FastAPI endpoint for storage"""
    results = []
    success_count = 0
    error_count = 0
    
    logger.info(f"Starting to store {len(rooms)} rooms in database")
    
    for i, room in enumerate(rooms):
        try:
            # Log the room data being sent
            if i < 3:  # Log only first 3 rooms to avoid log spam
                logger.info(f"Sending room data: {room}")
                
            # Make the API request
            response = requests.post(
                f"{FASTAPI_BASE_URL}/rooms", 
                json=room
            )
            response.raise_for_status()
            
            # Process successful response
            room_id = response.json().get("id")
            success_count += 1
            
            # Log success
            if i < 3:  # Log only first 3 responses to avoid log spam
                logger.info(f"Successfully created room: '{room['name']}' with ID {room_id}")
                
            results.append({
                "room": room["name"],
                "status": "success",
                "id": room_id
            })
        except Exception as e:
            error_count += 1
            error_msg = str(e)
            
            # Log the error with request details
            logger.error(f"Error creating room '{room['name']}': {error_msg}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}, Content: {e.response.text}")
                
            results.append({
                "room": room["name"],
                "status": "error",
                "message": error_msg
            })
    
    # Log summary of results
    logger.info(f"Room synchronization completed: {success_count} succeeded, {error_count} failed")
    
    return results

def store_faculty_staff_in_db(staff):
    """Send faculty staff to FastAPI endpoint for storage"""
    results = []
    success_count = 0
    error_count = 0
    
    logger.info(f"Starting to store {len(staff)} faculty staff in database")
    
    for i, user in enumerate(staff):
        try:
            # Log the user data being sent
            if i < 3:  # Log only first 3 users to avoid log spam
                logger.info(f"Sending user data: {user}")
                
            # Make the API request
            response = requests.post(
                f"{FASTAPI_BASE_URL}/users", 
                json=user
            )
            response.raise_for_status()
            
            # Process successful response
            user_id = response.json().get("id")
            success_count += 1
            
            # Log success
            if i < 3:  # Log only first 3 responses to avoid log spam
                logger.info(f"Successfully created user: '{user['firstName']} {user['lastName']}' with ID {user_id}")
                
            results.append({
                "user": f"{user['firstName']} {user['lastName']}",
                "status": "success",
                "id": user_id
            })
        except Exception as e:
            error_count += 1
            error_msg = str(e)
            
            # Log the error with request details
            logger.error(f"Error creating user '{user['firstName']} {user['lastName']}': {error_msg}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}, Content: {e.response.text}")
                
            results.append({
                "user": f"{user['firstName']} {user['lastName']}",
                "status": "error",
                "message": error_msg
            })
    
    # Log summary of results
    logger.info(f"Faculty staff synchronization completed: {success_count} succeeded, {error_count} failed")
    
    return results
