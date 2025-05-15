"""API routes for the Quart application (async Flask alternative)."""
from quart import Blueprint, jsonify
# Comment out swagger import since it's causing issues
# from quart_swagger import swag_from
import logging
import asyncio
from services.api_service import (
    fetch_faculties, 
    fetch_groups, 
    fetch_rooms,
    fetch_faculty_staff,
    fetch_group_subjects
)
from services.transform_service import (
    transform_groups, 
    transform_rooms,
    transform_faculty_staff,
    transform_subjects
)
from services.store_service import (
    store_groups_in_db, 
    store_rooms_in_db,
    store_faculty_staff_in_db,
    store_subjects_in_db
)

# Create a logger for this module
logger = logging.getLogger(__name__)

# Create a blueprint for the API routes
api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
# Swagger documentation commented out to avoid dependency issues
# @swag_from documentation was here
async def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy"})

@api_bp.route('/fetch-and-sync-data', methods=['POST'])
# Swagger documentation commented out to avoid dependency issues
# @swag_from documentation was here
async def fetch_and_sync_data():
    """Fetch data from USV APIs and sync it to the TWAAOS database via FastAPI
    
    Process:
    1. Fetch faculties to find FIESC
    2. Fetch groups and filter for FIESC
    3. Fetch rooms
    4. Fetch faculty staff
    5. Transform data to match our API format
    6. Send to FastAPI for storage
    """
    try:
        # Part 1: Process Groups 
        # -----------------------
        # Step 1: Fetch faculties and find FIESC
        faculties = await fetch_faculties()
        fiesc_id = None
        group_results = []
        transformed_groups = []
        
        for faculty in faculties:
            if faculty.get("shortName") == "FIESC":
                fiesc_id = faculty.get("id")
                break
        
        if not fiesc_id:
            logger.warning("FIESC faculty not found")
        else:
            logger.info(f"Found FIESC faculty with ID: {fiesc_id}")
            
            # Step 2: Fetch all groups and filter for FIESC
            all_groups = await fetch_groups()
            fiesc_groups = [group for group in all_groups if group.get("facultyId") == fiesc_id]
            
            if not fiesc_groups:
                logger.warning("No FIESC groups found")
            else:
                logger.info(f"Found {len(fiesc_groups)} FIESC groups")
                
                # Step 3: Transform group data to match our API format
                transformed_groups = await transform_groups(fiesc_groups)
                
                # Step 4: Send groups to FastAPI for storage
                group_results = await store_groups_in_db(transformed_groups)
        
        # Part 2: Process Rooms
        # ---------------------
        # Step 1: Fetch all rooms
        all_rooms = await fetch_rooms()
        logger.info(f"Fetched {len(all_rooms)} rooms from USV API")
        
        # Step 2: Transform room data to match our API format
        transformed_rooms = await transform_rooms(all_rooms)
        
        # Step 3: Send rooms to FastAPI for storage
        room_results = await store_rooms_in_db(transformed_rooms)
        
        # Part 3: Process Faculty Staff (Users)
        # ------------------------------------
        # Step 1: Fetch all faculty staff
        all_staff = await fetch_faculty_staff()
        logger.info(f"Fetched {len(all_staff)} faculty staff from USV API")
        
        # Step 2: Transform staff data, filtering by faculty and department
        transformed_staff = await transform_faculty_staff(all_staff)
        
        # Step 3: Send faculty staff to FastAPI for storage
        staff_results = await store_faculty_staff_in_db(transformed_staff)
        
        # Part 4: Process Subjects
        # ---------------------
        # Note: This needs to happen after users are processed since we need to look up teacher IDs
        logger.info("Starting subject synchronization process")
        
        all_subject_results = []
        total_subjects_processed = 0
        
        # For each FIESC group that we successfully synced, fetch its subjects
        for group_result in group_results:
            if group_result.get("status") != "success" or not group_result.get("id"):
                continue
                
            group_db_id = group_result.get("id")
            group_name = group_result.get("group")
            
            # Find the original group in our transformed groups to get USV group IDs
            original_group = None
            for group in transformed_groups:
                if group.get("name") == group_name:
                    original_group = group
                    break
                    
            if not original_group or not original_group.get("groupIds"):
                logger.warning(f"Could not find original group data for '{group_name}', skipping subject fetch")
                continue
            
            # Collect all subject data from all USV group IDs for this database group
            all_group_subject_data = []
            
            # Fetch subjects for each groupId from the USV API
            for usv_group_id in original_group.get("groupIds", []):
                logger.info(f"Fetching subjects for group {group_name} (USV ID: {usv_group_id})")
                
                # Fetch subject data from USV API
                subject_data = await fetch_group_subjects(usv_group_id)
                
                if not subject_data or not subject_data[0]:
                    logger.warning(f"No subject data found for group {group_name} (USV ID: {usv_group_id})")
                    continue
                
                # Combine all activities from all USV group IDs for this database group
                if all_group_subject_data:
                    # If we already have data, append the new activities to the existing list
                    all_group_subject_data[0].extend(subject_data[0])
                    # Preserve the second element (ID mapping) as is
                else:
                    # First subject data for this group - use as is
                    all_group_subject_data = subject_data
            
            # Skip if we didn't find any subject data for this group
            if not all_group_subject_data:
                continue
                
            # Now transform all collected subject data at once for this group
            # This ensures deduplication happens across all USV group IDs for this database group
            transformed_subjects = await transform_subjects(all_group_subject_data, group_db_id)
            logger.info(f"Transformed {len(transformed_subjects)} unique subjects for group {group_name} (across all USV IDs)")
            total_subjects_processed += len(transformed_subjects)
            
            # Send subjects to FastAPI for storage
            if transformed_subjects:
                subject_results = await store_subjects_in_db(transformed_subjects)
                all_subject_results.extend(subject_results)
        
        logger.info(f"Completed subject synchronization: processed {total_subjects_processed} total subjects")
        
        return jsonify({
            "success": True,
            "message": f"Successfully processed {len(transformed_groups)} groups, {len(transformed_rooms)} rooms, {len(transformed_staff)} faculty staff, and {total_subjects_processed} subjects",
            "groups": {
                "count": len(transformed_groups),
                "results": group_results
            },
            "rooms": {
                "count": len(transformed_rooms),
                "results": room_results
            },
            "users": {
                "count": len(transformed_staff),
                "results": staff_results
            },
            "subjects": {
                "count": total_subjects_processed,
                "results": all_subject_results
            }
        })
        
    except Exception as e:
        logger.error(f"Error during data synchronization: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
