
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from src.models import Base

class Media(Base):
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # destination, itinerary, activity, review
    entity_id = Column(Integer, nullable=False, index=True)
    media_type = Column(String(50), nullable=False)  # image, video, document
    file_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)  # in bytes
    mime_type = Column(String(100), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    caption = Column(String(500), nullable=True)
    alt_text = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="media")
    
    def __repr__(self):
        return f"<Media(id={self.id}, type='{self.media_type}', entity='{self.entity_type}:{self.entity_id}')>"
