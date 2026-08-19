from typing import Dict, Any
from .step_executor import StepExecutor
from .test_executor import TestExecutor
from ..models.command import SocketCommand
from ..models.response import ExecutionResponse, GeneralResponse, PingResponse, StepResult
from ..models.test_store import TestStore
from ..selenium_wrapper.session import SessionManager
from ..errors import AppError

class CommandDispatcher:
    def __init__(self, session_manager: SessionManager, test_store: TestStore):
        self.session_manager = session_manager
        self.test_store = test_store
        self.step_executor = StepExecutor()
        self.test_executor = TestExecutor(self.step_executor)

    async def dispatch(self, command: SocketCommand) -> Dict[str, Any]:
        cmd_name = command.command.lower()

        if cmd_name == "ping":
            return PingResponse(status="pong").model_dump()

        elif cmd_name == "closesession":
            if not command.session_id:
                raise AppError("session_id required for CloseSession")
            await self.session_manager.close_session(command.session_id)
            return GeneralResponse(
                success=True,
                session_id=command.session_id,
                message="Session closed"
            ).model_dump()

        elif cmd_name == "executesteps":
            session = await self.session_manager.get_or_create_session(command.session_id)
            steps = command.steps or []
            async with session._lock:
                session.last_steps = list(steps)

            results = []
            overall_success = True
            for s in steps:
                res = await self.step_executor.execute_step(session.driver, s)
                if res.status != "success":
                    overall_success = False
                results.append(res)

            return ExecutionResponse(
                success=overall_success,
                session_id=session.id,
                results=results
            ).model_dump()

        elif cmd_name == "executetest":
            if not command.test:
                raise AppError("test parameter required for ExecuteTest")
            session = await self.session_manager.get_or_create_session(command.session_id)
            async with session._lock:
                session.last_steps = list(command.test.steps)

            resp = await self.test_executor.execute_test(session.driver, command.test, session.id)
            return resp.model_dump()

        elif cmd_name == "executesteprange":
            if not command.session_id:
                raise AppError("session_id required for ExecuteStepRange")
            session = await self.session_manager.get_or_create_session(command.session_id)
            async with session._lock:
                loaded_steps = list(session.last_steps)

            start = command.start or 0
            end = command.end if command.end is not None else len(loaded_steps)
            if start < 0 or end > len(loaded_steps) or start > end:
                raise AppError(f"Invalid step range [{start}, {end}] for steps count {len(loaded_steps)}")

            target_steps = loaded_steps[start:end]
            results = []
            overall_success = True
            for s in target_steps:
                res = await self.step_executor.execute_step(session.driver, s)
                if res.status != "success":
                    overall_success = False
                results.append(res)

            return ExecutionResponse(
                success=overall_success,
                session_id=session.id,
                results=results
            ).model_dump()

        elif cmd_name == "createtest":
            if not command.test:
                raise AppError("test object required for CreateTest")
            created = await self.test_store.create(command.test)
            return {
                "success": True,
                "message": f"Test '{created.id}' created in memory",
                "test": created.model_dump()
            }

        elif cmd_name == "updatetest":
            if not command.test:
                raise AppError("test object required for UpdateTest")
            updated = await self.test_store.update(command.test)
            return {
                "success": True,
                "message": f"Test '{updated.id}' updated in memory",
                "test": updated.model_dump()
            }

        elif cmd_name == "deletetest":
            if not command.id:
                raise AppError("id required for DeleteTest")
            await self.test_store.delete(command.id)
            return {
                "success": True,
                "message": f"Test '{command.id}' deleted"
            }

        elif cmd_name == "savetest":
            if not command.id:
                raise AppError("id required for SaveTest")
            path = await self.test_store.save(command.id)
            return {
                "success": True,
                "message": f"Test '{command.id}' saved to disk",
                "path": str(path)
            }

        elif cmd_name == "listtests":
            tests = await self.test_store.list()
            return {
                "success": True,
                "count": len(tests),
                "tests": [t.model_dump() for t in tests]
            }

        elif cmd_name == "gettest":
            if not command.id:
                raise AppError("id required for GetTest")
            test = await self.test_store.get(command.id)
            if not test:
                raise AppError(f"Test '{command.id}' not found")
            return {
                "success": True,
                "test": test.model_dump()
            }

        elif cmd_name == "runtest":
            if not command.id:
                raise AppError("id required for RunTest")
            test = await self.test_store.get(command.id)
            if not test:
                raise AppError(f"Test '{command.id}' not found")
            session = await self.session_manager.get_or_create_session(command.session_id)
            async with session._lock:
                session.last_steps = list(test.steps)
            resp = await self.test_executor.execute_test(session.driver, test, session.id)
            return resp.model_dump()

        elif cmd_name == "stopexecution":
            return GeneralResponse(
                success=True,
                session_id=command.session_id,
                message="Stop command dispatched"
            ).model_dump()

        elif cmd_name == "shutdown":
            return GeneralResponse(
                success=True,
                message="Shutdown command received"
            ).model_dump()

        else:
            raise AppError(f"Unsupported command '{command.command}'")
