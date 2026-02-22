"""
Goal Tracking and KPI Management Service
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.database.mongodb import db
from app.schemas.analytics import Goal, KPIMetric


class GoalTrackingService:
    """Service for managing goals and KPIs"""

    async def create_goal(self, tenant_id: str, goal: Goal) -> Goal:
        """Create a new goal"""
        goal_dict = goal.dict()
        goal_dict['tenant_id'] = tenant_id
        goal_dict['created_at'] = datetime.utcnow()
        goal_dict['updated_at'] = datetime.utcnow()
        goal_dict['status'] = self._calculate_goal_status(
            goal.current_value,
            goal.target_value,
            goal.end_date
        )
        goal_dict['progress_percentage'] = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0

        result = await db.goals_tracking.insert_one(goal_dict)
        goal_dict['goal_id'] = str(result.inserted_id)
        return Goal(**goal_dict)

    async def list_goals(
        self,
        tenant_id: str,
        goal_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Goal]:
        """List all goals for a tenant"""
        query = {'tenant_id': tenant_id}
        if goal_type:
            query['goal_type'] = goal_type
        if status:
            query['status'] = status

        goals = await db.goals_tracking.find(query).to_list(None)
        return [Goal(**goal) for goal in goals]

    async def get_goal(self, tenant_id: str, goal_id: str) -> Goal:
        """Get a specific goal"""
        goal = await db.goals_tracking.find_one({
            '_id': ObjectId(goal_id),
            'tenant_id': tenant_id
        })
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")
        goal['goal_id'] = str(goal['_id'])
        return Goal(**goal)

    async def update_goal(self, tenant_id: str, goal_id: str, goal: Goal) -> Goal:
        """Update a goal"""
        goal_dict = goal.dict()
        goal_dict['updated_at'] = datetime.utcnow()
        goal_dict['status'] = self._calculate_goal_status(
            goal.current_value,
            goal.target_value,
            goal.end_date
        )
        goal_dict['progress_percentage'] = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0

        result = await db.goals_tracking.update_one(
            {'_id': ObjectId(goal_id), 'tenant_id': tenant_id},
            {'$set': goal_dict}
        )

        if result.matched_count == 0:
            raise ValueError(f"Goal {goal_id} not found")

        updated_goal = await db.goals_tracking.find_one({
            '_id': ObjectId(goal_id),
            'tenant_id': tenant_id
        })
        updated_goal['goal_id'] = str(updated_goal['_id'])
        return Goal(**updated_goal)

    async def delete_goal(self, tenant_id: str, goal_id: str) -> Dict[str, Any]:
        """Delete a goal"""
        result = await db.goals_tracking.delete_one({
            '_id': ObjectId(goal_id),
            'tenant_id': tenant_id
        })

        if result.deleted_count == 0:
            raise ValueError(f"Goal {goal_id} not found")

        return {'status': 'deleted', 'goal_id': goal_id}

    async def update_goal_progress(
        self,
        tenant_id: str,
        goal_id: str,
        current_value: float
    ) -> Goal:
        """Update goal progress"""
        goal = await self.get_goal(tenant_id, goal_id)
        goal.current_value = current_value
        return await self.update_goal(tenant_id, goal_id, goal)

    async def list_kpis(self, tenant_id: str) -> List[KPIMetric]:
        """List all KPI metrics"""
        kpis = await db.kpi_metrics.find({'tenant_id': tenant_id}).to_list(None)
        return [KPIMetric(**kpi) for kpi in kpis]

    async def get_kpi(self, tenant_id: str, kpi_id: str) -> KPIMetric:
        """Get a specific KPI metric"""
        kpi = await db.kpi_metrics.find_one({
            '_id': ObjectId(kpi_id),
            'tenant_id': tenant_id
        })
        if not kpi:
            raise ValueError(f"KPI {kpi_id} not found")
        kpi['kpi_id'] = str(kpi['_id'])
        return KPIMetric(**kpi)

    async def get_goal_alerts(self, tenant_id: str, goal_id: str) -> List[Dict[str, Any]]:
        """Get alerts for a goal"""
        goal = await self.get_goal(tenant_id, goal_id)

        alerts = []

        # Check if goal is at risk
        progress_percentage = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
        days_remaining = (datetime.fromisoformat(goal.end_date) - datetime.utcnow()).days

        if progress_percentage < 60 and days_remaining > 0:
            alerts.append({
                'id': f"alert_{goal_id}_at_risk",
                'goal_id': goal_id,
                'goal_name': goal.name,
                'type': 'at_risk',
                'message': f"Goal is at risk. Current progress: {progress_percentage:.0f}%",
                'severity': 'high' if progress_percentage < 40 else 'medium',
                'created_at': datetime.utcnow().isoformat(),
                'read': False,
                'action_required': True
            })

        # Check if goal is missed
        if datetime.utcnow() > datetime.fromisoformat(goal.end_date) and progress_percentage < 100:
            alerts.append({
                'id': f"alert_{goal_id}_missed",
                'goal_id': goal_id,
                'goal_name': goal.name,
                'type': 'missed',
                'message': f"Goal deadline has passed. Final achievement: {progress_percentage:.0f}%",
                'severity': 'critical',
                'created_at': datetime.utcnow().isoformat(),
                'read': False,
                'action_required': True
            })

        # Check if goal is off track
        if days_remaining > 0 and progress_percentage < (100 * (1 - days_remaining / ((datetime.fromisoformat(goal.end_date) - datetime.fromisoformat(goal.start_date)).days or 1))):
            alerts.append({
                'id': f"alert_{goal_id}_off_track",
                'goal_id': goal_id,
                'goal_name': goal.name,
                'type': 'off_track',
                'message': f"Goal is off track. Expected progress: {100 * (1 - days_remaining / ((datetime.fromisoformat(goal.end_date) - datetime.fromisoformat(goal.start_date)).days or 1)):.0f}%",
                'severity': 'medium',
                'created_at': datetime.utcnow().isoformat(),
                'read': False,
                'action_required': False
            })

        return alerts

    async def get_goal_recommendations(self, tenant_id: str, goal_id: str) -> List[Dict[str, Any]]:
        """Get recommendations for a goal"""
        goal = await self.get_goal(tenant_id, goal_id)

        recommendations = []
        progress_percentage = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
        days_remaining = (datetime.fromisoformat(goal.end_date) - datetime.utcnow()).days

        # Recommendation 1: Increase effort if behind
        if progress_percentage < 50 and days_remaining > 0:
            required_daily_progress = (100 - progress_percentage) / max(days_remaining, 1)
            recommendations.append({
                'id': f"rec_{goal_id}_increase_effort",
                'goal_id': goal_id,
                'goal_name': goal.name,
                'title': 'Increase Daily Effort',
                'description': f"To achieve this goal, you need to increase daily progress to {required_daily_progress:.1f}%",
                'action': f"Focus on increasing daily progress by {required_daily_progress:.1f}% to meet the target",
                'impact': 'high',
                'based_on': 'Current progress vs time remaining',
                'created_at': datetime.utcnow().isoformat()
            })

        # Recommendation 2: Allocate more resources
        if progress_percentage < 70 and goal.goal_type in ['revenue', 'bookings']:
            recommendations.append({
                'id': f"rec_{goal_id}_allocate_resources",
                'goal_id': goal_id,
                'goal_name': goal.name,
                'title': 'Allocate More Resources',
                'description': f"Consider allocating additional resources to accelerate progress toward this {goal.goal_type} goal",
                'action': 'Review resource allocation and consider increasing staff or marketing budget',
                'impact': 'high',
                'based_on': 'Goal type and current progress',
                'created_at': datetime.utcnow().isoformat()
            })

        # Recommendation 3: Review strategy
        if progress_percentage > 100:
            recommendations.append({
                'id': f"rec_{goal_id}_review_strategy",
                'goal_id': goal_id,
                'goal_name': goal.name,
                'title': 'Goal Exceeded - Review Strategy',
                'description': 'This goal has been exceeded. Consider setting a higher target for next period',
                'action': 'Analyze what worked well and apply those strategies to other goals',
                'impact': 'medium',
                'based_on': 'Goal achievement',
                'created_at': datetime.utcnow().isoformat()
            })

        return recommendations

    async def get_team_goal_comparison(self, tenant_id: str, goal_id: str) -> Dict[str, Any]:
        """Get team vs individual goal comparison"""
        goal = await self.get_goal(tenant_id, goal_id)

        # Get team members' performance (mock data for now)
        team_members = [
            {
                'member_id': f"member_{i}",
                'member_name': f"Team Member {i+1}",
                'current_value': goal.current_value * (0.8 + i * 0.1),
                'target_value': goal.target_value,
                'achievement_rate': ((goal.current_value * (0.8 + i * 0.1)) / goal.target_value * 100) if goal.target_value > 0 else 0,
                'historical_achievement_rates': [70 + j * 5 for j in range(5)],
                'trend': 'up' if i % 2 == 0 else 'down',
                'last_updated': datetime.utcnow().isoformat()
            }
            for i in range(3)
        ]

        team_progress = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0

        return {
            'goal_id': goal_id,
            'goal_name': goal.name,
            'goal_type': goal.goal_type,
            'team_target': goal.target_value,
            'team_current': goal.current_value,
            'team_progress': team_progress,
            'team_members': team_members,
            'historical_team_achievement': [70 + i * 5 for i in range(5)],
            'historical_individual_achievements': {
                member['member_id']: member['historical_achievement_rates']
                for member in team_members
            }
        }

    async def get_historical_achievement(self, tenant_id: str, goal_id: str) -> Dict[str, Any]:
        """Get historical achievement rates for a goal"""
        goal = await self.get_goal(tenant_id, goal_id)

        # Get historical data from database
        historical_data = await db.goal_history.find({
            'goal_id': goal_id,
            'tenant_id': tenant_id
        }).sort('date', -1).limit(30).to_list(None)

        return {
            'goal_id': goal_id,
            'goal_name': goal.name,
            'current_achievement': (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0,
            'historical_data': [
                {
                    'date': h['date'].isoformat(),
                    'achievement_rate': (h['current_value'] / goal.target_value * 100) if goal.target_value > 0 else 0,
                    'current_value': h['current_value']
                }
                for h in reversed(historical_data)
            ]
        }

    def _calculate_goal_status(self, current_value: float, target_value: float, end_date: str) -> str:
        """Calculate goal status based on progress and time remaining"""
        if target_value <= 0:
            return 'on_track'

        progress_percentage = (current_value / target_value * 100)

        if progress_percentage >= 100:
            return 'achieved'

        days_remaining = (datetime.fromisoformat(end_date) - datetime.utcnow()).days

        if days_remaining < 0:
            return 'missed'

        # Expected progress based on time
        if days_remaining > 0:
            expected_progress = 100 * (1 - days_remaining / ((datetime.fromisoformat(end_date) - datetime.fromisoformat(datetime.utcnow().isoformat())).days or 1))
            if progress_percentage < expected_progress - 10:
                return 'at_risk'

        return 'on_track'
