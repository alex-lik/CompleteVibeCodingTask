"""
Тесты для MCP адаптера
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from mcp import MCPAdapter, MCPConfig, MCPContextManager, create_mcp_context


class TestMCPConfig:
    """Тесты для MCPConfig"""

    def test_mcp_config_creation(self):
        """Тест создания конфигурации MCP"""
        config = MCPConfig(
            base_url="http://localhost:8001",
            api_key="test-key",
            timeout=60,
            retry_attempts=5
        )

        assert config.base_url == "http://localhost:8001"
        assert config.api_key == "test-key"
        assert config.timeout == 60
        assert config.retry_attempts == 5

    def test_mcp_config_defaults(self):
        """Тест значений по умолчанию"""
        config = MCPConfig(
            base_url="http://localhost:8001",
            api_key="test-key"
        )

        assert config.timeout == 30
        assert config.retry_attempts == 3


class TestMCPAdapter:
    """Тесты для MCPAdapter"""

    @pytest.fixture
    def mock_config(self):
        """Фикстура с тестовой конфигурацией"""
        return MCPConfig(
            base_url="http://test-api:8001",
            api_key="test-api-key",
            timeout=5,
            retry_attempts=2
        )

    @pytest.fixture
    def mock_session(self):
        """Фикстура с мок сессией"""
        session = AsyncMock()
        session.request = AsyncMock()
        session.aclose = AsyncMock()
        return session

    @pytest.fixture
    async def mcp_adapter(self, mock_config):
        """Фикстура с MCP адаптером"""
        adapter = MCPAdapter(mock_config)
        return adapter

    @pytest.mark.asyncio
    async def test_adapter_context_manager(self, mcp_adapter):
        """Тест контекстного менеджера"""
        with patch('httpx.AsyncClient') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session

            async with mcp_adapter as adapter:
                assert adapter.session is not None
                assert adapter is mcp_adapter

            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_task_success(self, mcp_adapter, mock_session):
        """Тест успешного запуска задачи"""
        # Мокаем ответ API
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "task_id": "test-task-123",
            "message": "Task started successfully"
        }
        mock_session.request.return_value = mock_response

        # Мокаем сессию
        mcp_adapter.session = mock_session

        result = await mcp_adapter.start_task(
            project="test-project",
            task="Test task description",
            task_id="test-task-123",
            agent="test-agent",
            metadata={"priority": "high"}
        )

        assert result["status"] == "success"
        assert result["task_id"] == "test-task-123"

        # Проверяем, что был сделан правильный запрос
        mock_session.request.assert_called_once_with(
            "POST",
            "http://test-api:8001/webhook/start",
            json={
                "project": "test-project",
                "task": "Test task description",
                "task_id": "test-task-123",
                "agent": "test-agent",
                "metadata": {"priority": "high"}
            }
        )

    @pytest.mark.asyncio
    async def test_finish_task_success(self, mcp_adapter, mock_session):
        """Тест успешного завершения задачи"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "message": "Task finished successfully"
        }
        mock_session.request.return_value = mock_response

        mcp_adapter.session = mock_session

        result = await mcp_adapter.finish_task(
            project="test-project",
            task="Test task description",
            task_id="test-task-123",
            agent="test-agent",
            result="Task completed",
            duration_seconds=300,
            metadata={"files": ["result.txt"]}
        )

        assert result["status"] == "success"
        mock_session.request.assert_called_once_with(
            "POST",
            "http://test-api:8001/webhook/finish",
            json={
                "project": "test-project",
                "task": "Test task description",
                "task_id": "test-task-123",
                "agent": "test-agent",
                "result": "Task completed",
                "duration_seconds": 300,
                "metadata": {"files": ["result.txt"]}
            }
        )

    @pytest.mark.asyncio
    async def test_update_status_success(self, mcp_adapter, mock_session):
        """Тест успешного обновления статуса"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "status": "success",
            "message": "Status updated successfully"
        }
        mock_session.request.return_value.__aenter__.return_value = mock_response

        mcp_adapter.session = mock_session

        result = await mcp_adapter.update_status(
            project="test-project",
            task="Test task description",
            task_id="test-task-123",
            agent="test-agent",
            status="running",
            progress=75,
            message="Processing data"
        )

        assert result["status"] == "success"
        mock_session.request.assert_called_once_with(
            "POST",
            "http://test-api:8001/webhook/status",
            json={
                "project": "test-project",
                "task": "Test task description",
                "task_id": "test-task-123",
                "agent": "test-agent",
                "status": "running",
                "progress": 75,
                "message": "Processing data",
                "metadata": {}
            }
        )

    @pytest.mark.asyncio
    async def test_report_error_success(self, mcp_adapter, mock_session):
        """Тест успешного отчета об ошибке"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "status": "success",
            "message": "Error reported successfully"
        }
        mock_session.request.return_value.__aenter__.return_value = mock_response

        mcp_adapter.session = mock_session

        result = await mcp_adapter.report_error(
            project="test-project",
            task="Test task description",
            task_id="test-task-123",
            agent="test-agent",
            error_type="ValueError",
            error_message="Invalid input data",
            stack_trace="Traceback...",
            metadata={"attempt": 2}
        )

        assert result["status"] == "success"
        mock_session.request.assert_called_once_with(
            "POST",
            "http://test-api:8001/webhook/error",
            json={
                "project": "test-project",
                "task": "Test task description",
                "task_id": "test-task-123",
                "agent": "test-agent",
                "error_type": "ValueError",
                "error_message": "Invalid input data",
                "stack_trace": "Traceback...",
                "metadata": {"attempt": 2}
            }
        )

    @pytest.mark.asyncio
    async def test_get_projects_success(self, mcp_adapter, mock_session):
        """Тест получения списка проектов"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "projects": [
                {"id": 1, "name": "project1"},
                {"id": 2, "name": "project2"}
            ]
        }
        mock_session.request.return_value.__aenter__.return_value = mock_response

        mcp_adapter.session = mock_session

        projects = await mcp_adapter.get_projects()

        assert len(projects) == 2
        assert projects[0]["name"] == "project1"
        assert projects[1]["name"] == "project2"

        mock_session.request.assert_called_once_with("GET", "http://test-api:8001/api/projects")

    @pytest.mark.asyncio
    async def test_api_error_handling(self, mcp_adapter, mock_session):
        """Тест обработки ошибок API"""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text.return_value = "Unauthorized"
        mock_session.request.return_value.__aenter__.return_value = mock_response

        mcp_adapter.session = mock_session

        with pytest.raises(ValueError, match="Invalid API key"):
            await mcp_adapter.start_task(
                project="test-project",
                task="Test task",
                task_id="test-task-123",
                agent="test-agent"
            )

    @pytest.mark.asyncio
    async def test_no_session_error(self, mcp_adapter):
        """Тест ошибки при отсутствии сессии"""
        with pytest.raises(RuntimeError, match="MCPAdapter must be used as async context manager"):
            await mcp_adapter.start_task(
                project="test-project",
                task="Test task",
                task_id="test-task-123",
                agent="test-agent"
            )


class TestMCPContextManager:
    """Тесты для MCPContextManager"""

    @pytest.mark.asyncio
    async def test_context_manager_lifecycle(self):
        """Тест жизненного цикла контекстного менеджера"""
        with patch('mcp.MCPAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter_class.return_value = mock_adapter

            mock_adapter.__aenter__.return_value = mock_adapter
            mock_adapter.__aexit__.return_value = None

            async with create_mcp_context("test-agent", "test-project") as ctx:
                assert ctx.agent_name == "test-agent"
                assert ctx.project_name == "test-project"
                assert ctx.adapter is not None
                assert ctx.current_task_id is None
                assert ctx.start_time is None

            mock_adapter.__aenter__.assert_called_once()
            mock_adapter.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_task_in_context(self):
        """Тест запуска задачи в контексте"""
        with patch('mcp.MCPAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter_class.return_value = mock_adapter
            mock_adapter.__aenter__.return_value = mock_adapter
            mock_adapter.start_task.return_value = {"status": "success"}

            async with create_mcp_context("test-agent", "test-project") as ctx:
                task_id = await ctx.start_task(
                    task_description="Test task",
                    task_id="custom-task-id",
                    metadata={"priority": "high"}
                )

                assert task_id == "custom-task-id"
                assert ctx.current_task_id == "custom-task-id"
                assert ctx.start_time is not None

                mock_adapter.start_task.assert_called_once_with(
                    project="test-project",
                    task="Test task",
                    task_id="custom-task-id",
                    agent="test-agent",
                    metadata={"priority": "high"}
                )

    @pytest.mark.asyncio
    async def test_auto_task_id_generation(self):
        """Тест автоматической генерации ID задачи"""
        with patch('mcp.MCPAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter_class.return_value = mock_adapter
            mock_adapter.__aenter__.return_value = mock_adapter
            mock_adapter.start_task.return_value = {"status": "success"}

            with patch('mcp.datetime') as mock_datetime:
                mock_now = MagicMock()
                mock_now.timestamp.return_value = 1640995200.0  # Fixed timestamp
                mock_datetime.now.return_value = mock_now

                async with create_mcp_context("test-agent", "test-project") as ctx:
                    task_id = await ctx.start_task(task_description="Test task")

                    expected_id = "test-agent-1640995200"
                    assert task_id == expected_id
                    assert ctx.current_task_id == expected_id

    @pytest.mark.asyncio
    async def test_update_progress(self):
        """Тест обновления прогресса"""
        with patch('mcp.MCPAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter_class.return_value = mock_adapter
            mock_adapter.__aenter__.return_value = mock_adapter
            mock_adapter.start_task.return_value = {"status": "success"}

            async with create_mcp_context("test-agent", "test-project") as ctx:
                await ctx.start_task(task_description="Test task")
                await ctx.update_progress(50, "Half done")

                mock_adapter.update_status.assert_called_once_with(
                    project="test-project",
                    task="",
                    task_id=ctx.current_task_id,
                    agent="test-agent",
                    status="running",
                    progress=50,
                    message="Half done"
                )

    @pytest.mark.asyncio
    async def test_complete_task(self):
        """Тест завершения задачи"""
        with patch('mcp.MCPAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter_class.return_value = mock_adapter
            mock_adapter.__aenter__.return_value = mock_adapter
            mock_adapter.start_task.return_value = {"status": "success"}

            async with create_mcp_context("test-agent", "test-project") as ctx:
                # Устанавливаем время начала для теста duration
                start_time = datetime.now()
                ctx.start_time = start_time
                ctx.current_task_id = "test-task-id"

                await ctx.complete_task(
                    result="Task completed",
                    metadata={"files": 1}
                )

                mock_adapter.finish_task.assert_called_once()
                call_args = mock_adapter.finish_task.call_args[1]

                assert call_args["project"] == "test-project"
                assert call_args["task_id"] == "test-task-id"
                assert call_args["agent"] == "test-agent"
                assert call_args["result"] == "Task completed"
                assert call_args["metadata"]["files"] == 1
                assert call_args["duration_seconds"] is not None

    @pytest.mark.asyncio
    async def test_fail_task(self):
        """Тест обработки ошибки задачи"""
        with patch('mcp.MCPAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter_class.return_value = mock_adapter
            mock_adapter.__aenter__.return_value = mock_adapter
            mock_adapter.start_task.return_value = {"status": "success"}

            async with create_mcp_context("test-agent", "test-project") as ctx:
                ctx.current_task_id = "test-task-id"

                await ctx.fail_task(
                    error_type="ValueError",
                    error_message="Something went wrong",
                    stack_trace="Traceback..."
                )

                mock_adapter.report_error.assert_called_once_with(
                    project="test-project",
                    task="",
                    task_id="test-task-id",
                    agent="test-agent",
                    error_type="ValueError",
                    error_message="Something went wrong",
                    stack_trace="Traceback..."
                )

    @pytest.mark.asyncio
    async def test_no_current_task_operations(self):
        """Тест операций без текущей задачи"""
        with patch('mcp.MCPAdapter') as mock_adapter_class:
            mock_adapter = AsyncMock()
            mock_adapter_class.return_value = mock_adapter
            mock_adapter.__aenter__.return_value = mock_adapter

            async with create_mcp_context("test-agent", "test-project") as ctx:
                # Не начинаем задачу
                assert ctx.current_task_id is None

                # Операции должны выполняться без ошибок, но без вызовов API
                await ctx.update_progress(50, "Test")
                await ctx.complete_task("Done")
                await ctx.fail_task("Error", "Message")

                # Никаких вызовов API не должно быть
                mock_adapter.update_status.assert_not_called()
                mock_adapter.finish_task.assert_not_called()
                mock_adapter.report_error.assert_not_called()


class TestCreateMCPContext:
    """Тесты для функции create_mcp_context"""

    def test_create_mcp_context(self):
        """Тест создания MCP контекста"""
        ctx = create_mcp_context("test-agent", "test-project")

        assert isinstance(ctx, MCPContextManager)
        assert ctx.agent_name == "test-agent"
        assert ctx.project_name == "test-project"
        assert ctx.adapter is None
        assert ctx.current_task_id is None
        assert ctx.start_time is None


@pytest.mark.asyncio
async def test_integration_example():
    """Интеграционный тест использования MCP адаптера"""
    # Этот тест демонстрирует полный сценарий использования
    with patch('mcp.MCPAdapter') as mock_adapter_class:
        mock_adapter = AsyncMock()
        mock_adapter_class.return_value = mock_adapter

        # Мокаем успешные ответы для всех операций
        mock_adapter.__aenter__.return_value = mock_adapter
        mock_adapter.__aexit__.return_value = None
        mock_adapter.start_task.return_value = {"status": "success", "task_id": "integration-test"}
        mock_adapter.update_status.return_value = {"status": "success"}
        mock_adapter.finish_task.return_value = {"status": "success"}

        async with create_mcp_context("integration-agent", "integration-project") as ctx:
            # Полный рабочий процесс
            task_id = await ctx.start_task(
                task_description="Integration test task",
                metadata={"test": True}
            )

            assert task_id is not None
            assert ctx.current_task_id == task_id

            await ctx.update_progress(25, "Started")
            await ctx.update_progress(50, "Halfway")
            await ctx.update_progress(75, "Almost done")
            await ctx.update_progress(100, "Complete")

            await ctx.complete_task(
                result="Integration test completed successfully",
                metadata={"test_passed": True}
            )

            # Проверяем, что все операции были вызваны
            mock_adapter.start_task.assert_called_once()
            assert mock_adapter.update_status.call_count == 4
            mock_adapter.finish_task.assert_called_once()