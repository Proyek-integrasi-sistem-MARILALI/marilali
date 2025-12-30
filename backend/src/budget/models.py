from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from src.models import Base

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Integer, nullable=False)
    expense_date = Column(Date, nullable=False)
    payment_method = Column(String(50), nullable=True)
    receipt_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    itinerary = relationship("Itinerary", back_populates="expenses")
    activity = relationship("Activity", backref="expenses")
    def __repr__(self):
        return f"<Expense(id={self.id}, category='{self.category}', amount={self.amount})>"

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, func
from sqlalchemy.orm import relationship
from src.models import Base

class BudgetAlert(Base):
    __tablename__ = "budget_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Alert configuration
    alert_type = Column(String(50), nullable=False)  # threshold_warning, threshold_exceeded, daily_summary
    threshold_percentage = Column(Float, nullable=True)  # 50, 75, 90, 100
    threshold_amount = Column(Integer, nullable=True)
    
    # Budget status
    total_budget = Column(Integer, nullable=False)
    current_spent = Column(Integer, nullable=False)
    remaining_budget = Column(Integer, nullable=False)
    percentage_used = Column(Float, nullable=False)
    
    # Alert details
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="info")  # info, warning, critical
    recommendation = Column(Text, nullable=True)  # AI-generated budget advice
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="budget_alerts")
    itinerary = relationship("Itinerary", backref="budget_alerts")


class BudgetRecommendation(Base):
    __tablename__ = "budget_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Recommendation details
    recommendation_type = Column(String(50), nullable=False)  # cost_saving, alternative_option, budget_reallocation
    category = Column(String(50), nullable=True)  # transportation, accommodation, activities, food
    
    # Financial impact
    current_cost = Column(Integer, nullable=True)
    suggested_cost = Column(Integer, nullable=True)
    potential_savings = Column(Integer, nullable=True)
    
    # Suggestion details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    alternative_options = Column(Text, nullable=True)
    impact_analysis = Column(Text, nullable=True)
    
    # AI context
    confidence_score = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    
    # User interaction
    is_viewed = Column(Boolean, default=False)
    is_accepted = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    user_feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="budget_recommendations")
    itinerary = relationship("Itinerary", backref="budget_recommendations")
    
