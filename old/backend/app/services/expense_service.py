"""
Expense tracking and financial reporting service
"""
from datetime import datetime, date
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class ExpenseService:
    """Service layer for expense management"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_expenses(
        self,
        tenant_id: str,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict:
        """Get list of expenses with filtering"""
        try:
            # Build query
            query = {"tenant_id": tenant_id}
            
            if category:
                query["category"] = category
            
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date.isoformat()
                if end_date:
                    date_query["$lte"] = end_date.isoformat()
                query["expense_date"] = date_query
            
            # Get total count
            total = self.db.expenses.count_documents(query)
            
            # Get expenses
            cursor = self.db.expenses.find(query).sort("expense_date", -1).skip(skip).limit(limit)
            expenses = list(cursor)
            
            # Convert ObjectId to string
            for expense in expenses:
                expense["_id"] = str(expense["_id"])
            
            return {
                "expenses": expenses,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        
        except Exception as e:
            logger.error(f"Error getting expenses: {e}")
            raise Exception(f"Failed to get expenses: {str(e)}")
    
    async def create_expense(
        self,
        tenant_id: str,
        user_id: str,
        category: str,
        description: str,
        amount: float,
        expense_date: date,
        payment_method: Optional[str],
        vendor: Optional[str],
        receipt_url: Optional[str],
        notes: Optional[str]
    ) -> Dict:
        """Create a new expense"""
        try:
            # Create expense
            expense_data = {
                "tenant_id": tenant_id,
                "created_by": user_id,
                "category": category,
                "description": description,
                "amount": amount,
                "expense_date": expense_date.isoformat(),
                "payment_method": payment_method,
                "vendor": vendor,
                "receipt_url": receipt_url,
                "notes": notes,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.db.expenses.insert_one(expense_data)
            expense_data["_id"] = str(result.inserted_id)
            
            return expense_data
        
        except Exception as e:
            logger.error(f"Error creating expense: {e}")
            raise Exception(f"Failed to create expense: {str(e)}")
    
    async def update_expense(
        self,
        expense_id: str,
        tenant_id: str,
        update_data: Dict
    ) -> Dict:
        """Update an expense"""
        try:
            # Find expense
            expense = self.db.expenses.find_one({
                "_id": ObjectId(expense_id),
                "tenant_id": tenant_id
            })
            
            if not expense:
                raise ValueError("Expense not found")
            
            # Convert date to ISO format if present
            if "expense_date" in update_data and isinstance(update_data["expense_date"], date):
                update_data["expense_date"] = update_data["expense_date"].isoformat()
            
            # Update expense
            update_data["updated_at"] = datetime.utcnow()
            
            self.db.expenses.update_one(
                {"_id": ObjectId(expense_id)},
                {"$set": update_data}
            )
            
            # Get updated expense
            updated_expense = self.db.expenses.find_one({"_id": ObjectId(expense_id)})
            updated_expense["_id"] = str(updated_expense["_id"])
            
            return updated_expense
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error updating expense: {e}")
            raise Exception(f"Failed to update expense: {str(e)}")
    
    async def delete_expense(
        self,
        expense_id: str,
        tenant_id: str
    ) -> bool:
        """Delete an expense"""
        try:
            # Find expense
            expense = self.db.expenses.find_one({
                "_id": ObjectId(expense_id),
                "tenant_id": tenant_id
            })
            
            if not expense:
                raise ValueError("Expense not found")
            
            # Hard delete expense
            self.db.expenses.delete_one({"_id": ObjectId(expense_id)})
            
            return True
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error deleting expense: {e}")
            raise Exception(f"Failed to delete expense: {str(e)}")


# Legacy functions for backward compatibility


async def get_expense_summary(
    tenant_id: str,
    start_date: date,
    end_date: date,
    db
) -> Dict:
    """
    Get expense summary for a period
    """
    try:
        # Convert dates to datetime for MongoDB query
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        # Aggregate expenses by category
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "expense_date": {
                        "$gte": start_date.isoformat(),
                        "$lte": end_date.isoformat()
                    }
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "total_amount": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"total_amount": -1}}
        ]
        
        results = await db.expenses.aggregate(pipeline).to_list(length=None)
        
        category_breakdown = []
        total_expenses = 0
        
        for result in results:
            category_breakdown.append({
                "category": result["_id"],
                "total_amount": result["total_amount"],
                "count": result["count"]
            })
            total_expenses += result["total_amount"]
        
        return {
            "total_expenses": total_expenses,
            "category_breakdown": category_breakdown,
            "expense_count": sum(r["count"] for r in category_breakdown)
        }
    
    except Exception as e:
        logger.error(f"Error getting expense summary: {e}")
        return {
            "total_expenses": 0,
            "category_breakdown": [],
            "expense_count": 0
        }


async def calculate_profit_loss(
    tenant_id: str,
    start_date: date,
    end_date: date,
    db
) -> Dict:
    """
    Calculate profit/loss for a period
    """
    try:
        # Convert dates to datetime
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        # Get revenue from completed bookings
        revenue_pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "status": "completed",
                    "completed_at": {
                        "$gte": start_dt,
                        "$lte": end_dt
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$service_price"}
                }
            }
        ]
        
        revenue_results = await db.bookings.aggregate(revenue_pipeline).to_list(length=1)
        total_revenue = revenue_results[0]["total_revenue"] if revenue_results else 0
        
        # Get expenses
        expense_summary = await get_expense_summary(tenant_id, start_date, end_date, db)
        total_expenses = expense_summary["total_expenses"]
        
        # Calculate profit/loss
        profit_loss = total_revenue - total_expenses
        profit_margin = (profit_loss / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "profit_loss": profit_loss,
            "profit_margin": round(profit_margin, 2),
            "is_profitable": profit_loss > 0
        }
    
    except Exception as e:
        logger.error(f"Error calculating profit/loss: {e}")
        return {
            "total_revenue": 0,
            "total_expenses": 0,
            "profit_loss": 0,
            "profit_margin": 0,
            "is_profitable": False
        }


async def generate_financial_report(
    tenant_id: str,
    start_date: date,
    end_date: date,
    db
) -> bytes:
    """
    Generate financial report PDF
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import inch
        import io
        
        # Get data
        profit_loss = await calculate_profit_loss(tenant_id, start_date, end_date, db)
        expense_summary = await get_expense_summary(tenant_id, start_date, end_date, db)
        
        # Get tenant info
        from bson import ObjectId
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
        salon_name = tenant["salon_name"] if tenant else "Salon"
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>{salon_name}</b><br/>Financial Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Period
        period = Paragraph(
            f"Period: {start_date.isoformat()} to {end_date.isoformat()}",
            styles['Normal']
        )
        elements.append(period)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Summary table
        summary_data = [
            ['Metric', 'Amount'],
            ['Total Revenue', f"${profit_loss['total_revenue']:.2f}"],
            ['Total Expenses', f"${profit_loss['total_expenses']:.2f}"],
            ['Profit/Loss', f"${profit_loss['profit_loss']:.2f}"],
            ['Profit Margin', f"{profit_loss['profit_margin']:.2f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.5 * inch))
        
        # Expense breakdown
        if expense_summary["category_breakdown"]:
            expense_title = Paragraph("<b>Expense Breakdown by Category</b>", styles['Heading2'])
            elements.append(expense_title)
            elements.append(Spacer(1, 0.2 * inch))
            
            expense_data = [['Category', 'Amount', 'Count']]
            for cat in expense_summary["category_breakdown"]:
                expense_data.append([
                    cat["category"],
                    f"${cat['total_amount']:.2f}",
                    str(cat["count"])
                ])
            
            expense_table = Table(expense_data, colWidths=[2.5 * inch, 1.5 * inch, 1 * inch])
            expense_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(expense_table)
        
        # Build PDF
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    except Exception as e:
        logger.error(f"Error generating financial report: {e}")
        raise

