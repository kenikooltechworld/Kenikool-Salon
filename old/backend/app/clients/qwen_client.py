"""
Qwen3-Reranker Client for Language Detection
Communicates with Qwen3-Reranker Docker container for multilingual language detection
"""

import logging
from typing import Dict, List, Tuple
from .base_client import BaseDockerClient

logger = logging.getLogger(__name__)


class QwenClient(BaseDockerClient):
    """Client for Qwen3-Reranker Docker container"""
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'yo': 'Yoruba',
        'ig': 'Igbo',
        'ha': 'Hausa',
        'pcm': 'Nigerian Pidgin'
    }
    
    async def detect_language(self, text: str) -> Dict[str, any]:
        """
        Detect language from text
        
        Args:
            text: Input text
            
        Returns:
            dict with keys:
                - language: Detected language code
                - confidence: Confidence score
                - alternatives: List of (language, score) tuples
                
        Raises:
            httpx.HTTPError: If detection fails
        """
        try:
            # Build language detection prompt
            prompt = self._build_detection_prompt(text)
            
            payload = {
                'query': text,
                'documents': list(self.SUPPORTED_LANGUAGES.values()),
                'top_k': 5
            }
            
            response = await self._post(
                '/rerank',
                json_data=payload
            )
            
            result = response.json()
            
            # Parse reranking results
            scores = result.get('results', [])
            
            if not scores:
                return {
                    'language': 'en',  # Default to English
                    'confidence': 0.5,
                    'alternatives': []
                }
            
            # Map document indices back to language codes
            lang_codes = list(self.SUPPORTED_LANGUAGES.keys())
            
            detected_lang = lang_codes[scores[0]['index']]
            confidence = scores[0]['relevance_score']
            
            alternatives = [
                (lang_codes[score['index']], score['relevance_score'])
                for score in scores[1:5]
            ]
            
            logger.info(f"Detected language: {detected_lang} (confidence: {confidence:.2f})")
            
            return {
                'language': detected_lang,
                'confidence': confidence,
                'alternatives': alternatives
            }
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            # Fallback to simple heuristic
            return self._fallback_detection(text)
    
    def _build_detection_prompt(self, text: str) -> str:
        """Build prompt for language detection"""
        return f"Identify the language of this text: {text}"
    
    def _fallback_detection(self, text: str) -> Dict[str, any]:
        """
        Fallback language detection using simple heuristics
        
        Args:
            text: Input text
            
        Returns:
            Detection result with low confidence
        """
        text_lower = text.lower()
        
        # Simple keyword-based detection
        yoruba_keywords = ['ṣe', 'ẹ', 'ọ', 'ń', 'gbogbo', 'nibo', 'bawo']
        igbo_keywords = ['nke', 'na', 'ọ', 'ị', 'kedu', 'gini']
        hausa_keywords = ['da', 'na', 'ya', 'ta', 'yaya', 'ina']
        pidgin_keywords = ['wetin', 'dey', 'no', 'go', 'fit', 'make']
        
        scores = {
            'yo': sum(1 for kw in yoruba_keywords if kw in text_lower),
            'ig': sum(1 for kw in igbo_keywords if kw in text_lower),
            'ha': sum(1 for kw in hausa_keywords if kw in text_lower),
            'pcm': sum(1 for kw in pidgin_keywords if kw in text_lower),
            'en': 1  # Default score for English
        }
        
        detected_lang = max(scores, key=scores.get)
        max_score = scores[detected_lang]
        
        # Normalize confidence
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        alternatives = [
            (lang, score / total_score)
            for lang, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[1:4]
        ]
        
        logger.warning(f"Using fallback detection: {detected_lang} (confidence: {confidence:.2f})")
        
        return {
            'language': detected_lang,
            'confidence': confidence,
            'alternatives': alternatives
        }
    
    async def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5
    ) -> List[Dict[str, any]]:
        """
        Rerank documents based on relevance to query
        
        Args:
            query: Search query
            documents: List of documents to rank
            top_k: Number of top results to return
            
        Returns:
            List of ranked documents with scores
        """
        try:
            payload = {
                'query': query,
                'documents': documents,
                'top_k': min(top_k, len(documents))
            }
            
            response = await self._post(
                '/rerank',
                json_data=payload
            )
            
            result = response.json()
            
            return result.get('results', [])
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            raise
