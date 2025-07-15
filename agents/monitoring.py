from .base import BaseAgent
import time

class MonitoringAgent(BaseAgent):
    def __init__(self, name, check_interval=3600):
        super().__init__(name)
        self.check_interval = check_interval  # seconds

    def run(self, health_check_func, improvement_func, context):
        print(f"[MonitoringAgent] Starting continuous monitoring every {self.check_interval} seconds...")
        while context.status == "complete":
            print("[MonitoringAgent] Running health check...")
            healthy = health_check_func()
            if not healthy:
                print("[MonitoringAgent] Issue detected! Triggering improvement loop...")
                improvement_func()
            else:
                print("[MonitoringAgent] System healthy.")
            time.sleep(self.check_interval) 