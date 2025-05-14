"""Services for transforming data from external APIs to our data model."""
from config.settings import logger, TARGET_FACULTY_NAME

async def transform_groups(groups):
    """Transform groups from USV API format to our API format
    
    Extract only the needed fields and format them according to our GroupDTO.
    Deduplicate groups by comparing all relevant properties (name, study year, specialization),
    keeping only the first occurrence but storing all original IDs in the groupIds field.
    """
    # Dictionary to track unique groups by a composite key and collect all related IDs
    unique_groups = {}
    
    for group in groups:
        # Skip any groups with missing required fields
        if not group.get("groupName"):
            continue
            
        group_name = group.get("groupName")
        group_id = group.get("id")
        study_year = int(group.get("studyYear") or 1)
        specialization = group.get("specializationShortName") or ""
        
        # Create a composite key using multiple fields for uniqueness
        # This ensures we're not just relying on the name but considering all relevant properties
        unique_key = f"{group_name}_{study_year}_{specialization}"
        
        # If we've already seen a group with the same properties, just add its ID to the list
        if unique_key in unique_groups:
            # Add this ID to the existing group's groupIds list
            if group_id:
                unique_groups[unique_key]["groupIds"].append(group_id)
            continue
            
        # Create a new dict with only the fields we need
        group_data = {
            "name": group_name,
            "studyYear": study_year,
            "specializationShortName": specialization,
            "groupIds": [group_id] if group_id else []  # Initialize with this group's ID
        }
        
        # Store in our unique groups dictionary using the composite key
        unique_groups[unique_key] = group_data
    
    # Convert the dictionary to a list
    transformed = list(unique_groups.values())
    
    logger.info(f"Found {len(groups)} total groups, deduplicated to {len(transformed)} unique groups")
    return transformed

async def transform_rooms(rooms):
    """Transform rooms from USV API format to our API format
    
    The room fields in the USV API match our needs, but we want to remove the id field
    as it will be auto-generated in our database.
    """
    transformed = []
    skipped_count = 0
    
    # Log the structure of the first room for debugging
    if rooms and len(rooms) > 0:
        logger.info(f"Sample room structure from API: {rooms[0]}")
    
    for room in rooms:
        # Check for all required fields
        required_fields = ["name"]
        missing_fields = [field for field in required_fields if not room.get(field)]
        
        if missing_fields:
            skipped_count += 1
            if skipped_count <= 3:  # Only log first 3 skipped rooms
                logger.warning(f"Skipping room due to missing fields {missing_fields}: {room}")
            continue
        
        # Create a new dict with all required fields for RoomDTO
        room_data = {
            "name": room.get("name"),
            "shortName": room.get("shortName") or room.get("name"),  # Fallback if shortName missing
            "buildingName": room.get("buildingName") or "Unknown",  # Fallback if buildingName missing
            "capacity": int(room.get("capacity") or 0),  # Default to 0 if capacity is None
            "computers": int(room.get("computers") or 0)  # Default to 0 if computers is None
        }
        
        # Ensure all values are of the correct types
        room_data["capacity"] = int(room_data["capacity"])
        room_data["computers"] = int(room_data["computers"])
        
        transformed.append(room_data)
    
    logger.info(f"Transformed {len(transformed)} rooms successfully, skipped {skipped_count} rooms")
    return transformed

async def transform_subjects(subject_data, group_db_id):
    """Transform subjects from USV API format to our API format
    
    Args:
        subject_data (list): The subject data from USV API (containing list of activities and ID mapping)
        group_db_id (int): The database ID of the group these subjects belong to
        
    Returns:
        list: List of transformed subjects ready for saving in our database
    """
    if not subject_data or len(subject_data) < 2:
        logger.warning("No valid subject data to transform")
        return []
    
    activities = subject_data[0]  # List of activities
    
    # Extract lecture ("curs") activities as these will become our subject base
    courses = [activity for activity in activities if activity.get("typeLongName") == "curs"]
    
    # Use a dictionary to deduplicate subjects based on topicShortName
    unique_subjects = {}
    
    for course in courses:
        # Skip any courses with missing required fields
        if not course.get("topicLongName") or not course.get("topicShortName"):
            continue
            
        # Use topicShortName as the unique key
        subject_key = course.get("topicShortName")
        
        # If we haven't seen this subject before, create a new one
        if subject_key not in unique_subjects:
            unique_subjects[subject_key] = {
                "name": course.get("topicLongName"),
                "shortName": course.get("topicShortName"),
                "groupId": group_db_id,
                "teacherId": None,  # Will be filled later after user lookup
                "assistantIds": [],  # Will be filled later
                "teacherInfo": {  # Store for reference during assistant processing
                    "lastName": course.get("teacherLastName", "").strip(),
                    "firstName": course.get("teacherFirstName", "").strip()
                }
            }
    
    # Now find all other activities (labs, seminars) that match our subjects
    # to identify assistant teachers
    for activity in activities:
        activity_type = activity.get("typeLongName")
        subject_key = activity.get("topicShortName")
        
        # Skip courses (already processed) and activities not matching our subjects
        if activity_type == "curs" or subject_key not in unique_subjects:
            continue
            
        # Get the teacher info from this activity
        last_name = activity.get("teacherLastName", "").strip()
        first_name = activity.get("teacherFirstName", "").strip()
        
        # Check if this is a different teacher than the course teacher
        subject = unique_subjects[subject_key]
        if (last_name and first_name and 
            (last_name != subject["teacherInfo"]["lastName"] or 
             first_name != subject["teacherInfo"]["firstName"])):
            
            # Add this assistant info to be processed later
            if "assistantInfo" not in subject:
                subject["assistantInfo"] = []
                
            # Check if we already have this assistant
            assistant_exists = False
            for assistant in subject["assistantInfo"]:
                if assistant["lastName"] == last_name and assistant["firstName"] == first_name:
                    assistant_exists = True
                    break
                    
            if not assistant_exists:
                subject["assistantInfo"].append({
                    "lastName": last_name,
                    "firstName": first_name
                })
    
    # Convert dictionary to list, preserving all fields for later processing
    transformed = list(unique_subjects.values())
    
    # Add logging details
    teachers_count = sum(1 for subject in transformed if "teacherInfo" in subject)
    assistants_count = sum(len(subject.get("assistantInfo", [])) for subject in transformed)
    
    logger.info(f"Found {len(transformed)} unique subjects with {teachers_count} teachers and {assistants_count} assistants")
    return transformed

async def transform_faculty_staff(staff_data):
    """Transform faculty staff data from USV API format to our API format
    
    Filter staff by faculty name or department name (Exterior),
    and map fields according to our UserDTO requirements.
    """
    transformed = []
    skipped_count = 0
    
    # Log the structure of the first staff member for debugging
    if staff_data and len(staff_data) > 0:
        logger.info(f"Sample staff structure from API: {staff_data[0]}")
    
    for staff in staff_data:
        # Check if this person belongs to our target faculty or has department "Exterior"
        faculty_name = staff.get("facultyName")
        department_name = staff.get("departmentName")
        
        if not (faculty_name == TARGET_FACULTY_NAME or department_name == "Exterior"):
            skipped_count += 1
            continue
        
        # Check for all required fields
        required_fields = ["lastName", "firstName", "emailAddress"]
        missing_fields = [field for field in required_fields if not staff.get(field)]
        
        if missing_fields:
            skipped_count += 1
            if skipped_count <= 3:  # Only log first 3 skipped staff
                logger.warning(f"Skipping staff due to missing fields {missing_fields}: {staff}")
            continue
        
        # Create a new dict with mapped fields for UserDTO
        user_data = {
            "lastName": staff.get("lastName"),
            "firstName": staff.get("firstName"),
            "email": staff.get("emailAddress"),
            "phone": staff.get("phoneNumber"),
            "department": staff.get("departmentName"),
            "role": "CD",  # All faculty staff will be assigned role CD
            "isActive": True
        }
        
        transformed.append(user_data)
    
    logger.info(f"Transformed {len(transformed)} faculty staff successfully, skipped {skipped_count} staff members")
    return transformed
