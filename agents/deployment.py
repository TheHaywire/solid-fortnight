from .base import BaseAgent
import subprocess
import shutil
import os

class DeploymentAgent(BaseAgent):
    def __init__(self, name):
        super().__init__(name)

    def run(self, recommendation):
        # Expect recommendation to include an install command (e.g., pip install ...)
        print(f"[DeploymentAgent] Installing or running: {recommendation}")
        try:
            result = subprocess.run(recommendation, shell=True, capture_output=True, text=True, timeout=120)
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e)
            }

    def backup(self, target_path, backup_path):
        print(f"[DeploymentAgent] Backing up {target_path} to {backup_path}")
        try:
            if os.path.isdir(target_path):
                shutil.copytree(target_path, backup_path, dirs_exist_ok=True)
            else:
                shutil.copy2(target_path, backup_path)
            return True
        except Exception as e:
            print(f"[DeploymentAgent] Backup failed: {e}")
            return False

    def rollback(self, backup_path, target_path):
        print(f"[DeploymentAgent] Rolling back {target_path} from {backup_path}")
        try:
            if os.path.isdir(backup_path):
                shutil.copytree(backup_path, target_path, dirs_exist_ok=True)
            else:
                shutil.copy2(backup_path, target_path)
            return True
        except Exception as e:
            print(f"[DeploymentAgent] Rollback failed: {e}")
            return False

    def deploy_to_windows_mt5(self, code_path, remote_info):
        # Stub: To be implemented for real Windows/MT5 deployment
        pass 