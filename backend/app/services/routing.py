from typing import Literal

class Router:
    def route_query(self, query: str) -> Literal["rag", "chat", "skip"]:
        """
        Determine how to handle the query.
        """
        normalized = query.lower().strip()
        
        # Rule 1: Greetings
        greetings = ["hi", "hello", "hey", "good morning", "good evening"]
        if normalized in greetings:
            return "chat"
            
        # Rule 2: Very short queries (unlikely to need retrieval)
        # Exception: "metrics?" or "status" might be commands, but for now treat as chat
        if len(normalized.split()) < 2 and normalized not in ["help", "info"]:
            return "chat"
            
        # Default
        return "rag"
