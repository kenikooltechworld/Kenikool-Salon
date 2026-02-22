import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ProactiveAlerter:
    """Generates proactive alerts for business issues"""

    def __init__(self):
        """Initialize proactive alerter"""
        self.alerts = []
        self.alert_history = []

    async def check_inventory_shortage(
        self,
        inventory_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for inventory shortages"""
        try:
            alerts = []
            
            for item in inventory_data:
                quantity = item.get('quantity', 0)
                min_quantity = item.get('min_quantity', 0)
                reorder_point = item.get('reorder_point', min_quantity * 1.5)
                
                if quantity <= min_quantity:
                    alerts.append({
                        "type": "inventory_shortage",
                        "severity": "critical",
                        "item_id": item.get('id'),
                        "item_name": item.get('name'),
                        "current_quantity": quantity,
                        "minimum_quantity": min_quantity,
                        "message": f"CRITICAL: {item.get('name')} is out of stock!",
                        "action_required": True,
                        "recommended_action": "Reorder immediately",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif quantity <= reorder_point:
                    alerts.append({
                        "type": "inventory_low",
                        "severity": "warning",
                        "item_id": item.get('id'),
                        "item_name": item.get('name'),
                        "current_quantity": quantity,
                        "reorder_point": reorder_point,
                        "message": f"WARNING: {item.get('name')} is running low",
                        "action_required": True,
                        "recommended_action": "Plan reorder soon",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            logger.info(f"Inventory alerts generated: {len(alerts)}")
            return alerts

        except Exception as e:
            logger.error(f"Inventory shortage check failed: {e}")
            return []

    async def check_client_churn_risk(
        self,
        client_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for client churn risks"""
        try:
            alerts = []
            
            for client in client_data:
                last_visit = client.get('last_visit_date')
                if not last_visit:
                    continue
                
                # Calculate days since last visit
                last_visit_date = datetime.fromisoformat(last_visit) if isinstance(last_visit, str) else last_visit
                days_since_visit = (datetime.utcnow() - last_visit_date).days
                
                if days_since_visit > 120:
                    alerts.append({
                        "type": "client_churn_risk",
                        "severity": "critical",
                        "client_id": client.get('id'),
                        "client_name": client.get('name'),
                        "days_since_visit": days_since_visit,
                        "message": f"CRITICAL: {client.get('name')} hasn't visited in {days_since_visit} days",
                        "action_required": True,
                        "recommended_action": "Send personalized re-engagement offer",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif days_since_visit > 90:
                    alerts.append({
                        "type": "client_churn_risk",
                        "severity": "warning",
                        "client_id": client.get('id'),
                        "client_name": client.get('name'),
                        "days_since_visit": days_since_visit,
                        "message": f"WARNING: {client.get('name')} hasn't visited in {days_since_visit} days",
                        "action_required": True,
                        "recommended_action": "Send reminder and special offer",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            logger.info(f"Client churn alerts generated: {len(alerts)}")
            return alerts

        except Exception as e:
            logger.error(f"Client churn risk check failed: {e}")
            return []

    async def check_underutilized_slots(
        self,
        booking_data: List[Dict[str, Any]],
        total_slots: int = 100
    ) -> List[Dict[str, Any]]:
        """Check for underutilized appointment slots"""
        try:
            alerts = []
            
            booked_slots = len(booking_data)
            utilization_rate = (booked_slots / total_slots * 100) if total_slots > 0 else 0
            
            if utilization_rate < 30:
                alerts.append({
                    "type": "underutilized_slots",
                    "severity": "critical",
                    "utilization_rate": utilization_rate,
                    "booked_slots": booked_slots,
                    "total_slots": total_slots,
                    "available_slots": total_slots - booked_slots,
                    "message": f"CRITICAL: Only {utilization_rate:.1f}% of slots are booked",
                    "action_required": True,
                    "recommended_action": "Launch promotional campaign to fill slots",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif utilization_rate < 50:
                alerts.append({
                    "type": "underutilized_slots",
                    "severity": "warning",
                    "utilization_rate": utilization_rate,
                    "booked_slots": booked_slots,
                    "total_slots": total_slots,
                    "available_slots": total_slots - booked_slots,
                    "message": f"WARNING: Only {utilization_rate:.1f}% of slots are booked",
                    "action_required": True,
                    "recommended_action": "Increase marketing efforts",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info(f"Underutilized slot alerts generated: {len(alerts)}")
            return alerts

        except Exception as e:
            logger.error(f"Underutilized slots check failed: {e}")
            return []

    async def check_staff_performance(
        self,
        staff_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for staff performance issues"""
        try:
            alerts = []
            
            avg_appointments = sum(s.get('appointments_completed', 0) for s in staff_data) / max(len(staff_data), 1)
            
            for staff in staff_data:
                appointments = staff.get('appointments_completed', 0)
                
                if appointments < avg_appointments * 0.5:
                    alerts.append({
                        "type": "staff_performance",
                        "severity": "warning",
                        "staff_id": staff.get('id'),
                        "staff_name": staff.get('name'),
                        "appointments": appointments,
                        "average": avg_appointments,
                        "message": f"WARNING: {staff.get('name')} is underperforming",
                        "action_required": True,
                        "recommended_action": "Schedule performance review",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            logger.info(f"Staff performance alerts generated: {len(alerts)}")
            return alerts

        except Exception as e:
            logger.error(f"Staff performance check failed: {e}")
            return []

    async def generate_all_alerts(
        self,
        inventory_data: Optional[List[Dict[str, Any]]] = None,
        client_data: Optional[List[Dict[str, Any]]] = None,
        booking_data: Optional[List[Dict[str, Any]]] = None,
        staff_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate all proactive alerts"""
        try:
            all_alerts = []
            
            # Inventory alerts
            if inventory_data:
                inventory_alerts = await self.check_inventory_shortage(inventory_data)
                all_alerts.extend(inventory_alerts)
            
            # Client churn alerts
            if client_data:
                churn_alerts = await self.check_client_churn_risk(client_data)
                all_alerts.extend(churn_alerts)
            
            # Underutilized slot alerts
            if booking_data:
                slot_alerts = await self.check_underutilized_slots(booking_data)
                all_alerts.extend(slot_alerts)
            
            # Staff performance alerts
            if staff_data:
                perf_alerts = await self.check_staff_performance(staff_data)
                all_alerts.extend(perf_alerts)
            
            # Sort by severity
            severity_order = {"critical": 0, "warning": 1, "info": 2}
            all_alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'info'), 3))
            
            self.alerts = all_alerts
            self.alert_history.extend(all_alerts)
            
            result = {
                "alerts": all_alerts,
                "total_alerts": len(all_alerts),
                "critical_alerts": len([a for a in all_alerts if a.get('severity') == 'critical']),
                "warning_alerts": len([a for a in all_alerts if a.get('severity') == 'warning']),
                "requires_action": any(a.get('action_required') for a in all_alerts),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"All alerts generated: {result}")
            return result

        except Exception as e:
            logger.error(f"Alert generation failed: {e}")
            return {"error": str(e)}

    async def acknowledge_alert(self, alert_id: str) -> Dict[str, Any]:
        """Acknowledge an alert"""
        try:
            for alert in self.alerts:
                if alert.get('id') == alert_id:
                    alert['acknowledged'] = True
                    alert['acknowledged_at'] = datetime.utcnow().isoformat()
                    logger.info(f"Alert acknowledged: {alert_id}")
                    return {"success": True, "message": "Alert acknowledged"}
            
            return {"success": False, "message": "Alert not found"}

        except Exception as e:
            logger.error(f"Alert acknowledgment failed: {e}")
            return {"error": str(e)}

    def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Get critical alerts"""
        return [a for a in self.alerts if a.get('severity') == 'critical']

    def get_unacknowledged_alerts(self) -> List[Dict[str, Any]]:
        """Get unacknowledged alerts"""
        return [a for a in self.alerts if not a.get('acknowledged', False)]
