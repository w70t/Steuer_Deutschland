"""Tax calculation model for storing calculation history"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from .user import Base


class TaxCalculation(Base):
    """Tax calculation history model"""
    __tablename__ = 'tax_calculations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Input parameters
    gross_income = Column(Float, nullable=False)
    tax_class = Column(Integer, nullable=False)
    children = Column(Integer, default=0)
    church_tax = Column(Boolean, default=False)
    state = Column(String(50), nullable=True)  # For state-specific calculations

    # Calculated results
    income_tax = Column(Float, nullable=False)
    solidarity_surcharge = Column(Float, default=0)
    church_tax_amount = Column(Float, default=0)
    health_insurance = Column(Float, default=0)
    pension_insurance = Column(Float, default=0)
    unemployment_insurance = Column(Float, default=0)
    care_insurance = Column(Float, default=0)
    total_deductions = Column(Float, nullable=False)
    net_income = Column(Float, nullable=False)

    # Metadata
    calculation_details = Column(JSON, nullable=True)  # Store detailed breakdown
    tax_year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TaxCalculation(user_id={self.user_id}, gross={self.gross_income}, net={self.net_income})>"
