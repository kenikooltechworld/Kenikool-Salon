import csv
import io
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
from app.database import Database


class ExportService:
    
    @staticmethod
    def export_bookings_csv(
        tenant_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """Export bookings to CSV"""
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        
        if status:
            query["status"] = status
        
        if date_from or date_to:
            query["booking_date"] = {}
            if date_from:
                query["booking_date"]["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            if date_to:
                query["booking_date"]["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        
        bookings = list(db.bookings.find(query).sort("booking_date", -1))
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            "Booking ID", "Client Name", "Service", "Stylist", 
            "Date", "Time", "Status", "Price", "Payment Status"
        ])
        
        # Data
        for booking in bookings:
            writer.writerow([
                str(booking.get("_id")),
                booking.get("client_name", ""),
                booking.get("service_name", ""),
                booking.get("stylist_name", ""),
                booking.get("booking_date", "").strftime("%Y-%m-%d") if booking.get("booking_date") else "",
                booking.get("booking_date", "").strftime("%H:%M") if booking.get("booking_date") else "",
                booking.get("status", ""),
                booking.get("service_price", 0),
                booking.get("payment_status", "")
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_clients_csv(tenant_id: str) -> str:
        """Export clients to CSV"""
        db = Database.get_db()
        
        clients = list(db.clients.find({"tenant_id": tenant_id}))
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            "Client ID", "Name", "Phone", "Email", 
            "Total Visits", "Total Spent", "Last Visit"
        ])
        
        # Data
        for client in clients:
            writer.writerow([
                str(client.get("_id")),
                client.get("name", ""),
                client.get("phone", ""),
                client.get("email", ""),
                client.get("total_visits", 0),
                client.get("total_spent", 0),
                client.get("last_visit_date", "").strftime("%Y-%m-%d") if client.get("last_visit_date") else ""
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_revenue_csv(
        tenant_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> str:
        """Export revenue report to CSV"""
        db = Database.get_db()
        
        query = {
            "tenant_id": tenant_id,
            "status": "completed"
        }
        
        if date_from or date_to:
            query["booking_date"] = {}
            if date_from:
                query["booking_date"]["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            if date_to:
                query["booking_date"]["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        
        bookings = list(db.bookings.find(query).sort("booking_date", -1))
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            "Date", "Service", "Stylist", "Client", "Amount", "Payment Method"
        ])
        
        total_revenue = 0
        
        # Data
        for booking in bookings:
            amount = booking.get("service_price", 0)
            total_revenue += amount
            
            writer.writerow([
                booking.get("booking_date", "").strftime("%Y-%m-%d") if booking.get("booking_date") else "",
                booking.get("service_name", ""),
                booking.get("stylist_name", ""),
                booking.get("client_name", ""),
                amount,
                booking.get("payment_method", "")
            ])
        
        # Summary
        writer.writerow([])
        writer.writerow(["Total Revenue", total_revenue])
        
        return output.getvalue()
    
    @staticmethod
    def export_stylist_performance_csv(tenant_id: str) -> str:
        """Export stylist performance report"""
        db = Database.get_db()
        
        stylists = list(db.stylists.find({"tenant_id": tenant_id}))
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            "Stylist", "Total Bookings", "Completed", "Revenue", "Average Rating", "Reviews"
        ])
        
        # Data
        for stylist in stylists:
            stylist_id = stylist.get("_id")
            
            bookings = list(db.bookings.find({
                "tenant_id": tenant_id,
                "stylist_id": stylist_id,
                "status": "completed"
            }))
            
            revenue = sum(b.get("service_price", 0) for b in bookings)
            
            reviews = list(db.reviews.find({
                "tenant_id": tenant_id,
                "stylist_id": stylist_id,
                "is_approved": True
            }))
            
            avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews) if reviews else 0
            
            writer.writerow([
                stylist.get("name", ""),
                len(bookings),
                len(bookings),
                revenue,
                round(avg_rating, 2),
                len(reviews)
            ])
        
        return output.getvalue()
