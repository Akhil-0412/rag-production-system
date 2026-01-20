import json
import os
import time
from typing import Dict, Any

class MonitoringService:
    def __init__(self, log_file: str = "metrics.jsonl"):
        self.log_file = log_file
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                pass

    def log_request(self, 
                    query: str, 
                    response: str, 
                    latency_ms: float, 
                    tokens: int = 0, 
                    cost: float = 0.0,
                    model: str = "unknown",
                    retrieval_count: int = 0):
        """
        Log metrics to JSONL file.
        In production, this would write to Postgres or Prometheus/Grafana.
        """
        record = {
            "timestamp": time.time(),
            "query": query,
            # Truncate response for logging
            "response": response[:100] + "..." if len(response) > 100 else response,
            "latency_ms": latency_ms,
            "tokens": tokens,
            "cost": cost,
            "model": model,
            "retrieval_count": retrieval_count
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"Monitoring Log Error: {e}")

    def get_recent_metrics(self, limit: int = 50) -> list:
        """
        Read recent metrics for dashboard.
        """
        if not os.path.exists(self.log_file):
            return []
            
        lines = []
        try:
            # Read last N lines (inefficient for large files, use shell tail or deque in prod)
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except:
            return []
            
        records = [json.loads(line) for line in lines[-limit:]]
        return list(reversed(records))
