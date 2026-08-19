import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Union
from .test import Test
from ..errors import AppError

class TestStore:
    __test__ = False
    """In-memory test store with optional JSON file persistence."""
    def __init__(self, work_dir: Union[str, Path] = "."):
        self.work_dir = Path(work_dir)
        self._tests: Dict[str, Test] = {}
        self._lock = asyncio.Lock()

    async def create(self, test: Test) -> Test:
        async with self._lock:
            if test.id in self._tests:
                raise AppError(f"Test with id '{test.id}' already exists")
            self._tests[test.id] = test
            return test

    async def update(self, test: Test) -> Test:
        async with self._lock:
            if test.id not in self._tests:
                raise AppError(f"Test '{test.id}' not found")
            self._tests[test.id] = test
            return test

    async def delete(self, test_id: str) -> None:
        async with self._lock:
            if test_id not in self._tests:
                raise AppError(f"Test '{test_id}' not found")
            del self._tests[test_id]
            file_path = self._test_path(test_id)
            if file_path.exists():
                try:
                    os.remove(file_path)
                except OSError as e:
                    raise AppError(f"Failed to delete test file: {e}")

    async def save(self, test_id: str) -> Path:
        async with self._lock:
            test = self._tests.get(test_id)
            if not test:
                raise AppError(f"Test '{test_id}' not found in memory")
            self.work_dir.mkdir(parents=True, exist_ok=True)
            file_path = self._test_path(test_id)
            try:
                data = test.model_dump()
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                return file_path
            except Exception as e:
                raise AppError(f"Failed to write test file: {e}")

    async def list(self) -> List[Test]:
        async with self._lock:
            return list(self._tests.values())

    async def get(self, test_id: str) -> Optional[Test]:
        async with self._lock:
            return self._tests.get(test_id)

    def _test_path(self, test_id: str) -> Path:
        safe_id = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in test_id)
        return self.work_dir / f"{safe_id}.test.json"
