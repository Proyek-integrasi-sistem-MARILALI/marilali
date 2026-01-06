from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from src.models import Base

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=True, index=True)
    notification_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, index=True)
    priority = Column(String(20), default="normal")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", backref="notifications")
    itinerary = relationship("Itinerary", backref="notifications")
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.notification_type}', read={self.is_read})>"
