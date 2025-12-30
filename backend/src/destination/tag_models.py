from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, func
from sqlalchemy.orm import relationship
from src.models import Base

# Association tables for many-to-many relationships
destination_tags = Table(
    'destination_tags',
    Base.metadata,
    Column('destination_id', Integer, ForeignKey('destinations.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

itinerary_tags = Table(
    'itinerary_tags',
    Base.metadata,
    Column('itinerary_id', Integer, ForeignKey('itineraries.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=True)  # destination_tag, itinerary_tag, general
    description = Column(String(255), nullable=True)
    color = Column(String(20), nullable=True)  # for UI display
    icon = Column(String(50), nullable=True)  # icon name or code
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships (defined in respective models)
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"
