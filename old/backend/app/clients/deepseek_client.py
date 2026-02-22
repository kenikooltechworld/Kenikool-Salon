"""
DeepSeek Client for Complex Reasoning
Communicates with DeepSeek Docker container for advanced reasoning tasks
"""

import logging
from typing import Optional, List, Dict, Any
from .base_client import BaseDockerClient

logger = logging.getLogger(__name__)


class DeepSeekClient(BaseDockerClient):
    """Client for DeepSeek reasoning Docker container"""
    
    async def reason(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        thinking_budget: int = 5000
    ) -> Dict[str, str]:
        """
        Perform complex reasoning using DeepSeek
        
        Args:
            prompt: Reasoning prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            thinking_budget: Budget for reasoning tokens
            
        Returns:
            dict with 'thinking' and 'response' keys
            
        Raises:
            httpx.HTTPError: If reasoning fails
        """
        try:
            payload = {
                'prompt': prompt,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'thinking_budget': thinking_budget,
                'stream': False
            }
            
            response = await self._post(
                '/v1/completions',
                json_data=payload
            )
            
            result = response.json()
            
            # DeepSeek returns thinking process and final response
            thinking = result.get('thinking', '')
            response_text = result['choices'][0]['text'].strip()
            
            logger.info(f"DeepSeek reasoning: {len(thinking)} thinking chars, {len(response_text)} response chars")
            
            return {
                'thinking': thinking,
                'response': response_text
            }
            
        except Exception as e:
            logger.error(f"DeepSeek reasoning failed: {e}")
            raise
    
    async def analyze_business_data(
        self,
        data: Dict[str, Any],
        question: str,
        language: str = 'en'
    ) -> str:
        """
        Analyze business data and answer questions
        
        Args:
            data: Business data (revenue, bookings, etc.)
            question: User's question
            language: Response language
            
        Returns:
            Analysis response
        """
        try:
            # Build analysis prompt
            prompt = self._build_analysis_prompt(data, question, language)
            
            result = await self.reason(
                prompt=prompt,
                max_tokens=500,
                temperature=0.5,
                thinking_budget=3000
            )
            
            return result['response']
            
        except Exception as e:
            logger.error(f"Business data analysis failed: {e}")
            raise
    
    async def optimize_schedule(
        self,
        appointments: List[Dict[str, Any]],
        staff: List[Dict[str, Any]],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize staff scheduling using reasoning
        
        Args:
            appointments: List of appointments
            staff: List of staff members
            constraints: Scheduling constraints
            
        Returns:
            Optimized schedule
        """
        try:
            prompt = self._build_scheduling_prompt(appointments, staff, constraints)
            
            result = await self.reason(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3,
                thinking_budget=5000
            )
            
            # Parse response as JSON
            import json
            schedule = json.loads(result['response'])
            
            return schedule
            
        except Exception as e:
            logger.error(f"Schedule optimization failed: {e}")
            raise
    
    def _build_analysis_prompt(
        self,
        data: Dict[str, Any],
        question: str,
        language: str
    ) -> str:
        """Build prompt for business data analysis"""
        
        import json
        data_str = json.dumps(data, indent=2)
        
        prompt = f"""You are a business analyst for a salon management system. Analyze the following data and answer the question.

Data:
{data_str}

Question: {question}

Language: {language}

Provide a clear, concise answer based on the data. If the language is not English, respond in that language.
"""
        
        return prompt
    
    def _build_scheduling_prompt(
        self,
        appointments: List[Dict[str, Any]],
        staff: List[Dict[str, Any]],
        constraints: Dict[str, Any]
    ) -> str:
        """Build prompt for schedule optimization"""
        
        import json
        
        prompt = f"""You are a scheduling optimizer for a salon. Create an optimal schedule that:
1. Assigns all appointments to appropriate staff
2. Respects staff availability and skills
3. Minimizes wait times
4. Balances workload

Appointments:
{json.dumps(appointments, indent=2)}

Staff:
{json.dumps(staff, indent=2)}

Constraints:
{json.dumps(constraints, indent=2)}

Respond with a JSON object containing the optimized schedule with assignments.
"""
        
        return prompt
    
    async def generate_insights(
        self,
        metrics: Dict[str, Any],
        language: str = 'en'
    ) -> List[str]:
        """
        Generate business insights from metrics
        
        Args:
            metrics: Business metrics
            language: Response language
            
        Returns:
            List of insights
        """
        try:
            import json
            
            prompt = f"""Analyze these salon business metrics and generate 3-5 actionable insights:

{json.dumps(metrics, indent=2)}

Language: {language}

Provide insights as a JSON array of strings. Focus on trends, opportunities, and recommendations.
"""
            
            result = await self.reason(
                prompt=prompt,
                max_tokens=500,
                temperature=0.6
            )
            
            insights = json.loads(result['response'])
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            raise
