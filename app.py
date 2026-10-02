from fastapi import FastAPI
from pydantic import BaseModel
from database import engine, Base, SessionLocal
from models.user import User
from models.trip import Trip
from security import hash_password, verify_password
from auth import create_access_token
from models.destination import Destination
from models.place import Place
from models.trip_place import TripPlace


app = FastAPI(title="TripWise")

Base.metadata.create_all(bind=engine)


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


@app.get("/")
def home():
    return {
        "message": "Welcome to TripWise!"
    }


@app.get("/test-db")
def test_database():
    try:
        with engine.connect():
            return {
                "status": "success",
                "message": "TripWise connected to MySQL successfully!"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/register")
def register_user(user_data: RegisterRequest):

    db = SessionLocal()

    try:
        hashed_password = hash_password(user_data.password)

        new_user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "status": "success",
            "message": "User registered successfully!",
            "user_id": new_user.id
        }

    finally:
        db.close()
class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/login")
def login_user(login_data: LoginRequest):

    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.email == login_data.email
        ).first()

        if not user:
            return {
                "status": "error",
                "message": "Invalid email or password"
            }

        if not verify_password(
            login_data.password,
            user.password_hash
        ):
            return {
                "status": "error",
                "message": "Invalid email or password"
            }

        access_token = create_access_token(user.id)

        return {
            "status": "success",
            "message": "Login successful!",
            "user_id": user.id,
            "name": user.name,
            "access_token": access_token,
            "token_type": "bearer"
        }

    finally:
        db.close()

class TripCreateRequest(BaseModel):
    name: str
    description: str | None = None
    start_date: str | None = None
    end_date: str | None = None


@app.post("/trips")
def create_trip(trip_data: TripCreateRequest):

    db = SessionLocal()

    try:
        new_trip = Trip(
            user_id=1,
            name=trip_data.name,
            description=trip_data.description,
            start_date=trip_data.start_date,
            end_date=trip_data.end_date,
            status="planning"
        )

        db.add(new_trip)
        db.commit()
        db.refresh(new_trip)

        return {
            "status": "success",
            "message": "Trip created successfully!",
            "trip_id": new_trip.id
        }

    finally:
        db.close()

class DestinationCreateRequest(BaseModel):
    trip_id: int
    name: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    arrival_date: str | None = None
    departure_date: str | None = None
    order_index: int = 0
    notes: str | None = None


@app.post("/destinations")
def create_destination(data: DestinationCreateRequest):

    db = SessionLocal()

    try:
        destination = Destination(
            trip_id=data.trip_id,
            name=data.name,
            location=data.location,
            latitude=data.latitude,
            longitude=data.longitude,
            arrival_date=data.arrival_date,
            departure_date=data.departure_date,
            order_index=data.order_index,
            notes=data.notes
        )

        db.add(destination)
        db.commit()
        db.refresh(destination)

        return {
            "status": "success",
            "message": "Destination added successfully!",
            "destination_id": destination.id
        }

    finally:
        db.close()

class TripPlaceCreateRequest(BaseModel):
    trip_id: int
    place_id: int
    planned_date: str | None = None
    visit_status: str = "planned"
    personal_notes: str | None = None


@app.post("/trip-places")
def add_place_to_trip(data: TripPlaceCreateRequest):

    db = SessionLocal()

    try:
        trip_place = TripPlace(
            trip_id=data.trip_id,
            place_id=data.place_id,
            planned_date=data.planned_date,
            visit_status=data.visit_status,
            personal_notes=data.personal_notes
        )

        db.add(trip_place)
        db.commit()
        db.refresh(trip_place)

        return {
            "status": "success",
            "message": "Place added to trip successfully!",
            "trip_place_id": trip_place.id
        }

    finally:
        db.close()

class PlaceCreateRequest(BaseModel):
    name: str
    category: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    source: str = "user"


@app.post("/places")
def create_place(data: PlaceCreateRequest):

    db = SessionLocal()

    try:
        place = Place(
            name=data.name,
            category=data.category,
            address=data.address,
            latitude=data.latitude,
            longitude=data.longitude,
            description=data.description,
            source=data.source
        )

        db.add(place)
        db.commit()
        db.refresh(place)

        return {
            "status": "success",
            "message": "Place created successfully!",
            "place_id": place.id
        }

    finally:
        db.close()