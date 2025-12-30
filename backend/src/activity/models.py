from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from src.models import Base

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    activity_date = Column(Date, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    location = Column(String(200), nullable=True)
    estimated_cost = Column(Integer, nullable=True)
    actual_cost = Column(Integer, nullable=True)
    order_index = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    itinerary = relationship("Itinerary", back_populates="activities")
    destination = relationship("Destination", backref="activities")
    def __repr__(self):
        return f"<Activity(id={self.id}, title='{self.title}', date={self.activity_date})>"
