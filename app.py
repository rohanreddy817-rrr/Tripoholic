from datetime import date, datetime

from fastapi import FastAPI, Depends, HTTPException, status, Query
from pydantic import BaseModel

from database import engine, Base, SessionLocal
from models.user import User
from models.trip import Trip
from models.destination import Destination
from models.place import Place
from models.trip_place import TripPlace

from security import hash_password, verify_password
from auth import create_access_token
from core.dependencies import get_current_user
from services.place_service import search_india_places


app = FastAPI(title="Tripoholic")

Base.metadata.create_all(bind=engine)


# ============================================================
# REQUEST MODELS
# ============================================================

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TripCreateRequest(BaseModel):
    name: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class DestinationCreateRequest(BaseModel):
    trip_id: int
    name: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    arrival_date: date | None = None
    departure_date: date | None = None
    order_index: int = 0
    notes: str | None = None


class TripPlaceCreateRequest(BaseModel):
    trip_id: int
    place_id: int
    planned_date: datetime | None = None
    visit_status: str = "planned"
    personal_notes: str | None = None


class PlaceCreateRequest(BaseModel):
    name: str
    category: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    source: str = "user"


# ============================================================
# BASIC ROUTES
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Welcome to Tripoholic!"
    }


@app.get("/test-db")
def test_database():
    try:
        with engine.connect():
            return {
                "status": "success",
                "message": "Tripoholic connected to MySQL successfully!"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# AUTHENTICATION
# ============================================================

@app.post("/register")
def register_user(user_data: RegisterRequest):

    db = SessionLocal()

    try:
        existing_user = db.query(User).filter(
            User.email == user_data.email
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered"
            )

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


@app.post("/login")
def login_user(login_data: LoginRequest):

    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.email == login_data.email
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(
            login_data.password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

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


# ============================================================
# TRIPS
# ============================================================

@app.post("/trips")
def create_trip(
    trip_data: TripCreateRequest,
    current_user: User = Depends(get_current_user)
):

    db = SessionLocal()

    try:
        new_trip = Trip(
            user_id=current_user.id,
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


# ============================================================
# DESTINATIONS
# ============================================================

@app.post("/destinations")
def create_destination(
    data: DestinationCreateRequest,
    current_user: User = Depends(get_current_user)
):

    db = SessionLocal()

    try:
        trip = db.query(Trip).filter(
            Trip.id == data.trip_id,
            Trip.user_id == current_user.id
        ).first()

        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found or access denied"
            )

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


# ============================================================
# PLACES
# ============================================================

@app.post("/places")
def create_place(
    data: PlaceCreateRequest,
    current_user: User = Depends(get_current_user)
):

    db = SessionLocal()

    try:
        place = Place(
            name=data.name,
            category=data.category,
            address=data.address,
            latitude=data.latitude,
            longitude=data.longitude,
            description=data.description,
            source=data.source,
            created_by_user_id=current_user.id
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

# ============================================================
# INDIA-WIDE PLACE SEARCH
# ============================================================

@app.get("/places/search")
async def search_places_endpoint(
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(10, ge=1, le=20),
    current_user: User = Depends(get_current_user)
):
    try:
        places = await search_india_places(
            query=q,
            limit=limit
        )

        return {
            "status": "success",
            "country": "India",
            "query": q,
            "count": len(places),
            "places": places
        }

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail="Place search service is temporarily unavailable"
        )

# ============================================================
# ADD PLACE TO TRIP
# ============================================================

@app.post("/trip-places")
def add_place_to_trip(
    data: TripPlaceCreateRequest,
    current_user: User = Depends(get_current_user)
):

    db = SessionLocal()

    try:
        # Check that the trip belongs to the logged-in user
        trip = db.query(Trip).filter(
            Trip.id == data.trip_id,
            Trip.user_id == current_user.id
        ).first()

        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found or access denied"
            )

        # Check that the place exists
        place = db.query(Place).filter(
            Place.id == data.place_id
        ).first()

        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )

        # Prevent duplicate place entries in the same trip
        existing_trip_place = db.query(TripPlace).filter(
            TripPlace.trip_id == data.trip_id,
            TripPlace.place_id == data.place_id
        ).first()

        if existing_trip_place:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Place is already added to this trip"
            )

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

# ============================================================
# TRIP MANAGEMENT
# ============================================================

class TripUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None


@app.get("/trips")
def get_my_trips(
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        trips = db.query(Trip).filter(
            Trip.user_id == current_user.id
        ).order_by(Trip.created_at.desc()).all()

        return {
            "status": "success",
            "count": len(trips),
            "trips": [
                {
                    "id": trip.id,
                    "name": trip.name,
                    "description": trip.description,
                    "start_date": trip.start_date,
                    "end_date": trip.end_date,
                    "status": trip.status,
                    "created_at": trip.created_at
                }
                for trip in trips
            ]
        }

    finally:
        db.close()


@app.get("/trips/{trip_id}")
def get_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        trip = db.query(Trip).filter(
            Trip.id == trip_id,
            Trip.user_id == current_user.id
        ).first()

        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found or access denied"
            )

        return {
            "status": "success",
            "trip": {
                "id": trip.id,
                "name": trip.name,
                "description": trip.description,
                "start_date": trip.start_date,
                "end_date": trip.end_date,
                "status": trip.status,
                "created_at": trip.created_at
            }
        }

    finally:
        db.close()


@app.put("/trips/{trip_id}")
def update_trip(
    trip_id: int,
    trip_data: TripUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        trip = db.query(Trip).filter(
            Trip.id == trip_id,
            Trip.user_id == current_user.id
        ).first()

        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found or access denied"
            )

        update_data = trip_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(trip, field, value)

        db.commit()
        db.refresh(trip)

        return {
            "status": "success",
            "message": "Trip updated successfully!",
            "trip_id": trip.id
        }

    finally:
        db.close()


@app.delete("/trips/{trip_id}")
def delete_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        trip = db.query(Trip).filter(
            Trip.id == trip_id,
            Trip.user_id == current_user.id
        ).first()

        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found or access denied"
            )

        db.delete(trip)
        db.commit()

        return {
            "status": "success",
            "message": "Trip deleted successfully!"
        }

    finally:
        db.close()