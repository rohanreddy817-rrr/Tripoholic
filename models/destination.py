from sqlalchemy import Column, Integer, String, Text, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)

    trip_id = Column(
        Integer,
        ForeignKey("trips.id"),
        nullable=False
    )

    name = Column(String(150), nullable=False)
    location = Column(String(255), nullable=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    arrival_date = Column(Date, nullable=True)
    departure_date = Column(Date, nullable=True)

    order_index = Column(Integer, nullable=False, default=0)

    notes = Column(Text, nullable=True)

    trip = relationship("Trip", backref="destinations")