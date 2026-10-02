from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class TripPlace(Base):
    __tablename__ = "trip_places"

    id = Column(Integer, primary_key=True, index=True)

    trip_id = Column(
        Integer,
        ForeignKey("trips.id"),
        nullable=False
    )

    place_id = Column(
        Integer,
        ForeignKey("places.id"),
        nullable=False
    )

    planned_date = Column(DateTime, nullable=True)

    visit_status = Column(
        String(30),
        nullable=False,
        default="planned"
    )

    personal_notes = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    trip = relationship("Trip", backref="trip_places")
    place = relationship("Place", backref="trip_places")