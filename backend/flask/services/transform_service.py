"""Services for transforming data from external APIs to our data model."""
from config.settings import logger, TARGET_FACULTY_NAME

def transform_groups(groups):
    """Transform groups from USV API format to our API format
    
    Extract only the needed fields and format them according to our GroupDTO.
    Deduplicate groups by groupName, keeping only the first occurrence but storing
    all original IDs in the groupIds field.
    """
    # Dictionary to track unique groups by name and collect all related IDs
    unique_groups = {}
    
    for group in groups:
        # Skip any groups with missing required fields
        if not group.get("groupName"):
            continue
            
        group_name = group.get("groupName")
        group_id = group.get("id")
        
        # If we've already seen this group name, just add its ID to the list
        if group_name in unique_groups:
            # Add this ID to the existing group's groupIds list
            if group_id:
                unique_groups[group_name]["groupIds"].append(group_id)
            continue
            
        # Create a new dict with only the fields we need
        group_data = {
            "name": group_name,
            "studyYear": int(group.get("studyYear") or 1),
            "specializationShortName": group.get("specializationShortName") or "",
            "groupIds": [group_id] if group_id else []  # Initialize with this group's ID
        }
        
        # Store in our unique groups dictionary
        unique_groups[group_name] = group_data
    
    # Convert the dictionary to a list
    transformed = list(unique_groups.values())
    
    logger.info(f"Found {len(groups)} total groups, deduplicated to {len(transformed)} unique groups")
    return transformed

def transform_rooms(rooms):
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

def transform_faculty_staff(staff_data):
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
