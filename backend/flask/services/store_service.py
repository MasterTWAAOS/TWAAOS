"""Services for storing data in the FastAPI database."""
import asyncio
import aiohttp
import requests  # Keep for compatibility with non-async functions
import concurrent.futures
from typing import List, Dict, Any
from config.settings import logger, FASTAPI_BASE_URL

async def process_group(session, group, index):
    """Process a single group with error handling"""
    try:
        # Log the group data being sent (only for first few)
        if index < 3:
            logger.info(f"Sending group data: {group}")
            
        # Make the API request
        async with session.post(
            f"{FASTAPI_BASE_URL}/groups", 
            json=group,
            timeout=15
        ) as response:
            response.raise_for_status()
            response_data = await response.json()
            
            # Process successful response
            group_id = response_data.get("id")
            
            # Log success (only for first few)
            if index < 3:
                logger.info(f"Successfully created group: '{group['name']}' with ID {group_id}")
                
            return {
                "group": group["name"],
                "status": "success",
                "id": group_id
            }, True  # Success flag
            
    except Exception as e:
        error_msg = str(e)
        
        # Log the error with request details
        logger.error(f"Error creating group '{group['name']}': {error_msg}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status}, Content: {await e.response.text()}")
            
        return {
            "group": group["name"],
            "status": "error",
            "message": error_msg
        }, False  # Error flag

async def store_groups_async(groups):
    """Send groups to FastAPI endpoint for storage using async"""
    results = []
    success_count = 0
    error_count = 0
    
    logger.info(f"Starting to store {len(groups)} groups in database using concurrent requests")
    
    # Process in batches to avoid overwhelming the server
    batch_size = 10
    
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(groups), batch_size):
            batch = groups[i:i+batch_size]
            batch_tasks = [process_group(session, group, i+j) for j, group in enumerate(batch)]
            batch_results = await asyncio.gather(*batch_tasks)
            
            # Process results
            for result, success in batch_results:
                results.append(result)
                if success:
                    success_count += 1
                else:
                    error_count += 1
    
    # Log summary of results
    logger.info(f"Group synchronization completed: {success_count} succeeded, {error_count} failed")
    
    return results

async def store_groups_in_db(groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Store groups in the FastAPI database via API calls.
    
    Args:
        groups (List[Dict[str, Any]]): List of group objects to store
        
    Returns:
        List[Dict[str, Any]]: Results of API calls
    """
    results = []
    success_count = 0
    error_count = 0
    
    # Use aiohttp for making HTTP calls
    async with aiohttp.ClientSession() as session:
        # Process groups sequentially to avoid concurrent database transactions
        for i, group in enumerate(groups):
            # Add a small delay between requests to avoid overwhelming the API
            if i > 0:
                await asyncio.sleep(0.1)
                
            # Process the group
            try:
                result, success = await process_group(session, group, i)
                results.append(result)
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
                # Log progress every 10 groups
                if i % 10 == 0 and i > 0:
                    logger.info(f"Processed {i}/{len(groups)} groups so far")
                    
            except Exception as e:
                logger.error(f"Unexpected error processing group {group.get('name', 'unknown')}: {str(e)}")
                results.append({
                    "group": group.get('name', 'unknown'),
                    "status": "error",
                    "message": f"Unexpected error: {str(e)}"
                })
                error_count += 1
    
    logger.info(f"Groups API results: {success_count} succeeded, {error_count} failed")
    return results

async def process_room(session, room, index):
    """Process a single room with error handling"""
    try:
        # Log the room data being sent
        if index < 3:
            logger.info(f"Sending room data: {room}")
            
        # Make the API request
        async with session.post(
            f"{FASTAPI_BASE_URL}/rooms", 
            json=room,
            timeout=15
        ) as response:
            response.raise_for_status()
            response_data = await response.json()
            
            # Process successful response
            room_id = response_data.get("id")
            
            # Log success
            if index < 3:
                logger.info(f"Successfully created room: '{room['name']}' with ID {room_id}")
                
            return {
                "room": room["name"],
                "status": "success",
                "id": room_id
            }, True  # Success flag
    except Exception as e:
        error_msg = str(e)
        
        # Log the error with request details
        logger.error(f"Error creating room '{room['name']}': {error_msg}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status}, Content: {await e.response.text()}")
            
        return {
            "room": room["name"],
            "status": "error",
            "message": error_msg
        }, False  # Error flag

async def store_rooms_async(rooms):
    """Send rooms to FastAPI endpoint for storage using async"""
    results = []
    success_count = 0
    error_count = 0
    
    logger.info(f"Starting to store {len(rooms)} rooms in database using concurrent requests")
    
    # Process in batches to avoid overwhelming the server
    batch_size = 10
    
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(rooms), batch_size):
            batch = rooms[i:i+batch_size]
            batch_tasks = [process_room(session, room, i+j) for j, room in enumerate(batch)]
            batch_results = await asyncio.gather(*batch_tasks)
            
            # Process results
            for result, success in batch_results:
                results.append(result)
                if success:
                    success_count += 1
                else:
                    error_count += 1
    
    # Log summary of results
    logger.info(f"Room synchronization completed: {success_count} succeeded, {error_count} failed")
    
    return results

async def store_rooms_in_db(rooms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Store rooms in the FastAPI database via API calls.
    
    Args:
        rooms (List[Dict[str, Any]]): List of room objects to store
        
    Returns:
        List[Dict[str, Any]]: Results of API calls
    """
    results = []
    success_count = 0
    error_count = 0
    
    # Use aiohttp for making HTTP calls
    async with aiohttp.ClientSession() as session:
        # Process rooms sequentially to avoid concurrent database transactions
        for i, room in enumerate(rooms):
            # Add a small delay between requests to avoid overwhelming the API
            if i > 0:
                await asyncio.sleep(0.1)
                
            # Process the room
            try:
                result, success = await process_room(session, room, i)
                results.append(result)
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
                # Log progress every 10 rooms
                if i % 10 == 0 and i > 0:
                    logger.info(f"Processed {i}/{len(rooms)} rooms so far")
                    
            except Exception as e:
                logger.error(f"Unexpected error processing room {room.get('name', 'unknown')}: {str(e)}")
                results.append({
                    "room": room.get('name', 'unknown'),
                    "status": "error",
                    "message": f"Unexpected error: {str(e)}"
                })
                error_count += 1
    
    logger.info(f"Rooms API results: {success_count} succeeded, {error_count} failed")
    return results

async def process_user(session, user, index):
    """Process a single user with error handling"""
    try:
        # Log the user data being sent
        if index < 3:
            logger.info(f"Sending user data: {user}")
            
        # Make the API request
        async with session.post(
            f"{FASTAPI_BASE_URL}/users", 
            json=user,
            timeout=15
        ) as response:
            response.raise_for_status()
            response_data = await response.json()
            
            # Process successful response
            user_id = response_data.get("id")
            
            # Log success
            if index < 3:
                logger.info(f"Successfully created user: '{user['firstName']} {user['lastName']}' with ID {user_id}")
                
            return {
                "user": f"{user['firstName']} {user['lastName']}",
                "status": "success",
                "id": user_id
            }, True  # Success flag
    except Exception as e:
        error_msg = str(e)
        
        # Log the error with request details
        logger.error(f"Error creating user '{user['firstName']} {user['lastName']}': {error_msg}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status}, Content: {await e.response.text()}")
            
        return {
            "user": f"{user['firstName']} {user['lastName']}",
            "status": "error",
            "message": error_msg
        }, False  # Error flag

async def store_faculty_staff_async(staff):
    """Send faculty staff to FastAPI endpoint for storage using async"""
    results = []
    success_count = 0
    error_count = 0
    
    logger.info(f"Starting to store {len(staff)} faculty staff in database using concurrent requests")
    
    # Process in batches to avoid overwhelming the server
    batch_size = 10
    
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(staff), batch_size):
            batch = staff[i:i+batch_size]
            batch_tasks = [process_user(session, user, i+j) for j, user in enumerate(batch)]
            batch_results = await asyncio.gather(*batch_tasks)
            
            # Process results
            for result, success in batch_results:
                results.append(result)
                if success:
                    success_count += 1
                else:
                    error_count += 1
    
    # Log summary of results
    logger.info(f"Faculty staff synchronization completed: {success_count} succeeded, {error_count} failed")
    
    return results

async def store_faculty_staff_in_db(staff: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Store faculty staff in the FastAPI database via API calls.
    
    Args:
        staff (List[Dict[str, Any]]): List of user objects to store
        
    Returns:
        List[Dict[str, Any]]: Results of API calls
    """
    results = []
    success_count = 0
    error_count = 0
    
    # Use aiohttp for making HTTP calls
    async with aiohttp.ClientSession() as session:
        # Process staff sequentially to avoid concurrent database transactions
        for i, user in enumerate(staff):
            # Add a small delay between requests to avoid overwhelming the API
            if i > 0:
                await asyncio.sleep(0.1)
                
            # Process the user
            try:
                result, success = await process_user(session, user, i)
                results.append(result)
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
                # Log progress every 10 users
                if i % 10 == 0 and i > 0:
                    logger.info(f"Processed {i}/{len(staff)} faculty staff so far")
                    
            except Exception as e:
                user_name = f"{user.get('firstName', '')} {user.get('lastName', '')}"
                logger.error(f"Unexpected error processing user {user_name}: {str(e)}")
                results.append({
                    "user": user_name,
                    "status": "error",
                    "message": f"Unexpected error: {str(e)}"
                })
                error_count += 1
    
    logger.info(f"Faculty staff API results: {success_count} succeeded, {error_count} failed")
    return results
