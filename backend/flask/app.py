from flask import Flask, jsonify, request
import requests
import logging
import os
from flasgger import Swagger, swag_from

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
    "title": "Data Synchronization API",
    "description": "API for synchronizing group data from USV to TWAAOS",
    "version": "1.0.0",
}

swagger = Swagger(app, config=swagger_config)

# Constants
FACULTY_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/facultati.php?json"
GROUPS_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/subgrupe.php?json"
ROOMS_ENDPOINT = "https://orar.usv.ro/orar/vizualizare/data/sali.php?json"
FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://localhost:8000")

@app.route('/health', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Health check successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'}
                }
            }
        }
    },
    'summary': 'Health check endpoint',
    'description': 'Simple endpoint to check if the service is running'
})
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/fetch-and-sync-data', methods=['POST'])
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
    'description': 'Fetches faculty, group, and room data from USV API and sends it to the FastAPI application to be stored in the database.',
    'tags': ['synchronization']
})
def fetch_and_sync_data():
    """
    Fetches faculty, group, and room data from USV API and sends it
    to the FastAPI application to be stored in the database.
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
        
        return jsonify({
            "success": True,
            "message": f"Successfully processed {len(transformed_groups)} groups and {len(transformed_rooms)} rooms",
            "groups": {
                "count": len(transformed_groups),
                "results": group_results
            },
            "rooms": {
                "count": len(transformed_rooms),
                "results": room_results
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return jsonify({"error": str(e)}), 500

def fetch_faculties():
    """Fetch faculties data from USV API"""
    response = requests.get(FACULTY_ENDPOINT)
    response.raise_for_status()  # Raise exception for 4XX/5XX responses
    return response.json()

def fetch_groups():
    """Fetch groups data from USV API"""
    response = requests.get(GROUPS_ENDPOINT)
    response.raise_for_status()
    return response.json()

def transform_groups(groups):
    """
    Transform groups from USV API format to our API format
    Extract only needed fields: groupName, studyYear, specializationShortName
    """
    transformed = []
    
    for group in groups:
        # Skip any groups with missing required fields
        if not group.get("groupName") or not group.get("studyYear"):
            continue
            
        transformed.append({
            "name": group.get("groupName"),
            "studyYear": int(group.get("studyYear")),
            "specializationShortName": group.get("specializationShortName")
        })
    
    return transformed

def store_groups_in_db(groups):
    """Send groups to FastAPI endpoint for storage"""
    results = []
    
    for group in groups:
        try:
            response = requests.post(
                f"{FASTAPI_BASE_URL}/groups", 
                json=group
            )
            response.raise_for_status()
            results.append({
                "group": group["name"],
                "status": "success",
                "id": response.json().get("id")
            })
        except Exception as e:
            results.append({
                "group": group["name"],
                "status": "error",
                "message": str(e)
            })
    
    return results

def fetch_rooms():
    """Fetch rooms data from USV API"""
    response = requests.get(ROOMS_ENDPOINT)
    response.raise_for_status()  # Raise exception for 4XX/5XX responses
    return response.json()
    
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
