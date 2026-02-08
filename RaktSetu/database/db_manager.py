"""
Database Manager
Handles all database operations for BloodFlow AI
"""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

from database.models import (
    Donor, Donation, BloodInventory, DemandHistory, 
    BloodUnit, Notification, EmergencyEvent, 
    BlockchainRecord, PredictionLog, init_database
)


class DatabaseManager:
    """
    Central database manager for all operations
    """
    
    def __init__(self, db_path="sqlite:///bloodflow.db"):
        self.engine = init_database(db_path)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    # ==================== DONOR OPERATIONS ====================
    
    def get_all_donors(self) -> List[Dict]:
        """Get all donors"""
        session = self.get_session()
        try:
            donors = session.query(Donor).all()
            return [self._donor_to_dict(d) for d in donors]
        finally:
            session.close()
    
    def get_donor_by_id(self, donor_id: str) -> Optional[Dict]:
        """Get donor by ID"""
        session = self.get_session()
        try:
            donor = session.query(Donor).filter(Donor.donor_id == donor_id).first()
            return self._donor_to_dict(donor) if donor else None
        finally:
            session.close()
    
    def get_eligible_donors(self, blood_type: str = None) -> List[Dict]:
        """Get eligible donors (90+ days since last donation)"""
        session = self.get_session()
        try:
            ninety_days_ago = datetime.now() - timedelta(days=90)
            
            query = session.query(Donor).join(Donation).group_by(Donor.id).having(
                func.max(Donation.donation_date) <= ninety_days_ago
            )
            
            if blood_type:
                query = query.filter(Donor.blood_type == blood_type)
            
            donors = query.all()
            return [self._donor_to_dict(d) for d in donors]
        finally:
            session.close()
    
    def _donor_to_dict(self, donor: Donor) -> Dict:
        """Convert Donor object to dictionary"""
        if not donor:
            return None
        
        session = self.get_session()
        try:
            # Get donation count
            donation_count = session.query(Donation).filter(
                Donation.donor_id == donor.id
            ).count()
            
            # Get last donation
            last_donation = session.query(Donation).filter(
                Donation.donor_id == donor.id
            ).order_by(Donation.donation_date.desc()).first()
            
            days_since_last = None
            if last_donation:
                days_since_last = (datetime.now() - last_donation.donation_date).days
            
            return {
                'donor_id': donor.donor_id,
                'blood_type': donor.blood_type,
                'age': donor.age,
                'gender': donor.gender,
                'location': donor.location,
                'total_donations': donation_count,
                'last_donation_date': last_donation.donation_date if last_donation else None,
                'days_since_last_donation': days_since_last,
                'eligible': days_since_last >= 90 if days_since_last else True,
                'emergency_available': donor.emergency_available,
                'contact_preference': donor.contact_preference
            }
        finally:
            session.close()
    
    # ==================== INVENTORY OPERATIONS ====================
    
    def get_inventory_status(self, blood_type: str = None) -> List[Dict]:
        """Get current inventory status"""
        session = self.get_session()
        try:
            query = session.query(BloodInventory)
            if blood_type:
                query = query.filter(BloodInventory.blood_type == blood_type)
            
            inventories = query.all()
            return [self._inventory_to_dict(inv) for inv in inventories]
        finally:
            session.close()
    
    def update_inventory(self, blood_type: str, current_stock: int):
        """Update inventory stock level"""
        session = self.get_session()
        try:
            inventory = session.query(BloodInventory).filter(
                BloodInventory.blood_type == blood_type
            ).first()
            
            if inventory:
                inventory.current_stock = current_stock
                inventory.last_updated = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating inventory: {e}")
            return False
        finally:
            session.close()
    
    def _inventory_to_dict(self, inv: BloodInventory) -> Dict:
        """Convert BloodInventory to dictionary"""
        if not inv:
            return None
        
        return {
            'blood_type': inv.blood_type,
            'current_stock': inv.current_stock,
            'safety_stock': inv.safety_stock,
            'optimal_stock': inv.optimal_stock,
            'location': inv.location,
            'last_updated': inv.last_updated
        }
    
    # ==================== DEMAND HISTORY OPERATIONS ====================
    
    def get_demand_history(self, blood_type: str, days: int = 365) -> pd.DataFrame:
        """Get historical demand data for ML training"""
        session = self.get_session()
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            records = session.query(DemandHistory).filter(
                DemandHistory.blood_type == blood_type,
                DemandHistory.date >= start_date
            ).order_by(DemandHistory.date).all()
            
            data = [{
                'date': r.date,
                'demand': r.demand,
                'actual_usage': r.actual_usage,
                'day_of_week': r.day_of_week,
                'month': r.month,
                'is_weekend': r.is_weekend,
                'is_holiday': r.is_holiday
            } for r in records]
            
            return pd.DataFrame(data)
        finally:
            session.close()
    
    def add_demand_record(self, blood_type: str, date: datetime, demand: int):
        """Add a demand history record"""
        session = self.get_session()
        try:
            record = DemandHistory(
                date=date,
                blood_type=blood_type,
                demand=demand,
                day_of_week=date.weekday(),
                month=date.month,
                is_weekend=date.weekday() >= 5
            )
            session.add(record)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error adding demand record: {e}")
            return False
        finally:
            session.close()
    
    # ==================== NOTIFICATION OPERATIONS ====================
    
    def add_notification(self, notif_data: Dict):
        """Add notification to database"""
        session = self.get_session()
        try:
            notification = Notification(
                notification_type=notif_data.get('type'),
                recipient_type=notif_data.get('recipient_type', 'donor'),
                recipient_id=notif_data.get('recipient_id'),
                subject=notif_data.get('subject'),
                message=notif_data.get('message'),
                channel=notif_data.get('channel', 'email'),
                priority=notif_data.get('priority', 'medium'),
                status='sent'
            )
            session.add(notification)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error adding notification: {e}")
            return False
        finally:
            session.close()
    
    def get_notification_stats(self) -> Dict:
        """Get notification statistics"""
        session = self.get_session()
        try:
            total = session.query(Notification).count()
            
            by_type = {}
            types = session.query(Notification.notification_type, 
                                func.count(Notification.id)).group_by(
                                    Notification.notification_type).all()
            for notif_type, count in types:
                by_type[notif_type] = count
            
            return {
                'total': total,
                'by_type': by_type
            }
        finally:
            session.close()
    
    # ==================== EMERGENCY OPERATIONS ====================
    
    def create_emergency_event(self, event_type: str, severity: str, 
                               blood_types: List[str], description: str = None) -> int:
        """Create emergency event record"""
        session = self.get_session()
        try:
            event = EmergencyEvent(
                event_type=event_type,
                severity=severity,
                blood_types_needed=','.join(blood_types),
                description=description,
                status='active'
            )
            session.add(event)
            session.commit()
            return event.id
        except Exception as e:
            session.rollback()
            print(f"Error creating emergency event: {e}")
            return None
        finally:
            session.close()
    
    def update_emergency_event(self, event_id: int, donors_contacted: int = None, 
                               units_collected: int = None):
        """Update emergency event"""
        session = self.get_session()
        try:
            event = session.query(EmergencyEvent).filter(
                EmergencyEvent.id == event_id
            ).first()
            
            if event:
                if donors_contacted is not None:
                    event.donors_contacted = donors_contacted
                if units_collected is not None:
                    event.units_collected = units_collected
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating emergency event: {e}")
            return False
        finally:
            session.close()
    
    # ==================== BLOCKCHAIN OPERATIONS ====================
    
    def add_blockchain_record(self, block_index: int, block_hash: str, 
                             previous_hash: str, transaction_data: str):
        """Add blockchain record to database"""
        session = self.get_session()
        try:
            record = BlockchainRecord(
                block_index=block_index,
                block_hash=block_hash,
                previous_hash=previous_hash,
                data=transaction_data
            )
            session.add(record)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error adding blockchain record: {e}")
            return False
        finally:
            session.close()
    
    # ==================== STATISTICS ====================
    
    def get_database_stats(self) -> Dict:
        """Get overall database statistics"""
        session = self.get_session()
        try:
            stats = {
                'total_donors': session.query(Donor).count(),
                'total_donations': session.query(Donation).count(),
                'total_demand_records': session.query(DemandHistory).count(),
                'total_notifications': session.query(Notification).count(),
                'total_emergency_events': session.query(EmergencyEvent).count(),
                'total_blockchain_records': session.query(BlockchainRecord).count()
            }
            return stats
        finally:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()
