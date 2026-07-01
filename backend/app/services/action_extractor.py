# backend/app/services/action_extractor.py
import re
from typing import List, Dict
from transformers import pipeline

class ActionItemExtractor:
    """Extract action items from transcript."""
    
    def __init__(self):
        self.ner_pipeline = pipeline(
            "token-classification",
            model="dslim/bert-base-NER"
        )
    
    def extract_actions(self, text: str) -> List[Dict]:
        """Extract action items from text."""
        # Pattern-based extraction
        action_patterns = [
            r'(?:should|must|need to|has to|will|shall)\s+(\w+\s+[\w\s]+)',
            r'(?:action item|next step|todo|task):\s*([^\n]+)',
            r'(?:assign|appoint|designate)\s+([^\n]+)'
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                actions.append({
                    'description': match.strip(),
                    'priority': self._determine_priority(match),
                    'deadline': self._extract_deadline(match)
                })
        
        # Remove duplicates
        unique_actions = []
        seen = set()
        for action in actions:
            desc = action['description'].lower()
            if desc not in seen:
                unique_actions.append(action)
                seen.add(desc)
        
        return unique_actions
    
    def _determine_priority(self, text: str) -> str:
        """Determine priority of action item."""
        if re.search(r'(?:urgent|asap|immediately|critical|high priority)', text, re.IGNORECASE):
            return 'high'
        elif re.search(r'(?:later|eventually|low priority)', text, re.IGNORECASE):
            return 'low'
        return 'medium'
    
    def _extract_deadline(self, text: str) -> str:
        """Extract deadline from text."""
        deadline_pattern = r'(?:by|before|deadline|due)\s+([^\s,.;]+)'
        match = re.search(deadline_pattern, text, re.IGNORECASE)
        return match.group(1) if match else 'TBD'