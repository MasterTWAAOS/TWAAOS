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

# User search and subject storage functions
async def get_all_users_with_role(session, role="CD"):
    """Get all users with a specific role from the database
    
    This is more efficient than making individual queries for each teacher
    
    Args:
        session (aiohttp.ClientSession): The HTTP client session
        role (str, optional): The role to filter by. Defaults to "CD" (teacher)
        
    Returns:
        dict: Dictionary mapping normalized names to user IDs
    """
    try:
        users_cache = {}
        
        # Make API request to get all users
        async with session.get(
            f"{FASTAPI_BASE_URL}/users", 
            timeout=15
        ) as response:
            if response.status == 200:
                users = await response.json()
                
                # Filter users by role and build the cache
                for user in users:
                    if user.get("role") == role:
                        # Create different variations of the name for matching
                        full_name = f"{user.get('firstName', '')} {user.get('lastName', '')}".lower()
                        last_first = f"{user.get('lastName', '')} {user.get('firstName', '')}".lower()
                        last_name = user.get('lastName', '').lower()
                        
                        # Store all variations in the cache
                        users_cache[full_name] = user.get("id")
                        users_cache[last_first] = user.get("id")
                        users_cache[last_name] = user.get("id")
                
                logger.info(f"Loaded {len(users)} users, {len([u for u in users if u.get('role') == role])} with role {role}")
                return users_cache
            else:
                logger.error(f"Error getting users: {response.status}")
                return {}
    except Exception as e:
        logger.error(f"Error getting users with role {role}: {str(e)}")
        return {}

async def find_user_by_name_and_role(session, last_name, first_name, role):
    """Find a user by name and role in the database using a direct search
    
    Args:
        session (aiohttp.ClientSession): The HTTP client session
        last_name (str): Last name to search for
        first_name (str): First name to search for
        role (str): Role to filter by
        
    Returns:
        int or None: User ID if found, None otherwise
    """
    try:
        # Build the query parameters for exact search
        # Note: FastAPI controller expects camelCase parameter names
        params = {
            "lastName": last_name,
            "firstName": first_name,
            "role": role
        }
        
        # Make the API request
        async with session.get(
            f"{FASTAPI_BASE_URL}/users/search", 
            params=params,
            timeout=10
        ) as response:
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_data = await response.json()
            
            # If we found at least one user, return the first one's ID
            if response_data and len(response_data) > 0:
                user_id = response_data[0]["id"]
                logger.info(f"Found user {last_name} {first_name} with role {role} (ID: {user_id})")
                return user_id
            else:
                # Try with just last name as fallback
                logger.warning(f"No exact match for {last_name} {first_name}. Trying with last name only.")
                params = {
                    "lastName": last_name,  # Use camelCase to match FastAPI controller
                    "role": role
                }
                
                async with session.get(
                    f"{FASTAPI_BASE_URL}/users/search", 
                    params=params,
                    timeout=10
                ) as fallback_response:
                    fallback_response.raise_for_status()
                    fallback_data = await fallback_response.json()
                    
                    if fallback_data and len(fallback_data) > 0:
                        user_id = fallback_data[0]["id"]
                        logger.info(f"Found user by last name only: {last_name} with role {role} (ID: {user_id})")
                        return user_id
                
                logger.warning(f"No user found for {last_name} {first_name} with role {role}")
                return None
    except Exception as e:
        logger.error(f"Error searching for user {last_name}, {first_name}, {role}: {str(e)}")
        return None

async def process_subject(session, subject, index, processed_teachers=None, processed_assistants=None):
    """Process a single subject with error handling
    
    Args:
        session (aiohttp.ClientSession): The HTTP client session
        subject (dict): The subject data to process
        index (int): The index of this subject in the list (for logging purposes)
        processed_teachers (dict): Dictionary of already processed teachers (lastName_firstName -> id)
        processed_assistants (dict): Dictionary of already processed assistants (lastName_firstName -> id)
        
    Returns:
        tuple: (result_dict, success_flag)
    """
    try:
        # Make a copy of the subject to avoid modifying the original
        subject_to_save = subject.copy()
        
        # Initialize dictionaries if None
        if processed_teachers is None:
            processed_teachers = {}
        if processed_assistants is None:
            processed_assistants = {}
            
        # Process teacher if available
        if "teacherInfo" in subject:
            teacher_info = subject["teacherInfo"]
            teacher_key = f"{teacher_info['lastName']}_{teacher_info['firstName']}"
            
            # Check if we've already processed this teacher
            if teacher_key in processed_teachers:
                teacher_id = processed_teachers[teacher_key]
                logger.info(f"Using cached teacherId {teacher_id} for subject {subject['name']}")
            else:
                # Find teacher in the database with direct search
                teacher_id = await find_user_by_name_and_role(
                    session, 
                    teacher_info["lastName"], 
                    teacher_info["firstName"], 
                    "CD"
                )
                
                # Save to processed dictionary for future use
                if teacher_id:
                    processed_teachers[teacher_key] = teacher_id
            
            # Store in subject if found
            if teacher_id:
                subject_to_save["teacherId"] = teacher_id
                logger.info(f"Set teacherId to {teacher_id} for subject {subject['name']}")
            else:
                # If no teacher found, this is an error - teacher must exist
                error_msg = f"ERROR: Teacher {teacher_info['lastName']} {teacher_info['firstName']} not found in database."
                logger.error(error_msg + " This indicates a potential data issue.")
                return {
                    "subject": subject.get("name", "Unknown"),
                    "status": "error",
                    "message": error_msg
                }, False
        else:
            # If no teacher info provided, skip this subject
            logger.warning(f"No teacher info for subject {subject['name']}, cannot create without a valid teacherId")
            return {
                "subject": subject.get("name", "Unknown"),
                "status": "error",
                "message": "No teacher information available"
            }, False
        
        # Process assistants if needed
        if "assistantInfo" in subject:
            assistant_infos = subject["assistantInfo"]
            subject_to_save["assistantIds"] = []
            
            # Find each assistant
            for assistant_info in assistant_infos:
                assistant_key = f"{assistant_info['lastName']}_{assistant_info['firstName']}"
                
                # Check if we've already processed this assistant
                if assistant_key in processed_assistants:
                    assistant_id = processed_assistants[assistant_key]
                    logger.info(f"Using cached assistantId {assistant_id} for subject {subject['name']}")
                else:
                    # Find assistant with direct search
                    assistant_id = await find_user_by_name_and_role(
                        session, 
                        assistant_info["lastName"], 
                        assistant_info["firstName"], 
                        "CD"
                    )
                    
                    # Save to processed dictionary
                    if assistant_id:
                        processed_assistants[assistant_key] = assistant_id
                
                # Add to subject's assistantIds list if found
                if assistant_id and assistant_id not in subject_to_save["assistantIds"]:
                    subject_to_save["assistantIds"].append(assistant_id)
                    logger.info(f"Added assistantId {assistant_id} for subject {subject['name']}")
        else:
            # Initialize empty assistantIds array if no assistants
            subject_to_save["assistantIds"] = []
            
        # Remove the reference fields before saving
        if "teacherInfo" in subject_to_save:
            del subject_to_save["teacherInfo"]
        if "assistantInfo" in subject_to_save:
            del subject_to_save["assistantInfo"]
        
        # Log the subject data being sent (only for first few)
        if index < 3:
            logger.info(f"Sending subject data: {subject_to_save}")
            
        # Make the API request
        async with session.post(
            f"{FASTAPI_BASE_URL}/subjects", 
            json=subject_to_save,
            timeout=15
        ) as response:
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_data = await response.json()
            
            # Process successful response
            subject_id = response_data.get("id")
            
            # Log success (only for first few)
            if index < 3:
                logger.info(f"Successfully created subject: '{subject_to_save['name']}' with ID {subject_id}")
                
            return {
                "subject": subject_to_save["name"],
                "status": "success",
                "id": subject_id
            }, True  # Success flag
            
    except Exception as e:
        error_msg = str(e)
        subject_name = subject.get("name", "Unknown")
        
        # Log the error with request details
        logger.error(f"Error creating subject '{subject_name}': {error_msg}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status}, Content: {await e.response.text()[:200]}")
            
        return {
            "subject": subject_name,
            "status": "error",
            "message": error_msg
        }, False  # Error flag

async def store_subjects_async(subjects):
    """Send subjects to FastAPI endpoint for storage using async
    
    Args:
        subjects (list): List of subject objects to store
        
    Returns:
        tuple: (results, success_count, error_count)
    """
    results = []
    success_count = 0
    error_count = 0
    
    # Dictionaries to cache processed teachers and assistants
    processed_teachers = {}
    processed_assistants = {}
    
    # Use aiohttp for asynchronous HTTP requests with increased timeout
    timeout = aiohttp.ClientTimeout(total=90)  # Increase timeout to 90 seconds
    conn = aiohttp.TCPConnector(limit=5)  # Strict limit on connections
    
    async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
        logger.info(f"Starting to process {len(subjects)} subjects")
        
        # Find all unique course names ("curs")
        unique_courses = set()
        for subject in subjects:
            if subject.get("type", "").lower() == "curs":
                unique_courses.add(subject.get("name", ""))
        logger.info(f"Found {len(unique_courses)} unique courses to process")
        
        # Process subjects COMPLETELY SEQUENTIALLY to avoid overwhelming the database
        # This is much safer but slower than parallel processing
        results_list = []
        
        for i, subject in enumerate(subjects):
            try:
                # Add delay between subjects to prevent any connection pool issues
                if i > 0:
                    # 1 second delay between each subject
                    await asyncio.sleep(0.1)
                
                result = await process_subject(session, subject, i, processed_teachers, processed_assistants)
                results_list.append(result)
                
                # Log progress
                if (i + 1) % 3 == 0 or i == len(subjects) - 1:
                    logger.info(f"Processed {i+1}/{len(subjects)} subjects")
            except Exception as e:
                logger.error(f"Unexpected error processing subject {subject.get('name', 'unknown')}: {str(e)}")
                results_list.append(Exception(f"Error processing {subject.get('name', 'unknown')}: {str(e)}"))

        # Process results
        for result in results_list:
            if isinstance(result, Exception):
                # Handle unexpected exceptions
                error_count += 1
                logger.error(f"Unexpected error processing subject: {str(result)}")
                results.append({
                    "subject": "Unknown",
                    "status": "error",
                    "message": f"Unexpected error: {str(result)}"
                })
            else:
                # result is a tuple (result_dict, success_flag)
                results.append(result[0])
                if result[1]:  # success flag
                    success_count += 1
                else:
                    error_count += 1
        
        # Log summary information
        logger.info(f"Processed {len(processed_teachers)} unique teachers")
        logger.info(f"Processed {len(processed_assistants)} unique assistants")
        teacher_sample = list(processed_teachers.items())[:3]
        logger.info(f"Sample of processed teachers: {teacher_sample}")
                
        # Final stats
        logger.info(f"Subject API results: {success_count} succeeded, {error_count} failed")
    
    return results, success_count, error_count

async def store_subjects_in_db(subjects: List[Dict[str, Any]]):
    """Store subjects in the FastAPI database via API calls.
    
    Args:
        subjects (List[Dict[str, Any]]): List of subject objects to store
        
    Returns:
        List[Dict[str, Any]]: Results of API calls
    """
    try:
        logger.info(f"Starting to store {len(subjects)} subjects in the database")
        
        # Use the async function to store subjects
        results, success_count, error_count = await store_subjects_async(subjects)
        
        # Log results summary
        logger.info(f"Subject storage complete: {success_count} succeeded, {error_count} failed")
        
        return results
    except Exception as e:
        logger.error(f"Error in store_subjects_in_db: {str(e)}")
        return [{"status": "error", "message": str(e)}]
