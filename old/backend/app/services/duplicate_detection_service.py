from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.client import Client
from app.database import db

class DuplicateDetectionService:
    """Service for detecting and managing duplicate client records."""
    
    SIMILARITY_THRESHOLD = 0.85
    MERGE_UNDO_WINDOW = timedelta(hours=24)
    
    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """Calculate similarity between two strings using SequenceMatcher."""
        if not str1 or not str2:
            return 0.0
        str1 = str(str1).lower().strip()
        str2 = str(str2).lower().strip()
        return SequenceMatcher(None, str1, str2).ratio()
    
    @staticmethod
    def find_duplicates(tenant_id: str, min_similarity: float = 0.85) -> List[Dict]:
        """Find potential duplicate client pairs."""
        clients = list(db.clients.find({"tenant_id": tenant_id}))
        duplicates = []
        
        for i, client1 in enumerate(clients):
            for client2 in clients[i+1:]:
                scores = {
                    "name": DuplicateDetectionService.calculate_similarity(
                        client1.get("name", ""), client2.get("name", "")
                    ),
                    "phone": DuplicateDetectionService.calculate_similarity(
                        str(client1.get("phone", "")), str(client2.get("phone", ""))
                    ),
                    "email": DuplicateDetectionService.calculate_similarity(
                        client1.get("email", ""), client2.get("email", "")
                    ),
                }
                
                avg_similarity = sum(scores.values()) / len(scores)
                
                if avg_similarity >= min_similarity:
                    duplicates.append({
                        "client1_id": str(client1["_id"]),
                        "client2_id": str(client2["_id"]),
                        "client1": {
                            "name": client1.get("name"),
                            "phone": client1.get("phone"),
                            "email": client1.get("email"),
                        },
                        "client2": {
                            "name": client2.get("name"),
                            "phone": client2.get("phone"),
                            "email": client2.get("email"),
                        },
                        "similarity_scores": scores,
                        "average_similarity": avg_similarity,
                    })
        
        return sorted(duplicates, key=lambda x: x["average_similarity"], reverse=True)
    
    @staticmethod
    def merge_clients(tenant_id: str, primary_id: str, secondary_id: str, 
                     field_preferences: Optional[Dict] = None) -> Dict:
        """Merge two client records, preserving all historical data."""
        primary_oid = ObjectId(primary_id)
        secondary_oid = ObjectId(secondary_id)
        
        primary = db.clients.find_one({"_id": primary_oid, "tenant_id": tenant_id})
        secondary = db.clients.find_one({"_id": secondary_oid, "tenant_id": tenant_id})
        
        if not primary or not secondary:
            raise ValueError("One or both clients not found")
        
        # Merge data with preferences
        merged_data = primary.copy()
        if field_preferences:
            for field, use_secondary in field_preferences.items():
                if use_secondary and field in secondary:
                    merged_data[field] = secondary[field]
        
        # Merge arrays (bookings, communications, etc.)
        for field in ["bookings", "communications", "photos", "notes"]:
            if field in secondary:
                if field not in merged_data:
                    merged_data[field] = []
                merged_data[field].extend(secondary.get(field, []))
        
        # Update merged client
        merged_data["merged_from"] = [str(secondary_oid)]
        merged_data["merged_at"] = datetime.utcnow()
        merged_data["merge_undo_until"] = datetime.utcnow() + DuplicateDetectionService.MERGE_UNDO_WINDOW
        
        db.clients.update_one(
            {"_id": primary_oid},
            {"$set": merged_data}
        )
        
        # Update all references to secondary client
        db.bookings.update_many(
            {"client_id": secondary_oid},
            {"$set": {"client_id": primary_oid}}
        )
        db.communications.update_many(
            {"client_id": secondary_oid},
            {"$set": {"client_id": primary_oid}}
        )
        
        # Mark secondary as merged
        db.clients.update_one(
            {"_id": secondary_oid},
            {"$set": {
                "is_merged": True,
                "merged_into": str(primary_oid),
                "merged_at": datetime.utcnow()
            }}
        )
        
        return {
            "status": "merged",
            "primary_id": str(primary_oid),
            "secondary_id": str(secondary_oid),
            "merged_at": datetime.utcnow().isoformat(),
            "undo_until": (datetime.utcnow() + DuplicateDetectionService.MERGE_UNDO_WINDOW).isoformat(),
        }
    
    @staticmethod
    def undo_merge(tenant_id: str, primary_id: str) -> Dict:
        """Undo a merge operation within the undo window."""
        primary_oid = ObjectId(primary_id)
        primary = db.clients.find_one({"_id": primary_oid, "tenant_id": tenant_id})
        
        if not primary or not primary.get("merged_from"):
            raise ValueError("No merge to undo")
        
        if datetime.utcnow() > primary.get("merge_undo_until", datetime.utcnow()):
            raise ValueError("Undo window has expired")
        
        secondary_id = ObjectId(primary["merged_from"][0])
        
        # Restore secondary client
        db.clients.update_one(
            {"_id": secondary_id},
            {"$set": {"is_merged": False}, "$unset": {"merged_into": ""}}
        )
        
        # Remove merge metadata from primary
        db.clients.update_one(
            {"_id": primary_oid},
            {"$unset": {
                "merged_from": "",
                "merged_at": "",
                "merge_undo_until": ""
            }}
        )
        
        return {
            "status": "undo_complete",
            "primary_id": str(primary_oid),
            "secondary_id": str(secondary_id),
        }
