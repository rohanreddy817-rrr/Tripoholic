from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)

    # External provider information
    external_place_id = Column(String(255), nullable=True, index=True)
    source = Column(String(50), nullable=False, default="user")

    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    description = Column(Text, nullable=True)

    # If this is a user-created private place
    created_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    creator = relationship("User", backref="created_places")