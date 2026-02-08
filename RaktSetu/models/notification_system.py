"""
Custom Smart Notification System
Context-aware, personalized notifications for donors and staff
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum


class NotificationType(Enum):
    """Types of notifications"""
    URGENCY = "urgency"
    PERSONALIZED = "personalized"
    LOCATION_AWARE = "location_aware"
    EVENT_TRIGGERED = "event_triggered"
    APPOINTMENT_REMINDER = "appointment_reminder"
    THANK_YOU = "thank_you"
    MILESTONE = "milestone"


class NotificationChannel(Enum):
    """Delivery channels"""
    SMS = "sms"
    EMAIL = "email"
    APP_PUSH = "app_push"
    WHATSAPP = "whatsapp"
    VOICE_CALL = "voice_call"


class NotificationPriority(Enum):
    """Priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SmartNotificationSystem:
    """
    Intelligent notification system
    
    Features:
    - Context-aware messaging
    - Anti-spam protection
    - Personalization
    - Multi-channel delivery
    - A/B testing capability
    """
    
    def __init__(self):
        self.notification_history = []
        self.spam_protection_hours = 24  # Don't contact same donor within 24h
        self.max_notifications_per_week = 3
    
    def create_urgency_notification(self, blood_type: str, units_needed: int,
                                   location: str, urgency: str) -> Dict:
        """
        Create urgent shortage notification
        
        Examples:
        - "O- shortage: Need 15 units in next 48 hours"
        - "Critical: AB- needed for emergency surgery"
        """
        urgency_messages = {
            "critical": f"🚨 CRITICAL: We urgently need {units_needed} units of {blood_type} blood at {location}. Lives depend on you!",
            "high": f"⚠️ URGENT: {blood_type} blood shortage predicted. We need {units_needed} units within 72 hours.",
            "medium": f"📢 NOTICE: {blood_type} stock is low. We need {units_needed} units this week.",
            "low": f"📋 REMINDER: {blood_type} donations welcome. Current need: {units_needed} units."
        }
        
        return {
            "type": NotificationType.URGENCY.value,
            "priority": urgency,
            "blood_type": blood_type,
            "subject": f"{urgency.upper()}: {blood_type} Blood Needed",
            "message": urgency_messages.get(urgency.lower(), urgency_messages["medium"]),
            "units_needed": units_needed,
            "location": location,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=72)).isoformat(),
            "call_to_action": "Donate Now",
            "channels": [NotificationChannel.SMS.value, NotificationChannel.APP_PUSH.value]
        }
    
    def create_personalized_notification(self, donor_id: str, donor_name: str,
                                        blood_type: str, last_donation_days: int) -> Dict:
        """
        Create personalized donor notification
        
        Examples:
        - "Hi John, it's been 120 days since your last donation. Ready to save lives again?"
        - "Sarah, your rare AB- blood type is needed this week!"
        """
        if last_donation_days >= 90 and last_donation_days <= 120:
            # Eligible and good timing
            message = (f"Hi! It's been {last_donation_days} days since your last donation. "
                      f"You're eligible to donate again and your {blood_type} blood can save lives! 🩸")
        elif last_donation_days > 365:
            # Re-engagement
            message = (f"We miss you! It's been over a year since your last donation. "
                      f"Your {blood_type} blood is valuable - come back and save lives! ❤️")
        elif last_donation_days < 90:
            # Thank you / not eligible yet
            days_until_eligible = 90 - last_donation_days
            message = (f"Thank you for your recent donation! You can donate again in "
                      f"{days_until_eligible} days. We'll remind you! 🙏")
        else:
            # General
            message = f"Your {blood_type} blood is valuable. Schedule your next donation today!"
        
        return {
            "type": NotificationType.PERSONALIZED.value,
            "priority": NotificationPriority.MEDIUM.value,
            "donor_id": donor_id,
            "subject": "Time to Donate Again?",
            "message": message,
            "blood_type": blood_type,
            "personalization": {
                "donor_name": donor_name,
                "days_since_last": last_donation_days,
                "eligible": last_donation_days >= 90
            },
            "created_at": datetime.now().isoformat(),
            "call_to_action": "Book Appointment",
            "channels": [NotificationChannel.EMAIL.value, NotificationChannel.APP_PUSH.value]
        }
    
    def create_location_aware_notification(self, donor_location: str, 
                                          nearby_centers: List[str],
                                          blood_type: str) -> Dict:
        """
        Location-based notifications
        
        Examples:
        - "Blood drive 2 km from your location this Saturday!"
        - "Your local blood bank has an urgent need for O+ blood"
        """
        nearest_center = nearby_centers[0] if nearby_centers else "your nearest blood bank"
        
        message = (f"📍 {blood_type} blood needed at {nearest_center} in {donor_location}. "
                  f"Donate at a location near you this week!")
        
        return {
            "type": NotificationType.LOCATION_AWARE.value,
            "priority": NotificationPriority.MEDIUM.value,
            "subject": f"Blood Needed Near You - {donor_location}",
            "message": message,
            "blood_type": blood_type,
            "location_info": {
                "donor_location": donor_location,
                "nearby_centers": nearby_centers,
                "distance": "2-5 km"
            },
            "created_at": datetime.now().isoformat(),
            "call_to_action": "Find Nearest Center",
            "channels": [NotificationChannel.APP_PUSH.value, NotificationChannel.SMS.value]
        }
    
    def create_event_notification(self, event_type: str, blood_types_needed: List[str],
                                  impact_description: str) -> Dict:
        """
        Event-triggered notifications
        
        Examples:
        - "Major accident on Highway 5: Emergency blood drive activated"
        - "Dengue outbreak: High demand for platelets and all blood types"
        """
        event_messages = {
            "accident": f"🚨 EMERGENCY: Major accident reported. Urgent need for {', '.join(blood_types_needed)}. {impact_description}",
            "disaster": f"⚠️ DISASTER RESPONSE: {impact_description}. All blood types needed urgently.",
            "outbreak": f"📊 HEALTH ALERT: {impact_description}. Increased need for {', '.join(blood_types_needed)}.",
            "festival": f"🎉 FESTIVAL ALERT: {impact_description}. Stock up needed for {', '.join(blood_types_needed)}."
        }
        
        message = event_messages.get(event_type, event_messages["accident"])
        
        return {
            "type": NotificationType.EVENT_TRIGGERED.value,
            "priority": NotificationPriority.CRITICAL.value if event_type in ["accident", "disaster"] else NotificationPriority.HIGH.value,
            "event_type": event_type,
            "subject": f"URGENT: {event_type.title()} - Blood Needed",
            "message": message,
            "blood_types_needed": blood_types_needed,
            "impact": impact_description,
            "created_at": datetime.now().isoformat(),
            "call_to_action": "Emergency Donate",
            "channels": [NotificationChannel.SMS.value, NotificationChannel.APP_PUSH.value, NotificationChannel.VOICE_CALL.value]
        }
    
    def create_appointment_reminder(self, donor_name: str, appointment_date: str,
                                   appointment_time: str, location: str) -> Dict:
        """
        Appointment reminder notifications
        
        Sent 24h and 2h before appointment
        """
        message = (f"👋 Hi {donor_name}! Reminder: You have a blood donation appointment "
                  f"tomorrow at {appointment_time} at {location}. See you there!")
        
        return {
            "type": NotificationType.APPOINTMENT_REMINDER.value,
            "priority": NotificationPriority.MEDIUM.value,
            "subject": "Donation Appointment Reminder",
            "message": message,
            "appointment_info": {
                "date": appointment_date,
                "time": appointment_time,
                "location": location
            },
            "created_at": datetime.now().isoformat(),
            "call_to_action": "Confirm Appointment",
            "channels": [NotificationChannel.SMS.value, NotificationChannel.EMAIL.value]
        }
    
    def create_thank_you_notification(self, donor_name: str, blood_type: str,
                                     donation_date: str, lives_impacted: int = 3) -> Dict:
        """
        Thank you and impact notification
        
        Sent after donation to show appreciation and impact
        """
        message = (f"🙏 Thank you, {donor_name}! Your {blood_type} donation on {donation_date} "
                  f"can help save up to {lives_impacted} lives. You're a hero! ❤️")
        
        return {
            "type": NotificationType.THANK_YOU.value,
            "priority": NotificationPriority.LOW.value,
            "subject": "Thank You for Saving Lives!",
            "message": message,
            "donation_info": {
                "blood_type": blood_type,
                "date": donation_date,
                "estimated_lives_saved": lives_impacted
            },
            "created_at": datetime.now().isoformat(),
            "call_to_action": "Share Your Impact",
            "channels": [NotificationChannel.EMAIL.value, NotificationChannel.APP_PUSH.value]
        }
    
    def create_milestone_notification(self, donor_name: str, total_donations: int,
                                     blood_type: str) -> Dict:
        """
        Milestone celebration notifications
        
        Sent at 5, 10, 25, 50, 100 donations
        """
        milestone_messages = {
            5: f"🎉 Congratulations {donor_name}! You've completed 5 donations! You're making a real difference!",
            10: f"🏆 Amazing milestone, {donor_name}! 10 donations means you've potentially saved 30 lives!",
            25: f"🌟 Incredible {donor_name}! 25 donations - you're a true lifesaver! Up to 75 lives impacted!",
            50: f"👑 {donor_name}, you're a LEGEND! 50 donations could have saved 150+ lives!",
            100: f"💎 {donor_name}, you've reached 100 donations! You've helped save 300+ lives. You're a superhero!"
        }
        
        message = milestone_messages.get(total_donations, 
            f"🎊 {donor_name}, you've completed {total_donations} donations! Thank you for your commitment!")
        
        return {
            "type": NotificationType.MILESTONE.value,
            "priority": NotificationPriority.LOW.value,
            "subject": f"Milestone Achieved: {total_donations} Donations!",
            "message": message,
            "milestone_info": {
                "total_donations": total_donations,
                "blood_type": blood_type,
                "estimated_lives_saved": total_donations * 3
            },
            "created_at": datetime.now().isoformat(),
            "call_to_action": "Share Your Achievement",
            "channels": [NotificationChannel.EMAIL.value, NotificationChannel.APP_PUSH.value]
        }
    
    def check_spam_protection(self, donor_id: str, notification_type: str) -> bool:
        """
        Check if we can send notification without spamming
        
        Returns True if OK to send, False if would be spam
        """
        # Get recent notifications to this donor
        recent = [n for n in self.notification_history 
                 if n.get("donor_id") == donor_id]
        
        if not recent:
            return True  # No history, OK to send
        
        # Check 24-hour rule
        last_notification = max(recent, key=lambda x: x.get("created_at", ""))
        last_time = datetime.fromisoformat(last_notification.get("created_at", datetime.now().isoformat()))
        
        if (datetime.now() - last_time).total_seconds() < self.spam_protection_hours * 3600:
            # Exception for critical notifications
            if notification_type == NotificationType.URGENCY.value:
                return True
            return False
        
        # Check weekly limit
        week_ago = datetime.now() - timedelta(days=7)
        recent_week = [n for n in recent 
                      if datetime.fromisoformat(n.get("created_at", "")) > week_ago]
        
        if len(recent_week) >= self.max_notifications_per_week:
            return False
        
        return True
    
    def send_notification(self, notification: Dict) -> Dict:
        """
        Send notification through specified channels
        
        In production, this would integrate with Twilio, SendGrid, Firebase, etc.
        """
        # Add to history
        self.notification_history.append(notification)
        
        # Simulate sending
        return {
            "status": "sent",
            "notification_id": f"NOTIF-{len(self.notification_history):06d}",
            "channels_used": notification.get("channels", []),
            "sent_at": datetime.now().isoformat(),
            "estimated_delivery": "immediate"
        }
    
    def get_notification_analytics(self) -> Dict:
        """Get analytics on notification performance"""
        total = len(self.notification_history)
        
        if total == 0:
            return {"total_sent": 0, "message": "No notifications sent yet"}
        
        by_type = {}
        by_priority = {}
        by_channel = {}
        
        for notif in self.notification_history:
            notif_type = notif.get("type", "unknown")
            priority = notif.get("priority", "unknown")
            
            by_type[notif_type] = by_type.get(notif_type, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            for channel in notif.get("channels", []):
                by_channel[channel] = by_channel.get(channel, 0) + 1
        
        return {
            "total_sent": total,
            "by_type": by_type,
            "by_priority": by_priority,
            "by_channel": by_channel,
            "average_per_day": round(total / max((datetime.now() - datetime(2024, 1, 1)).days, 1), 2)
        }
