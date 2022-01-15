from pydantic import BaseModel


class Student(BaseModel):
    first_name: str
    last_name: str
    email: str


class Scan(BaseModel):
    email: str
    room_id: str
