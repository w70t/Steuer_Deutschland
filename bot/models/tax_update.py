"""Tax update model for tracking tax law changes"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from .user import Base


class TaxUpdate(Base):
    """Tax update tracking model"""
    __tablename__ = 'tax_updates'

    id = Column(Integer, primary_key=True)

    # Update information
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    source_url = Column(String(1000), nullable=False)
    source_name = Column(String(200), nullable=False)  # BMF, BZST, etc.

    # Update content
    update_type = Column(String(100), nullable=False)  # tax_rate, allowance, social_security, etc.
    changes = Column(JSON, nullable=False)  # Detailed changes in JSON format
    effective_date = Column(DateTime, nullable=True)  # When the change takes effect

    # Status tracking
    detected_at = Column(DateTime, default=datetime.utcnow)
    admin_notified = Column(Boolean, default=False)
    admin_notified_at = Column(DateTime, nullable=True)
    approved_by_admin = Column(Boolean, default=False)
    approved_at = Column(DateTime, nullable=True)
    applied = Column(Boolean, default=False)
    applied_at = Column(DateTime, nullable=True)

    # Admin notes
    admin_notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<TaxUpdate(title={self.title}, applied={self.applied})>"
