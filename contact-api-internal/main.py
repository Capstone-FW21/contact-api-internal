from ctdb_utility_lib.utility import add_room, connect_to_db
from ctdb_utility_lib.admin_utility import (
    get_records,
    get_user_records,
    get_contacts,
    get_people,
    get_records_count,
    get_rooms,
    get_buildings,
    connect_to_db,
    get_students_count,
    get_rooms_count,
    get_room,
    get_buildings_count,
    get_building,
)
import fastapi
import sys
from fastapi import FastAPI, status
from typing import List, Optional
from sarge import capture_stdout
from enum import Enum
import datetime


app = FastAPI()
connection = None


# to ensure only valid types are passed in
class StatTypes(str, Enum):
    students = "students"
    records = "records"
    buildings = "buildings"
    rooms = "rooms"


@app.get("/", include_in_schema=False)
def index():
    """
    Main index redirects to the Documentation.
    """
    return fastapi.responses.RedirectResponse(url="./docs")


#returns all scans in scan table
@app.get("/records")
def records(limit:int):
    global connection
    if connection is None:
        connection = connect_to_db()
    
    records = get_records(limit, connection)
    if records is None:
        raise fastapi.HTTPException(
            status_code=400, detail="There are no scans")
    return records

#returns scans for a specific email adress
@app.get("/user_records")
def user_records(email: str, limit: int):
    global connection
    if connection is None:
        connection = connect_to_db()

    user_record = get_user_records(email, limit, connection)
    if user_record == None:
        raise fastapi.HTTPException(
            status_code=400, detail="There are no scans for this person")
    if user_record == -1:
        raise fastapi.HTTPException(
            status_code=400, detail="Invalid email address")

    return user_record

#returns all people in contact with email address
#date format should be: June 28 2018 7:40AM, October 10 2013 10:50PM
@app.get("/breakout")
def breakout(email: str, date: str):

    global connection
    if connection is None:
        connection = connect_to_db()
    
    try:
        date_time_obj = datetime.datetime.strptime(date, '%B %d %Y %I:%M%p')
    except:
        raise fastapi.HTTPException(status_code=400, detail="Invalid date format")

    contacted = get_contacts(email, date_time_obj, connection)
    if contacted == -1:
        raise fastapi.HTTPException(
            status_code=400, detail="Invalid email format, or date is greater than 14 days ago")

    return contacted

#returns all entries for specific type
@app.get("/stats")
def stats(stat_type: StatTypes):
    global connection
    if connection is None:
        connection = connect_to_db()

    match stat_type:
        case 'students':
            result = get_people(connection)
            if result == None:
                raise fastapi.HTTPException(
                    status_code=400, detail="No student exists")
        case 'records':
            result = get_records_count(connection)
            if result == None:
                raise fastapi.HTTPException(
                    status_code=400, detail="No scans exists")
        case 'buildings':
            result = get_buildings(connection)
            if result == None:
                raise fastapi.HTTPException(
                    status_code=400, detail="No building exists")
        case 'rooms':
            result = get_rooms(connection)
            if result == None:
                raise fastapi.HTTPException(
                    status_code=400, detail="No room exists")

    return result

#get number of students in database
@app.get("/total_students")
def total_students():
    global connection
    if connection is None:
        connection = connect_to_db()

    return get_students_count(connection)

#get number of rooms in database
@app.get("/total_rooms")
def total_rooms():
    global connection
    if connection is None:
        connection = connect_to_db()

    return get_rooms_count(connection)

#if no data provided
#gets room id, capacity, building name, the total number of scans that happened in the room,
#count of unique students that have scanned in the room, and # of scans per day for that room 
#else
#gets singular room data
@app.get("/rooms")
def room_data(room_id: Optional[str] = None):
    global connection
    if connection is None:
        connection = connect_to_db()

    if room_id:
        result = get_room(room_id, connection)
        if result is None:
            raise fastapi.HTTPException(
                status_code=400, detail="room does not exist")
    else:
        result = get_rooms(connection)
        if result is None:
            raise fastapi.HTTPException(
                status_code=400, detail="No rooms exist")
    
    return result

#get number of buildings in database
@app.get("/building_count")
def building_count():
    global connection
    if connection is None:
        connection = connect_to_db()

    return get_buildings_count(connection)

#if no data provided,
#gets building name, # of rooms in that building, # of scans that has been made in that building,
# the total number of unique students that scanned in that building, and scans per day 
#else returns specified building data
@app.get("/buildings")
def building(building_id: Optional[str] = None):
    global connection
    if connection is None:
        connection = connect_to_db()
    
    if building_id:
        result = get_building(building_id, connection)
        if result is None:
            raise fastapi.HTTPException(
                status_code=400, detail="No buildings exist")
    else:
        result = get_buildings(connection)
        if result is None:
            raise fastapi.HTTPException(
                status_code=400, detail="Building does not exist")
    return result

#adds room
@app.post("/add_room")
def api_add_room(room_id: str, capacity: int, building_name: str, room_aspect_ratio: str):
    global connection
    if connection is None:
        connection = connect_to_db()

    response = add_room(room_id, capacity, building_name, room_aspect_ratio, connection)
    if response == -1:
        raise fastapi.HTTPException(
            status_code=400, detail="Room Id/Building name invalid, or room already exists, or invalid aspect ratio")
    return "Room Added"


@app.get(
    "/versions",
    response_model=List[str],
    tags=["versions"],
    responses={200: {"success": status.HTTP_200_OK}},
)
def versions():
    output = None
    if sys.platform == "linux":
        output = capture_stdout("/usr/local/bin/pip list")
    else:
        output = capture_stdout("poetry show --no-dev --no-ansi")

    return output.stdout.text.splitlines()
