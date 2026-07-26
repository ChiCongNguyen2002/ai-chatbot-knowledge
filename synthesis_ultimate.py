"""
SYNTHESIS - Smart Structured Answers (No Ollama!)
Returns high-quality formatted answers using document content.
"""

from typing import List, Dict
from synthesis_fallback import get_fallback_response

def get_synthesis_response(question: str, docs: List[Dict]) -> Dict:
    """Wrapper - always use fallback (Ollama not reliable on Railway)"""
    return get_fallback_response(question, docs)
