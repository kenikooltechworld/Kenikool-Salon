import logging
from typing import Dict, List, Any, Optional
from app.schemas.voice import Intent, ActionResult

logger = logging.getLogger(__name__)


class AIVoiceCommands:
    """Handles AI-powered voice commands for suggestions and insights"""

    def __init__(
        self,
        pattern_analyzer=None,
        prediction_engine=None,
        suggestion_generator=None,
        insight_generator=None,
        proactive_alerter=None
    ):
        """Initialize AI voice commands"""
        self.pattern_analyzer = pattern_analyzer
        self.prediction_engine = prediction_engine
        self.suggestion_generator = suggestion_generator
        self.insight_generator = insight_generator
        self.proactive_alerter = proactive_alerter

    async def handle_what_do_you_suggest(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Handle 'what do you suggest' command"""
        try:
            if not self.suggestion_generator:
                return ActionResult(
                    success=False,
                    message="Suggestion engine not available"
                )

            # Get suggestions
            suggestions = self.suggestion_generator.get_high_impact_suggestions()
            
            if not suggestions:
                return ActionResult(
                    success=True,
                    message="No suggestions available at this time"
                )

            # Format response
            response_text = "Here are my top suggestions:\n"
            for i, suggestion in enumerate(suggestions[:3], 1):
                response_text += f"{i}. {suggestion.get('recommendation', '')}\n"

            return ActionResult(
                success=True,
                message=response_text,
                data={"suggestions": suggestions[:3]}
            )

        except Exception as e:
            logger.error(f"Suggestion command failed: {e}")
            return ActionResult(
                success=False,
                message=f"Error getting suggestions: {str(e)}"
            )

    async def handle_show_me_insights(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Handle 'show me insights' command"""
        try:
            if not self.insight_generator:
                return ActionResult(
                    success=False,
                    message="Insight engine not available"
                )

            # Get insights
            insights = self.insight_generator.get_actionable_insights()
            
            if not insights:
                return ActionResult(
                    success=True,
                    message="No insights available at this time"
                )

            # Format response
            response_text = "Here are key business insights:\n"
            for i, insight in enumerate(insights[:3], 1):
                response_text += f"{i}. {insight.get('description', '')}\n"

            return ActionResult(
                success=True,
                message=response_text,
                data={"insights": insights[:3]}
            )

        except Exception as e:
            logger.error(f"Insights command failed: {e}")
            return ActionResult(
                success=False,
                message=f"Error getting insights: {str(e)}"
            )

    async def handle_predict_next_weeks_bookings(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Handle 'predict next week's bookings' command"""
        try:
            if not self.prediction_engine:
                return ActionResult(
                    success=False,
                    message="Prediction engine not available"
                )

            # Get booking predictions
            predictions = await self.prediction_engine.predict_booking_demand(
                historical_bookings=[],
                days_ahead=7
            )

            if "error" in predictions:
                return ActionResult(
                    success=False,
                    message="Unable to generate predictions"
                )

            # Format response
            total_predicted = sum(predictions.get('predictions', []))
            response_text = f"Next week's booking forecast: {int(total_predicted)} appointments predicted\n"
            response_text += f"Confidence level: {predictions.get('confidence', 0):.0%}"

            return ActionResult(
                success=True,
                message=response_text,
                data=predictions
            )

        except Exception as e:
            logger.error(f"Booking prediction command failed: {e}")
            return ActionResult(
                success=False,
                message=f"Error predicting bookings: {str(e)}"
            )

    async def handle_which_clients_might_not_return(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Handle 'which clients might not return' command"""
        try:
            if not self.prediction_engine:
                return ActionResult(
                    success=False,
                    message="Prediction engine not available"
                )

            # Get churn predictions
            predictions = await self.prediction_engine.predict_client_churn(
                client_data=[]
            )

            if "error" in predictions:
                return ActionResult(
                    success=False,
                    message="Unable to generate churn predictions"
                )

            high_risk = predictions.get('high_risk_count', 0)
            medium_risk = predictions.get('medium_risk_count', 0)

            response_text = f"Client churn analysis:\n"
            response_text += f"High risk: {high_risk} clients\n"
            response_text += f"Medium risk: {medium_risk} clients\n"
            response_text += "Recommend reaching out with special offers"

            return ActionResult(
                success=True,
                message=response_text,
                data=predictions
            )

        except Exception as e:
            logger.error(f"Churn prediction command failed: {e}")
            return ActionResult(
                success=False,
                message=f"Error predicting churn: {str(e)}"
            )

    async def handle_when_should_i_reorder(
        self,
        user_id: str,
        item_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Handle 'when should I reorder [product]' command"""
        try:
            if not self.prediction_engine:
                return ActionResult(
                    success=False,
                    message="Prediction engine not available"
                )

            # Get inventory depletion prediction
            predictions = await self.prediction_engine.predict_inventory_depletion(
                inventory_data=[],
                item_id=item_name or "unknown"
            )

            if "error" in predictions:
                return ActionResult(
                    success=False,
                    message=f"Unable to predict depletion for {item_name}"
                )

            depletion_days = predictions.get('depletion_days', 0)
            reorder_recommended = predictions.get('reorder_recommended', False)

            if reorder_recommended:
                response_text = f"Reorder {item_name} immediately!\n"
                response_text += f"Stock will be depleted in {depletion_days} days"
            else:
                response_text = f"{item_name} stock is healthy.\n"
                response_text += f"Reorder in approximately {depletion_days} days"

            return ActionResult(
                success=True,
                message=response_text,
                data=predictions
            )

        except Exception as e:
            logger.error(f"Reorder prediction command failed: {e}")
            return ActionResult(
                success=False,
                message=f"Error predicting reorder: {str(e)}"
            )

    async def execute_ai_command(
        self,
        command: str,
        user_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Execute AI voice command"""
        try:
            command_lower = command.lower()

            if "suggest" in command_lower:
                return await self.handle_what_do_you_suggest(user_id, context)

            elif "insight" in command_lower:
                return await self.handle_show_me_insights(user_id, context)

            elif "predict" in command_lower and "booking" in command_lower:
                return await self.handle_predict_next_weeks_bookings(user_id, context)

            elif "churn" in command_lower or "not return" in command_lower:
                return await self.handle_which_clients_might_not_return(user_id, context)

            elif "reorder" in command_lower:
                item_name = parameters.get('item_name') if parameters else None
                return await self.handle_when_should_i_reorder(user_id, item_name, context)

            else:
                return ActionResult(
                    success=False,
                    message="Unknown AI command"
                )

        except Exception as e:
            logger.error(f"AI command execution failed: {e}")
            return ActionResult(
                success=False,
                message=f"Error executing command: {str(e)}"
            )

    def get_available_ai_commands(self) -> List[Dict[str, str]]:
        """Get list of available AI commands"""
        return [
            {
                "command": "what do you suggest",
                "description": "Get AI suggestions for business optimization",
                "example": "What do you suggest?"
            },
            {
                "command": "show me insights",
                "description": "Get business insights and analysis",
                "example": "Show me insights"
            },
            {
                "command": "predict next week's bookings",
                "description": "Get booking forecast for next week",
                "example": "Predict next week's bookings"
            },
            {
                "command": "which clients might not return",
                "description": "Identify clients at risk of churning",
                "example": "Which clients might not return?"
            },
            {
                "command": "when should I reorder [product]",
                "description": "Get inventory reorder recommendations",
                "example": "When should I reorder shampoo?"
            }
        ]
