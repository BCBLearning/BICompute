workers = {}
tasks = {}

def active_workers():
    return list(workers.values())

def pending_tasks():
    return [t for t in tasks.values() if t.status == "pending"]