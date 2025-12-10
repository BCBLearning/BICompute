#!/usr/bin/env python3
"""
BI-COMPUTE CLI
"""

import argparse
import requests
from datetime import datetime

class BICLI:

    def __init__(self, url):
        self.url = url.rstrip("/")

    def health(self):
        r = requests.get(f"{self.url}/api/health")
        print(r.json())

    def submit(self, command, name):
        payload = {
            "name": name or f"CLI Task {datetime.now().isoformat()}",
            "type": "shell",
            "command": {
                "type": "shell",
                "command": command
            }
        }

        r = requests.post(f"{self.url}/api/tasks", json=payload)
        print(r.json())

    def stats(self):
        r = requests.get(f"{self.url}/api/network/stats")
        data = r.json()

        print("\n🌐 BI-COMPUTE NETWORK")
        print("Workers:", data["workers"])
        print("Tasks:", data["tasks"])

    def status(self, task_id):
        r = requests.get(f"{self.url}/api/tasks/{task_id}")
        print(r.json())

# --------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:5000")

    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("health")
    sub.add_parser("stats")

    submit = sub.add_parser("submit")
    submit.add_argument("command")
    submit.add_argument("--name")

    status = sub.add_parser("status")
    status.add_argument("task_id")

    args = parser.parse_args()
    cli = BICLI(args.url)

    if args.cmd == "health":
        cli.health()
    elif args.cmd == "stats":
        cli.stats()
    elif args.cmd == "submit":
        cli.submit(args.command, args.name)
    elif args.cmd == "status":
        cli.status(args.task_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()