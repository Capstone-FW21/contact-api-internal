from sqlite3 import connect
from ctdb_utility_lib.utility import add_room, connect_to_db, get_person
from ctdb_utility_lib.admin_utility import retrieve_records, retrieve_user_records, retrieve_contacts, get_people, get_records_count, get_rooms, get_buildings, connect_to_db
import fastapi
import sys
from fastapi import FastAPI, status
from typing import List
from sarge import capture_stdout
from enum import Enum


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
@app.get("/user_records/")
def records():
    global connection
    if connection is None:
        connection = connect_to_db()
    
    records = retrieve_records(connection)
    if records is None:
        raise fastapi.HTTPException(
            status_code=400, detail="There are no scans")
    return records

#returns scans for a specific email adress
@app.get("/user_records/")
def user_records(email: str, limit: int):
    global connection
    if connection is None:
        connection = connect_to_db()

    user_record = retrieve_user_records(email, connection)
    if user_record == None:
        raise fastapi.HTTPException(
            status_code=400, detail="There are no scans for this person")
    if user_record == -1:
        raise fastapi.HTTPException(
            status_code=400, detail="Invalid email address")

    return user_record

#returns all people in contact with email address
@app.get("/breakout/")
def breakout(email: str, date: str):
    contacted = retrieve_contacts(email, date, connection)
    if contacted == -1:
        raise fastapi.HTTPException(
            status_code=400, detail="Invalid email format, or date is greater than 14 days ago")

    return contacted

#returns all entries for specific type
@app.get("/stats/")
def stats(stat_type: StatTypes):
    global connection
    if connection is None:
        connection = connect_to_db()

    match stat_type:
        case 'student':
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

#adds room
@app.get("/add_room/")
def add_room(room_id: str, capacity: int, building_name: str):
    global connection
    if connection is None:
        connection = connect_to_db()

    response = add_room(room_id, capacity, building_name)
    if response == -1:
        raise fastapi.HTTPException(
            status_code=400, detail="Room Id/Building name invalid, or room already exists")
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
