"""API routes for the Flask application."""
from flask import Blueprint, jsonify
from flasgger import swag_from
import logging
from services.api_service import (
    fetch_faculties, 
    fetch_groups, 
    fetch_rooms,
    fetch_faculty_staff
)
from services.transform_service import (
    transform_groups, 
    transform_rooms,
    transform_faculty_staff
)
from services.store_service import (
    store_groups_in_db, 
    store_rooms_in_db,
    store_faculty_staff_in_db
)
from config.settings import TARGET_FACULTY_NAME

# Create a logger for this module
logger = logging.getLogger(__name__)

# Create a blueprint for the API routes
api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Simple health check to verify the service is running',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'}
                }
            }
        }
    },
    'summary': 'Health check endpoint',
    'description': 'Simple endpoint to check if the service is up and running',
    'tags': ['system']
})
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy"})

@api_bp.route('/fetch-and-sync-data', methods=['POST'])
@swag_from({
    'responses': {
        200: {
            'description': 'Successfully fetched and synchronized data',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'groups': {
                        'type': 'object',
                        'properties': {
                            'count': {'type': 'integer'},
                            'results': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'group': {'type': 'string'},
                                        'status': {'type': 'string'},
                                        'id': {'type': 'integer'}
                                    }
                                }
                            }
                        }
                    },
                    'rooms': {
                        'type': 'object',
                        'properties': {
                            'count': {'type': 'integer'},
                            'results': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'room': {'type': 'string'},
                                        'status': {'type': 'string'},
                                        'id': {'type': 'integer'}
                                    }
                                }
                            }
                        }
                    },
                    'users': {
                        'type': 'object',
                        'properties': {
                            'count': {'type': 'integer'},
                            'results': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'user': {'type': 'string'},
                                        'status': {'type': 'string'},
                                        'id': {'type': 'integer'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Required data not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        500: {
            'description': 'Server error during processing',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    },
    'summary': 'Fetch and synchronize data from USV to TWAAOS',
    'description': 'Fetches faculty, group, room, and faculty staff data from USV API and sends it to the FastAPI application to be stored in the database.',
    'tags': ['synchronization']
})
def fetch_and_sync_data():
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
        faculties = fetch_faculties()
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
            all_groups = fetch_groups()
            fiesc_groups = [group for group in all_groups if group.get("facultyId") == fiesc_id]
            
            if not fiesc_groups:
                logger.warning("No FIESC groups found")
            else:
                logger.info(f"Found {len(fiesc_groups)} FIESC groups")
                
                # Step 3: Transform group data to match our API format
                transformed_groups = transform_groups(fiesc_groups)
                
                # Step 4: Send groups to FastAPI for storage
                group_results = store_groups_in_db(transformed_groups)
        
        # Part 2: Process Rooms
        # ---------------------
        # Step 1: Fetch all rooms
        all_rooms = fetch_rooms()
        logger.info(f"Fetched {len(all_rooms)} rooms from USV API")
        
        # Step 2: Transform room data to match our API format
        transformed_rooms = transform_rooms(all_rooms)
        
        # Step 3: Send rooms to FastAPI for storage
        room_results = store_rooms_in_db(transformed_rooms)
        
        # Part 3: Process Faculty Staff (Users)
        # ------------------------------------
        # Step 1: Fetch all faculty staff
        all_staff = fetch_faculty_staff()
        logger.info(f"Fetched {len(all_staff)} faculty staff from USV API")
        
        # Step 2: Transform staff data, filtering by faculty and department
        transformed_staff = transform_faculty_staff(all_staff)
        
        # Step 3: Send faculty staff to FastAPI for storage
        staff_results = store_faculty_staff_in_db(transformed_staff)
        
        return jsonify({
            "success": True,
            "message": f"Successfully processed {len(transformed_groups)} groups, {len(transformed_rooms)} rooms, and {len(transformed_staff)} faculty staff",
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
            }
        })
        
    except Exception as e:
        logger.error(f"Error during data synchronization: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
