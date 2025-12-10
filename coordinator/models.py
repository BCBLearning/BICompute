from datetime import datetime
import uuid

def generate_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

class Worker:
    def __init__(self, data):
        self.id = generate_id("WRK")
        self.name = data.get("name")
        self.cpu = data.get("cpu_cores", 1)
        self.memory = data.get("memory_mb", 0)
        self.platform = data.get("platform")
        self.last_seen = datetime.utcnow()
        self.tasks_completed = 0

class Task:
    def __init__(self, data):
        self.id = generate_id("TSK")
        self.name = data.get("name")
        self.type = data.get("type")
        self.command = data.get("command")
        self.status = "pending"
        self.created_at = datetime.utcnow().isoformat()
        self.completed_at = None
        self.results = []