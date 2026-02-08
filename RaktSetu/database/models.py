"""
Database Models for BloodFlow AI
SQLAlchemy ORM models for persistent storage
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class Donor(Base):
    """Donor information table"""
    __tablename__ = 'donors'
    
    id = Column(Integer, primary_key=True)
    donor_id = Column(String(50), unique=True, nullable=False)
    blood_type = Column(String(5), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    location = Column(String(100))
    contact_preference = Column(String(20))
    phone = Column(String(20))
    email = Column(String(100))
    emergency_available = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    donations = relationship("Donation", back_populates="donor")


class Donation(Base):
    """Donation history table"""
    __tablename__ = 'donations'
    
    id = Column(Integer, primary_key=True)
    donor_id = Column(Integer, ForeignKey('donors.id'), nullable=False)
    donation_date = Column(DateTime, nullable=False)
    blood_type = Column(String(5), nullable=False)
    volume_ml = Column(Integer, default=450)
    location = Column(String(100))
    
    # Relationships
    donor = relationship("Donor", back_populates="donations")


class BloodInventory(Base):
    """Current blood inventory table"""
    __tablename__ = 'blood_inventory'
    
    id = Column(Integer, primary_key=True)
    blood_type = Column(String(5), nullable=False, unique=True)
    current_stock = Column(Integer, default=0)
    safety_stock = Column(Integer, nullable=False)
    optimal_stock = Column(Integer, nullable=False)
    location = Column(String(100), default="Main Blood Bank")
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BloodUnit(Base):
    """Individual blood unit tracking"""
    __tablename__ = 'blood_units'
    
    id = Column(Integer, primary_key=True)
    unit_id = Column(String(50), unique=True, nullable=False)
    blood_type = Column(String(5), nullable=False)
    donor_id = Column(Integer, ForeignKey('donors.id'))
    collection_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='available')  # available, reserved, used, expired
    location = Column(String(100))
    blockchain_hash = Column(String(256))
    created_at = Column(DateTime, default=datetime.now)


class DemandHistory(Base):
    """Historical demand data for ML training"""
    __tablename__ = 'demand_history'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    blood_type = Column(String(5), nullable=False)
    demand = Column(Integer, nullable=False)
    actual_usage = Column(Integer)
    location = Column(String(100), default="Main Blood Bank")
    day_of_week = Column(Integer)
    month = Column(Integer)
    is_weekend = Column(Boolean)
    is_holiday = Column(Boolean, default=False)
    weather_condition = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)


class Notification(Base):
    """Notification history table"""
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    notification_type = Column(String(50), nullable=False)
    recipient_type = Column(String(50))  # donor, staff, hospital
    recipient_id = Column(String(100))
    subject = Column(String(200))
    message = Column(Text, nullable=False)
    channel = Column(String(20))  # sms, email, app_push, whatsapp
    priority = Column(String(20))  # critical, high, medium, low
    status = Column(String(20), default='sent')  # sent, delivered, failed
    sent_at = Column(DateTime, default=datetime.now)
    delivered_at = Column(DateTime)


class EmergencyEvent(Base):
    """Emergency event tracking"""
    __tablename__ = 'emergency_events'
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False)  # accident, disaster, outbreak
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    description = Column(Text)
    blood_types_needed = Column(String(100))  # Comma-separated
    units_needed = Column(Integer)
    donors_contacted = Column(Integer)
    units_collected = Column(Integer, default=0)
    status = Column(String(20), default='active')  # active, resolved, closed
    activated_at = Column(DateTime, default=datetime.now)
    resolved_at = Column(DateTime)


class BlockchainRecord(Base):
    """Blockchain transaction records"""
    __tablename__ = 'blockchain_records'
    
    id = Column(Integer, primary_key=True)
    block_index = Column(Integer, nullable=False)
    block_hash = Column(String(256), nullable=False)
    previous_hash = Column(String(256), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    transaction_type = Column(String(50))  # COLLECTION, TESTING, STORAGE, TRANSFER, TRANSFUSION
    unit_id = Column(String(50))
    data = Column(Text)  # JSON string of transaction data
    nonce = Column(Integer, default=0)


class PredictionLog(Base):
    """ML prediction logging for monitoring"""
    __tablename__ = 'prediction_logs'
    
    id = Column(Integer, primary_key=True)
    blood_type = Column(String(5), nullable=False)
    prediction_date = Column(DateTime, nullable=False)
    predicted_demand = Column(Integer, nullable=False)
    actual_demand = Column(Integer)
    confidence_score = Column(Float)
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)


# Database initialization
def init_database(db_path="sqlite:///bloodflow.db"):
    """Initialize database and create all tables"""
    engine = create_engine(db_path, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get database session"""
    Session = sessionmaker(bind=engine)
    return Session()


# Helper functions
def populate_initial_data(session):
    """Populate database with initial configuration data"""
    
    # Check if inventory already exists
    existing_inventory = session.query(BloodInventory).first()
    if existing_inventory:
        print("Database already populated, skipping initial data...")
        return
    
    print("Populating initial inventory data...")
    
    # Initial inventory settings
    blood_types_config = {
        "O+": {"safety": 50, "optimal": 80},
        "A+": {"safety": 40, "optimal": 70},
        "B+": {"safety": 30, "optimal": 50},
        "O-": {"safety": 25, "optimal": 40},
        "A-": {"safety": 20, "optimal": 35},
        "AB+": {"safety": 15, "optimal": 25},
        "B-": {"safety": 12, "optimal": 20},
        "AB-": {"safety": 10, "optimal": 15}
    }
    
    for blood_type, config in blood_types_config.items():
        inventory = BloodInventory(
            blood_type=blood_type,
            current_stock=0,  # Will be updated from Kaggle data
            safety_stock=config["safety"],
            optimal_stock=config["optimal"]
        )
        session.add(inventory)
    
    session.commit()
    print("✓ Initial inventory data added")


if __name__ == "__main__":
    # Test database creation
    print("Creating database...")
    engine = init_database()
    session = get_session(engine)
    populate_initial_data(session)
    print("✓ Database created successfully!")
    print(f"✓ Tables created: {', '.join(Base.metadata.tables.keys())}")
