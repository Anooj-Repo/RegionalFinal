"""
Background Job Scheduler for Vector DB Indexing & Sync (backend/app/core/scheduler.py)
Runs VectorImporter.sync_all_projects() periodically in background threads.
"""

import threading
import time
from backend.app.services.vector_importer import VectorImporter

class VectorStoreScheduler:
    _instance = None
    _thread = None
    _running = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start(self, interval_seconds: int = 300):
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, args=(interval_seconds,), daemon=True)
        self._thread.start()
        print(f"[VectorStoreScheduler] Started background vector indexing thread (interval: {interval_seconds}s).")

    def _run_loop(self, interval_seconds: int):
        importer = VectorImporter()
        # Initial sync on boot
        try:
            importer.sync_all_projects()
        except Exception as e:
            print(f"[VectorStoreScheduler Initial Sync Error] {e}")

        while self._running:
            time.sleep(interval_seconds)
            try:
                importer.sync_all_projects()
            except Exception as e:
                print(f"[VectorStoreScheduler Loop Error] {e}")

    def stop(self):
        self._running = False

def start_background_scheduler():
    scheduler = VectorStoreScheduler.get_instance()
    scheduler.start(interval_seconds=300)
