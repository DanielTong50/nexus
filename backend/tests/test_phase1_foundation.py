"""
Phase 1 Foundation Tests

Comprehensive tests for:
1. Organization configuration models and service
2. TaskPlan models for workflow decomposition
3. MongoDB query tools
4. Notion search tools

Run with: pytest tests/test_phase1_foundation.py -v
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# =============================================================================
# ORGANIZATION CONFIG TESTS
# =============================================================================

class TestOrganizationModels:
    """Tests for organization configuration models."""
    
    def test_slack_channel_mapping_defaults(self):
        """Test default Slack channel mappings."""
        from src.models.organization import SlackChannelMapping
        
        mapping = SlackChannelMapping()
        
        assert mapping.partnerships == "#partnerships"
        assert mapping.marketing == "#marketing"
        assert mapping.finance == "#finance"
        assert mapping.events == "#events"
        assert mapping.developers == "#developers"
    
    def test_slack_channel_resolve_direct(self):
        """Test resolving direct channel names."""
        from src.models.organization import SlackChannelMapping
        
        mapping = SlackChannelMapping()
        
        assert mapping.resolve("partnerships") == "#partnerships"
        assert mapping.resolve("marketing") == "#marketing"
    
    def test_slack_channel_resolve_aliases(self):
        """Test resolving natural language aliases."""
        from src.models.organization import SlackChannelMapping
        
        mapping = SlackChannelMapping()
        
        assert mapping.resolve("partnerships channel") == "#partnerships"
        assert mapping.resolve("event logistics") == "#events"
        assert mapping.resolve("event logistics channel") == "#events"
    
    def test_slack_channel_resolve_custom(self):
        """Test custom channel mappings."""
        from src.models.organization import SlackChannelMapping
        
        mapping = SlackChannelMapping(
            partnerships="#biz-partnerships",
            marketing="#biz-marketing",
            aliases={
                "sponsor updates": "#biz-partnerships",
                "content team": "#biz-marketing",
            }
        )
        
        assert mapping.resolve("partnerships") == "#biz-partnerships"
        assert mapping.resolve("sponsor updates") == "#biz-partnerships"
        assert mapping.resolve("content team") == "#biz-marketing"
    
    def test_slack_channel_resolve_unknown(self):
        """Test resolving unknown channel references."""
        from src.models.organization import SlackChannelMapping
        
        mapping = SlackChannelMapping()
        
        # Unknown channels should be returned with # prefix
        assert mapping.resolve("random-channel") == "#random-channel"
        assert mapping.resolve("#already-prefixed") == "#already-prefixed"
    
    def test_data_source_mapping_defaults(self):
        """Test default data source mappings."""
        from src.models.organization import DataSourceMapping
        
        mapping = DataSourceMapping()
        
        assert mapping.boothing_partnerships == "Boothing Companies"
        assert mapping.event_partnerships == "Event Sponsors"
        assert mapping.judges == "Judges"
        assert mapping.mentors == "Mentors"
    
    def test_data_source_resolve_aliases(self):
        """Test resolving data source aliases."""
        from src.models.organization import DataSourceMapping
        
        mapping = DataSourceMapping()
        
        assert mapping.resolve("boothing partnerships compendium") == "Boothing Companies"
        assert mapping.resolve("event partnerships compendium") == "Event Sponsors"
        assert mapping.resolve("partnership compendium") == "Boothing Companies"
    
    def test_event_config_defaults(self):
        """Test default event configuration."""
        from src.models.organization import EventConfig
        
        config = EventConfig(name="Blueprint")
        
        assert config.name == "Blueprint"
        assert config.sponsorship_goal == 100000
        assert "Platinum Sponsor" in config.sponsorship_tiers
        assert config.sponsorship_tiers["Platinum Sponsor"] == 25000
    
    def test_organization_config_creation(self):
        """Test creating a complete organization config."""
        from src.models.organization import (
            OrganizationConfig,
            SlackChannelMapping,
            DataSourceMapping,
            EventConfig,
        )
        
        config = OrganizationConfig(
            org_id="biztech",
            org_name="BizTech",
            slack_channels=SlackChannelMapping(partnerships="#biz-partnerships"),
            data_sources=DataSourceMapping(boothing_partnerships="BizTech Sponsors"),
            event=EventConfig(name="Blueprint", sponsorship_goal=150000),
        )
        
        assert config.org_id == "biztech"
        assert config.org_name == "BizTech"
        assert config.slack_channels.partnerships == "#biz-partnerships"
        assert config.data_sources.boothing_partnerships == "BizTech Sponsors"
        assert config.event.name == "Blueprint"
        assert config.event.sponsorship_goal == 150000
    
    def test_organization_config_prompt_context(self):
        """Test getting prompt context from org config."""
        from src.models.organization import OrganizationConfig, EventConfig
        
        config = OrganizationConfig(
            org_id="test",
            org_name="Test Org",
            event=EventConfig(name="TestEvent", sponsorship_goal=50000),
        )
        
        context = config.get_context_for_prompts()
        
        assert context["org_name"] == "Test Org"
        assert context["event_name"] == "TestEvent"
        assert context["sponsorship_goal"] == 50000
        assert "partnerships" in context["channels"]
        assert "boothing" in context["data_sources"]
    
    def test_create_default_config(self):
        """Test creating a default configuration."""
        from src.models.organization import create_default_config
        
        config = create_default_config("acme", "ACME Corp", "HackACME")
        
        assert config.org_id == "acme"
        assert config.org_name == "ACME Corp"
        assert config.event.name == "HackACME"


# =============================================================================
# TASK PLAN TESTS
# =============================================================================

class TestTaskPlanModels:
    """Tests for task planning models."""
    
    def test_task_creation(self):
        """Test creating a task."""
        from src.models.task_plan import Task
        
        task = Task(
            id="task_1",
            agent="partnerships",
            action="log_partnership_status",
            parameters={"company": "Google", "status": "Confirmed"},
            description="Log Google sponsorship in compendium",
        )
        
        assert task.id == "task_1"
        assert task.agent == "partnerships"
        assert task.action == "log_partnership_status"
        assert task.parameters["company"] == "Google"
        assert task.status == "pending"
    
    def test_task_with_dependencies(self):
        """Test task with dependencies."""
        from src.models.task_plan import Task
        
        task = Task(
            id="task_2",
            agent="events",
            action="send_team_message",
            parameters={"channel": "#partnerships", "message": "Update..."},
            description="Notify partnerships channel",
            depends_on=["task_1"],
        )
        
        assert task.depends_on == ["task_1"]
        assert not task.is_ready(set())  # No tasks completed
        assert task.is_ready({"task_1"})  # Dependency completed
    
    def test_task_status_transitions(self):
        """Test task status transitions."""
        from src.models.task_plan import Task
        
        task = Task(
            id="task_1",
            agent="partnerships",
            action="test_action",
            parameters={},
            description="Test task",
        )
        
        assert task.status == "pending"
        assert task.started_at is None
        
        task.mark_running()
        assert task.status == "running"
        assert task.started_at is not None
        
        task.mark_completed({"success": True})
        assert task.status == "completed"
        assert task.result == {"success": True}
        assert task.completed_at is not None
    
    def test_task_failure(self):
        """Test task failure handling."""
        from src.models.task_plan import Task
        
        task = Task(
            id="task_1",
            agent="partnerships",
            action="test_action",
            parameters={},
            description="Test task",
        )
        
        task.mark_running()
        task.mark_failed("Connection timeout")
        
        assert task.status == "failed"
        assert task.error == "Connection timeout"
    
    def test_task_skipped(self):
        """Test task skipping due to dependency failure."""
        from src.models.task_plan import Task
        
        task = Task(
            id="task_2",
            agent="events",
            action="send_message",
            parameters={},
            description="Send update",
            depends_on=["task_1"],
        )
        
        task.mark_skipped("Dependency task_1 failed")
        
        assert task.status == "skipped"
        assert "task_1" in task.error
    
    def test_task_plan_creation(self):
        """Test creating a task plan."""
        from src.models.task_plan import TaskPlan, Task
        
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Log"),
            Task(id="t2", agent="events", action="notify", parameters={}, description="Notify", depends_on=["t1"]),
        ]
        
        plan = TaskPlan(
            plan_id="plan_1",
            request_id="req_1",
            request_type="workflow",
            tasks=tasks,
            execution_strategy="mixed",
        )
        
        assert plan.plan_id == "plan_1"
        assert len(plan.tasks) == 2
        assert plan.request_type == "workflow"
    
    def test_task_plan_ready_tasks(self):
        """Test getting ready tasks from a plan."""
        from src.models.task_plan import TaskPlan, Task
        
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Log"),
            Task(id="t2", agent="events", action="notify", parameters={}, description="Notify", depends_on=["t1"]),
            Task(id="t3", agent="finance", action="invoice", parameters={}, description="Invoice", depends_on=["t1"]),
        ]
        
        plan = TaskPlan(plan_id="plan_1", request_id="req_1", tasks=tasks)
        
        # Initially only t1 is ready
        ready = plan.get_ready_tasks(set())
        assert len(ready) == 1
        assert ready[0].id == "t1"
        
        # After t1 completes, t2 and t3 are ready
        ready = plan.get_ready_tasks({"t1"})
        assert len(ready) == 2
        assert {t.id for t in ready} == {"t2", "t3"}
    
    def test_task_plan_all_complete(self):
        """Test checking if all tasks are complete."""
        from src.models.task_plan import TaskPlan, Task
        
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Log"),
            Task(id="t2", agent="events", action="notify", parameters={}, description="Notify"),
        ]
        
        plan = TaskPlan(plan_id="plan_1", request_id="req_1", tasks=tasks)
        
        assert not plan.all_complete()
        
        plan.tasks[0].mark_completed({})
        assert not plan.all_complete()
        
        plan.tasks[1].mark_completed({})
        assert plan.all_complete()
    
    def test_task_plan_target_agents(self):
        """Test target agents extraction."""
        from src.models.task_plan import create_task_plan
        
        tasks = [
            {"id": "t1", "agent": "partnerships", "action": "log", "parameters": {}, "description": "Log"},
            {"id": "t2", "agent": "events", "action": "notify", "parameters": {}, "description": "Notify"},
            {"id": "t3", "agent": "partnerships", "action": "update", "parameters": {}, "description": "Update"},
        ]
        
        plan = create_task_plan("req_1", "workflow", tasks)
        
        # Should have unique agents
        assert set(plan.target_agents) == {"partnerships", "events"}
    
    def test_task_plan_dependency_graph(self):
        """Test building dependency graph."""
        from src.models.task_plan import TaskPlan, Task
        
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Log"),
            Task(id="t2", agent="events", action="notify", parameters={}, description="Notify", depends_on=["t1"]),
            Task(id="t3", agent="finance", action="invoice", parameters={}, description="Invoice", depends_on=["t1"]),
        ]
        
        plan = TaskPlan(plan_id="plan_1", request_id="req_1", tasks=tasks)
        
        graph = plan.build_dependency_graph()
        
        assert graph["t1"] == ["t2", "t3"]  # t1 has two dependents
        assert graph["t2"] == []  # t2 has no dependents
        assert graph["t3"] == []  # t3 has no dependents
    
    def test_question_plan_to_task(self):
        """Test converting a question plan to a task."""
        from src.models.task_plan import QuestionPlan
        
        question = QuestionPlan(
            question="When will we be filming the teaser video?",
            data_source="notion",
            query_type="search",
            search_terms=["teaser video", "filming"],
        )
        
        task = question.to_task()
        
        assert task.id == "question_task"
        assert task.action == "search_notion"
        assert "teaser video" in task.parameters["search_terms"]


# =============================================================================
# ORGANIZATION SERVICE TESTS (with mocking)
# =============================================================================

class TestOrganizationService:
    """Tests for organization service."""
    
    @pytest.mark.asyncio
    async def test_get_config_creates_default(self):
        """Test that get_config creates default if not found."""
        from src.models.organization import OrganizationConfig
        from src.services.organization import OrganizationService, _org_cache
        
        # Clear cache
        _org_cache.clear()
        
        # Mock the MongoDB collection
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_collection.update_one = AsyncMock()
        
        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        with patch('src.services.organization.db_service') as mock_db_service:
            mock_db_service.db = mock_db
            
            service = OrganizationService()
            config = await service.get_config("new_org")
        
        assert config.org_id == "new_org"
        assert isinstance(config, OrganizationConfig)
        
        # Clean up
        _org_cache.clear()
    
    @pytest.mark.asyncio
    async def test_get_config_loads_from_db(self):
        """Test loading config from database."""
        from src.services.organization import OrganizationService, _org_cache
        
        # Clear cache
        _org_cache.clear()
        
        # Mock the MongoDB collection with existing data
        existing_config = {
            "org_id": "existing_org",
            "org_name": "Existing Organization",
            "slack_channels": {"partnerships": "#existing-partnerships"},
            "data_sources": {},
            "event": {"name": "ExistingEvent"},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
        }
        
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=existing_config)
        
        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        with patch('src.services.organization.db_service') as mock_db_service:
            mock_db_service.db = mock_db
            
            service = OrganizationService()
            config = await service.get_config("existing_org")
        
        assert config.org_id == "existing_org"
        assert config.org_name == "Existing Organization"
        
        # Clean up
        _org_cache.clear()
    
    @pytest.mark.asyncio
    async def test_resolve_channel(self):
        """Test resolving channel through service."""
        from src.services.organization import OrganizationService, _org_cache
        from src.models.organization import OrganizationConfig, SlackChannelMapping
        
        # Pre-populate cache
        _org_cache["test_org"] = OrganizationConfig(
            org_id="test_org",
            org_name="Test",
            slack_channels=SlackChannelMapping(partnerships="#test-partnerships"),
        )
        
        service = OrganizationService()
        channel = await service.resolve_channel("partnerships", "test_org")
        
        assert channel == "#test-partnerships"
        
        # Clean up
        _org_cache.clear()
    
    @pytest.mark.asyncio
    async def test_resolve_data_source(self):
        """Test resolving data source through service."""
        from src.services.organization import OrganizationService, _org_cache
        from src.models.organization import OrganizationConfig, DataSourceMapping
        
        # Pre-populate cache
        _org_cache["test_org"] = OrganizationConfig(
            org_id="test_org",
            org_name="Test",
            data_sources=DataSourceMapping(boothing_partnerships="Test Sponsors"),
        )
        
        service = OrganizationService()
        source = await service.resolve_data_source("boothing partnerships compendium", "test_org")
        
        assert source == "Test Sponsors"
        
        # Clean up
        _org_cache.clear()


# =============================================================================
# MONGODB QUERY TOOL TESTS (with mocking)
# =============================================================================

class TestMongoDBQueryTools:
    """Tests for MongoDB query tools."""
    
    @pytest.mark.asyncio
    async def test_query_event_data_count(self):
        """Test counting documents."""
        from src.tools.mongodb_query import query_event_data
        from src.services.organization import _org_cache
        from src.models.organization import OrganizationConfig
        
        # Set up mock org config
        _org_cache["default"] = OrganizationConfig(
            org_id="default",
            org_name="Test",
        )
        
        # Mock the database service
        mock_collection = MagicMock()
        mock_collection.count_documents = AsyncMock(return_value=42)
        
        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        with patch('src.tools.mongodb_query.db_service') as mock_db_service:
            mock_db_service.db = mock_db
            
            result = await query_event_data.ainvoke({
                "query_type": "count",
                "collection": "delegates",
            })
        
        assert "42" in result
        assert "delegates" in result
        
        # Clean up
        _org_cache.clear()
    
    @pytest.mark.asyncio
    async def test_query_event_data_search(self):
        """Test searching documents."""
        from src.tools.mongodb_query import query_event_data
        from src.services.organization import _org_cache
        from src.models.organization import OrganizationConfig
        
        # Set up mock org config
        _org_cache["default"] = OrganizationConfig(
            org_id="default",
            org_name="Test",
        )
        
        # Mock data
        mock_docs = [
            {"name": "John Doe", "company": "Google", "status": "confirmed"},
            {"name": "Jane Smith", "company": "Meta", "status": "pending"},
        ]
        
        # Mock cursor with chained methods
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_docs)
        
        # Mock collection with chained find().limit()
        mock_limited_cursor = MagicMock()
        mock_limited_cursor.to_list = AsyncMock(return_value=mock_docs)
        
        mock_find_result = MagicMock()
        mock_find_result.limit = MagicMock(return_value=mock_limited_cursor)
        
        mock_collection = MagicMock()
        mock_collection.find = MagicMock(return_value=mock_find_result)
        
        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        with patch('src.tools.mongodb_query.db_service') as mock_db_service:
            mock_db_service.db = mock_db
            
            result = await query_event_data.ainvoke({
                "query_type": "list",
                "collection": "delegates",
                "limit": 10,
            })
        
        assert "Found 2" in result
        assert "John Doe" in result or "Google" in result
        
        # Clean up
        _org_cache.clear()
    
    @pytest.mark.asyncio
    async def test_get_collection_stats(self):
        """Test getting collection statistics."""
        from src.tools.mongodb_query import get_collection_stats
        from src.services.organization import _org_cache
        from src.models.organization import OrganizationConfig
        
        # Set up mock org config
        _org_cache["default"] = OrganizationConfig(
            org_id="default",
            org_name="Test",
        )
        
        # Mock aggregation result
        mock_groups = [
            {"_id": "confirmed", "count": 30},
            {"_id": "pending", "count": 10},
        ]
        
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_groups)
        
        mock_collection = MagicMock()
        mock_collection.count_documents = AsyncMock(return_value=40)
        mock_collection.aggregate = MagicMock(return_value=mock_cursor)
        
        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        with patch('src.tools.mongodb_query.db_service') as mock_db_service:
            mock_db_service.db = mock_db
            
            result = await get_collection_stats.ainvoke({
                "collection": "delegates",
                "group_by": "status",
            })
        
        assert "40" in result  # Total
        assert "confirmed" in result
        assert "30" in result
        
        # Clean up
        _org_cache.clear()


# =============================================================================
# NOTION TOOL TESTS (with mocking)
# =============================================================================

class TestNotionTools:
    """Tests for Notion tools."""
    
    @pytest.mark.asyncio
    async def test_get_timeline(self):
        """Test getting timeline items."""
        from src.tools.notion import get_timeline
        from src.services.organization import _org_cache
        from src.models.organization import OrganizationConfig, DataSourceMapping
        
        # Set up mock org config with timeline database
        _org_cache["default"] = OrganizationConfig(
            org_id="default",
            org_name="Test",
            data_sources=DataSourceMapping(marketing_timeline="test-db-id"),
        )
        
        # Mock MCP response
        mock_response = {
            "items": [
                {"Name": "Film teaser video", "Status": "In Progress", "Date": "2026-02-15"},
                {"Name": "Launch campaign", "Status": "Not Started", "Date": "2026-03-01"},
            ],
            "count": 2,
        }
        
        with patch('src.tools.notion.mcp_client') as mock_mcp:
            mock_mcp.call_notion_tool = AsyncMock(return_value=mock_response)
            
            result = await get_timeline.ainvoke({})
        
        assert "Timeline items (2)" in result
        assert "Film teaser video" in result
        assert "In Progress" in result
        
        # Clean up
        _org_cache.clear()
    
    @pytest.mark.asyncio
    async def test_search_notion(self):
        """Test searching Notion database."""
        from src.tools.notion import search_notion
        from src.services.organization import _org_cache
        from src.models.organization import OrganizationConfig, DataSourceMapping
        
        # Set up mock org config
        _org_cache["default"] = OrganizationConfig(
            org_id="default",
            org_name="Test",
            data_sources=DataSourceMapping(marketing_timeline="test-db-id"),
        )
        
        # Mock MCP response
        mock_response = {
            "items": [
                {"Name": "Film teaser video", "Status": "In Progress", "Date": "2026-02-15"},
            ],
            "count": 1,
            "query": "teaser video",
        }
        
        with patch('src.tools.notion.mcp_client') as mock_mcp:
            mock_mcp.call_notion_tool = AsyncMock(return_value=mock_response)
            
            result = await search_notion.ainvoke({
                "query": "teaser video",
                "database_type": "timeline",
            })
        
        assert "teaser video" in result.lower()
        assert "Film teaser video" in result
        
        # Clean up
        _org_cache.clear()
    
    @pytest.mark.asyncio
    async def test_search_notion_no_results(self):
        """Test searching Notion with no results."""
        from src.tools.notion import search_notion
        from src.services.organization import _org_cache
        from src.models.organization import OrganizationConfig, DataSourceMapping
        
        # Set up mock org config
        _org_cache["default"] = OrganizationConfig(
            org_id="default",
            org_name="Test",
            data_sources=DataSourceMapping(marketing_timeline="test-db-id"),
        )
        
        # Mock MCP response with no results
        mock_response = {
            "items": [],
            "count": 0,
            "query": "nonexistent item",
        }
        
        with patch('src.tools.notion.mcp_client') as mock_mcp:
            mock_mcp.call_notion_tool = AsyncMock(return_value=mock_response)
            
            result = await search_notion.ainvoke({
                "query": "nonexistent item",
                "database_type": "timeline",
            })
        
        assert "No results found" in result
        
        # Clean up
        _org_cache.clear()


# =============================================================================
# INTEGRATION TESTS (Mock Full Workflow)
# =============================================================================

class TestPhase1Integration:
    """Integration tests for Phase 1 components."""
    
    def test_org_config_to_task_plan_flow(self):
        """Test that org config can be used to create task plans."""
        from src.models.organization import OrganizationConfig, SlackChannelMapping
        from src.models.task_plan import TaskPlan, Task
        
        # Create org config
        org_config = OrganizationConfig(
            org_id="test",
            org_name="Test Org",
            slack_channels=SlackChannelMapping(
                partnerships="#test-partnerships",
                marketing="#test-marketing",
            ),
        )
        
        # Resolve channel from config
        channel = org_config.slack_channels.resolve("partnerships channel")
        
        # Use in task
        task = Task(
            id="t1",
            agent="events",
            action="send_team_message",
            parameters={"channel": channel, "message": "Test message"},
            description="Send message to partnerships",
        )
        
        assert task.parameters["channel"] == "#test-partnerships"
    
    def test_workflow_decomposition_example(self):
        """Test the workflow decomposition from the example prompts."""
        from src.models.task_plan import TaskPlan, Task, ExtractedEntity
        
        # Example: New sponsor workflow
        # "Just finished a meeting with John Grey, john@gmail.com, Recruiter at Google 
        #  who agreed to sponsor us for $1.5k..."
        
        entities = [
            ExtractedEntity(entity_type="contact_name", value="John Grey"),
            ExtractedEntity(entity_type="email", value="john@gmail.com"),
            ExtractedEntity(entity_type="company", value="Google"),
            ExtractedEntity(entity_type="position", value="Recruiter"),
            ExtractedEntity(entity_type="amount", value=1500.0),
        ]
        
        tasks = [
            Task(
                id="task_1",
                agent="partnerships",
                action="add_partnership",
                parameters={
                    "sheet_name": "Boothing Companies",
                    "company": "Google",
                    "contact_name": "John Grey",
                    "contact_email": "john@gmail.com",
                    "position": "Recruiter",
                    "role": "Booth Sponsor",
                    "status": "Confirmed",
                },
                description="Log Google sponsorship in boothing partnerships compendium",
            ),
            Task(
                id="task_2",
                agent="events",
                action="send_team_message",
                parameters={
                    "channel": "#partnerships",
                    "message": "New sponsorship confirmed: Google ($1,500)",
                },
                description="Notify partnerships channel",
                depends_on=["task_1"],
            ),
            Task(
                id="task_3",
                agent="events",
                action="send_team_message",
                parameters={
                    "channel": "#marketing",
                    "message": "Please email john@gmail.com for marketing assets",
                },
                description="Notify marketing channel",
                depends_on=["task_1"],
            ),
            Task(
                id="task_4",
                agent="finance",
                action="draft_mou",
                parameters={
                    "sponsor_name": "Google",
                    "tier": "Booth Sponsor",
                    "amount": 1500.0,
                },
                description="Draft MOU for Google",
                depends_on=["task_1"],
                requires_approval=True,
            ),
        ]
        
        plan = TaskPlan(
            plan_id="plan_sponsor_1",
            request_id="req_1",
            request_type="workflow",
            tasks=tasks,
            extracted_entities=entities,
            execution_strategy="mixed",
            target_agents=["partnerships", "events", "finance"],
        )
        
        # Verify plan structure
        assert len(plan.tasks) == 4
        assert len(plan.extracted_entities) == 5
        assert plan.execution_strategy == "mixed"
        
        # Verify dependencies
        ready_initial = plan.get_ready_tasks(set())
        assert len(ready_initial) == 1
        assert ready_initial[0].id == "task_1"
        
        # After task_1 completes, 3 tasks should be ready
        ready_after = plan.get_ready_tasks({"task_1"})
        assert len(ready_after) == 3
        
        # Verify approval required flag
        mou_task = plan.get_task_by_id("task_4")
        assert mou_task.requires_approval is True


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
