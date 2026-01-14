"""
Fuzzy Name Matching Module

Uses n-gram cosine similarity and sequence matching for intelligent name search.
"""

import math
from difflib import SequenceMatcher
from typing import TypedDict


class EmployeeInfo(TypedDict):
    """Public employee information (excludes salary)."""
    name: str
    email: str
    role: str
    department: str


class FuzzyNameMatcher:
    """Fuzzy name matcher using cosine similarity and sequence matching."""
    
    FUZZY_THRESHOLD = 0.4
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    NGRAM_SIZE = 2
    
    def __init__(self, employees: list[dict]):
        self.employees = employees
        self._name_ngrams: dict[str, set[str]] = {}
        self._precompute_ngrams()
    
    def _precompute_ngrams(self) -> None:
        for emp in self.employees:
            name = emp["name"].lower()
            self._name_ngrams[name] = self._get_ngrams(name)
    
    def _get_ngrams(self, text: str) -> set[str]:
        text = f" {text.lower().strip()} "
        return {text[i:i+self.NGRAM_SIZE] for i in range(len(text) - self.NGRAM_SIZE + 1)}
    
    def _cosine_similarity(self, set1: set[str], set2: set[str]) -> float:
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        magnitude = math.sqrt(len(set1)) * math.sqrt(len(set2))
        return intersection / magnitude if magnitude > 0 else 0.0
    
    def _sequence_similarity(self, str1: str, str2: str) -> float:
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _combined_similarity(self, query: str, name: str) -> float:
        query_lower = query.lower().strip()
        name_lower = name.lower().strip()
        
        name_ngrams = self._name_ngrams.get(name_lower) or self._get_ngrams(name_lower)
        query_ngrams = self._get_ngrams(query_lower)
        
        cosine_score = self._cosine_similarity(query_ngrams, name_ngrams)
        sequence_score = self._sequence_similarity(query_lower, name_lower)
        
        # Check individual name parts
        name_parts = name_lower.split()
        best_part_score = max(
            (self._sequence_similarity(query_lower, part) for part in name_parts),
            default=0.0
        )
        
        return 0.4 * cosine_score + 0.3 * sequence_score + 0.3 * best_part_score
    
    def _format_employee(self, employee: dict) -> EmployeeInfo:
        return {
            "name": employee["name"],
            "email": employee["email"],
            "role": employee["role"],
            "department": employee["department"],
        }
    
    def search(self, query: str, top_k: int = 3) -> dict:
        """Search for employee by name with fuzzy matching."""
        query = query.strip()
        query_lower = query.lower()
        
        # 1. Exact match
        for emp in self.employees:
            if emp["name"].lower() == query_lower:
                return {
                    "found": True,
                    "match_type": "exact",
                    "employee": self._format_employee(emp),
                    "suggestions": [],
                    "message": f"Found employee: {emp['name']}"
                }
        
        # 2. Partial match (first/last name)
        partial_matches = []
        for emp in self.employees:
            name_parts = emp["name"].lower().split()
            if query_lower in name_parts or any(query_lower in part for part in name_parts):
                partial_matches.append(emp)
        
        if len(partial_matches) == 1:
            emp = partial_matches[0]
            return {
                "found": True,
                "match_type": "partial",
                "employee": self._format_employee(emp),
                "suggestions": [],
                "message": f"Found employee: {emp['name']}"
            }
        elif len(partial_matches) > 1:
            return {
                "found": False,
                "match_type": "multiple",
                "employee": None,
                "suggestions": [
                    {"employee": self._format_employee(emp), "score": 1.0, "match_type": "partial"}
                    for emp in partial_matches
                ],
                "message": f"Multiple employees match '{query}'. Please specify full name."
            }
        
        # 3. Fuzzy matching
        scored_matches = [
            {"employee": self._format_employee(emp), "score": round(score, 3), "match_type": "fuzzy"}
            for emp in self.employees
            if (score := self._combined_similarity(query, emp["name"])) >= self.FUZZY_THRESHOLD
        ]
        scored_matches.sort(key=lambda x: x["score"], reverse=True)
        
        # High confidence auto-accept
        if scored_matches and scored_matches[0]["score"] >= self.HIGH_CONFIDENCE_THRESHOLD:
            return {
                "found": True,
                "match_type": "fuzzy_high_confidence",
                "employee": scored_matches[0]["employee"],
                "suggestions": scored_matches[1:top_k],
                "message": f"Found employee: {scored_matches[0]['employee']['name']}"
            }
        
        # Return suggestions
        if scored_matches:
            names = [s["employee"]["name"] for s in scored_matches[:top_k]]
            return {
                "found": False,
                "match_type": "fuzzy_suggestions",
                "employee": None,
                "suggestions": scored_matches[:top_k],
                "message": f"Did you mean: {', '.join(names)}?"
            }
        
        return {
            "found": False,
            "match_type": "not_found",
            "employee": None,
            "suggestions": [],
            "message": f"Employee '{query}' not found. No similar names."
        }
