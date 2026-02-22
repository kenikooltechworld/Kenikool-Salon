import logging
import pickle
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from cryptography.fernet import Fernet
import json

logger = logging.getLogger(__name__)


class LearningModel:
    """Learning model with feedback loop and local storage"""

    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize learning model"""
        self.model_data = {
            "booking_patterns": {},
            "service_preferences": {},
            "client_behavior": {},
            "staff_performance": {},
            "inventory_trends": {}
        }
        self.feedback_history = []
        self.model_version = "1.0"
        self.last_updated = datetime.utcnow().isoformat()
        self.cipher_suite = None
        
        if encryption_key:
            try:
                self.cipher_suite = Fernet(encryption_key)
            except Exception as e:
                logger.warning(f"Encryption key invalid: {e}")

    async def update_from_booking(
        self,
        booking_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update model from booking data"""
        try:
            # Extract patterns
            stylist_id = booking_data.get('stylist_id')
            client_id = booking_data.get('client_id')
            service_id = booking_data.get('service_id')
            duration = booking_data.get('duration', 0)
            
            # Update booking patterns
            if stylist_id not in self.model_data['booking_patterns']:
                self.model_data['booking_patterns'][stylist_id] = {
                    "total_bookings": 0,
                    "average_duration": 0,
                    "client_count": set()
                }
            
            pattern = self.model_data['booking_patterns'][stylist_id]
            pattern['total_bookings'] += 1
            pattern['average_duration'] = (
                (pattern['average_duration'] * (pattern['total_bookings'] - 1) + duration) /
                pattern['total_bookings']
            )
            pattern['client_count'].add(client_id)
            
            # Update service preferences
            if service_id not in self.model_data['service_preferences']:
                self.model_data['service_preferences'][service_id] = {
                    "total_bookings": 0,
                    "average_rating": 0
                }
            
            self.model_data['service_preferences'][service_id]['total_bookings'] += 1
            
            self.last_updated = datetime.utcnow().isoformat()
            logger.info(f"Model updated from booking: {booking_data.get('id')}")
            
            return {"success": True, "message": "Model updated from booking"}

        except Exception as e:
            logger.error(f"Booking model update failed: {e}")
            return {"error": str(e)}

    async def update_from_service_completion(
        self,
        completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update model from service completion"""
        try:
            client_id = completion_data.get('client_id')
            service_id = completion_data.get('service_id')
            rating = completion_data.get('rating', 0)
            
            # Update client behavior
            if client_id not in self.model_data['client_behavior']:
                self.model_data['client_behavior'][client_id] = {
                    "services_completed": 0,
                    "average_rating": 0,
                    "preferred_services": []
                }
            
            client_data = self.model_data['client_behavior'][client_id]
            client_data['services_completed'] += 1
            client_data['average_rating'] = (
                (client_data['average_rating'] * (client_data['services_completed'] - 1) + rating) /
                client_data['services_completed']
            )
            
            if service_id not in client_data['preferred_services']:
                client_data['preferred_services'].append(service_id)
            
            # Update service preferences
            if service_id in self.model_data['service_preferences']:
                self.model_data['service_preferences'][service_id]['average_rating'] = (
                    (self.model_data['service_preferences'][service_id]['average_rating'] + rating) / 2
                )
            
            self.last_updated = datetime.utcnow().isoformat()
            logger.info(f"Model updated from service completion: {completion_data.get('id')}")
            
            return {"success": True, "message": "Model updated from service completion"}

        except Exception as e:
            logger.error(f"Service completion model update failed: {e}")
            return {"error": str(e)}

    async def update_from_inventory_change(
        self,
        inventory_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update model from inventory changes"""
        try:
            item_id = inventory_data.get('item_id')
            quantity_change = inventory_data.get('quantity_change', 0)
            
            # Update inventory trends
            if item_id not in self.model_data['inventory_trends']:
                self.model_data['inventory_trends'][item_id] = {
                    "total_usage": 0,
                    "reorder_count": 0,
                    "average_reorder_quantity": 0
                }
            
            trend = self.model_data['inventory_trends'][item_id]
            
            if quantity_change < 0:  # Usage
                trend['total_usage'] += abs(quantity_change)
            else:  # Reorder
                trend['reorder_count'] += 1
                trend['average_reorder_quantity'] = (
                    (trend['average_reorder_quantity'] * (trend['reorder_count'] - 1) + quantity_change) /
                    trend['reorder_count']
                )
            
            self.last_updated = datetime.utcnow().isoformat()
            logger.info(f"Model updated from inventory change: {item_id}")
            
            return {"success": True, "message": "Model updated from inventory change"}

        except Exception as e:
            logger.error(f"Inventory model update failed: {e}")
            return {"error": str(e)}

    async def incorporate_feedback(
        self,
        feedback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Incorporate user feedback into model"""
        try:
            feedback_id = feedback_data.get('id')
            feedback_type = feedback_data.get('type')  # 'positive', 'negative', 'neutral'
            entity_id = feedback_data.get('entity_id')
            entity_type = feedback_data.get('entity_type')  # 'service', 'stylist', 'client'
            
            # Store feedback
            self.feedback_history.append({
                "id": feedback_id,
                "type": feedback_type,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "timestamp": datetime.utcnow().isoformat(),
                "incorporated": True
            })
            
            # Adjust model based on feedback
            if entity_type == 'service' and entity_id in self.model_data['service_preferences']:
                if feedback_type == 'positive':
                    self.model_data['service_preferences'][entity_id]['average_rating'] += 0.5
                elif feedback_type == 'negative':
                    self.model_data['service_preferences'][entity_id]['average_rating'] -= 0.5
            
            self.last_updated = datetime.utcnow().isoformat()
            logger.info(f"Feedback incorporated: {feedback_id}")
            
            return {"success": True, "message": "Feedback incorporated"}

        except Exception as e:
            logger.error(f"Feedback incorporation failed: {e}")
            return {"error": str(e)}

    async def save_model(self, filepath: str) -> Dict[str, Any]:
        """Save model to local storage with encryption"""
        try:
            # Prepare model data
            model_dict = {
                "model_data": self.model_data,
                "feedback_history": self.feedback_history,
                "model_version": self.model_version,
                "last_updated": self.last_updated
            }
            
            # Serialize
            serialized = pickle.dumps(model_dict)
            
            # Encrypt if cipher available
            if self.cipher_suite:
                encrypted = self.cipher_suite.encrypt(serialized)
                with open(filepath, 'wb') as f:
                    f.write(encrypted)
                logger.info(f"Encrypted model saved to {filepath}")
            else:
                with open(filepath, 'wb') as f:
                    f.write(serialized)
                logger.info(f"Model saved to {filepath}")
            
            return {"success": True, "filepath": filepath}

        except Exception as e:
            logger.error(f"Model save failed: {e}")
            return {"error": str(e)}

    async def load_model(self, filepath: str) -> Dict[str, Any]:
        """Load model from local storage"""
        try:
            if not os.path.exists(filepath):
                return {"error": "Model file not found"}
            
            with open(filepath, 'rb') as f:
                data = f.read()
            
            # Decrypt if cipher available
            if self.cipher_suite:
                try:
                    data = self.cipher_suite.decrypt(data)
                except Exception:
                    logger.warning("Decryption failed, attempting to load as plaintext")
            
            # Deserialize
            model_dict = pickle.loads(data)
            
            self.model_data = model_dict.get('model_data', {})
            self.feedback_history = model_dict.get('feedback_history', [])
            self.model_version = model_dict.get('model_version', '1.0')
            self.last_updated = model_dict.get('last_updated', datetime.utcnow().isoformat())
            
            logger.info(f"Model loaded from {filepath}")
            return {"success": True, "filepath": filepath}

        except Exception as e:
            logger.error(f"Model load failed: {e}")
            return {"error": str(e)}

    def get_model_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        return {
            "model_version": self.model_version,
            "last_updated": self.last_updated,
            "booking_patterns_count": len(self.model_data['booking_patterns']),
            "service_preferences_count": len(self.model_data['service_preferences']),
            "client_behavior_count": len(self.model_data['client_behavior']),
            "staff_performance_count": len(self.model_data['staff_performance']),
            "inventory_trends_count": len(self.model_data['inventory_trends']),
            "feedback_count": len(self.feedback_history)
        }

    def get_model_insights(self) -> Dict[str, Any]:
        """Get insights from model"""
        return {
            "top_services": sorted(
                self.model_data['service_preferences'].items(),
                key=lambda x: x[1].get('total_bookings', 0),
                reverse=True
            )[:5],
            "top_stylists": sorted(
                self.model_data['booking_patterns'].items(),
                key=lambda x: x[1].get('total_bookings', 0),
                reverse=True
            )[:5],
            "loyal_clients": sorted(
                self.model_data['client_behavior'].items(),
                key=lambda x: x[1].get('services_completed', 0),
                reverse=True
            )[:5]
        }
