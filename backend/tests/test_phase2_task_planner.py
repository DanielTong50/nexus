"""
Phase 2 Task Planner Tests

Comprehensive tests for:
1. Task planner LLM response parsing
2. TaskPlan creation from LLM output
3. Organization context injection
4. Prompt building

Run with: pytest tests/test_phase2_task_planner.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json


# =============================================================================
# TASK PLANNER RESPONSE PARSING TESTS
# =============================================================================

class TestTaskPlannerParsing:
    """Tests for parsing LLM responses into task plans."""
    
    def test_parse_valid_json_response(self):
        """Test parsing a valid JSON response."""
        from src.graph.task_planner import _parse_llm_response
        
        valid_response = json.dumps({
            "request_type": "workflow",
            "extracted_entities": [
                {"entity_type": "company", "value": "Google", "confidence": 1.0}
            ],
            "tasks": [
                {
                    "id": "task_1",
                    "agent": "partnerships",
                    "action": "add_partnership",
                    "parameters": {"company": "Google"},
                    "description": "Add Google",
                    "depends_on": [],
                    "requires_approval": False
                }
            ],
            "execution_strategy": "sequential",
            "reasoning": "Simple add"
        })
        
        result = _parse_llm_response(valid_response)
        
        assert result["request_type"] == "workflow"
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["agent"] == "partnerships"
    
    def test_parse_json_with_markdown_code_block(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        from src.graph.task_planner import _parse_llm_response
        
        response = '''```json
{
    "request_type": "question",
    "tasks": [],
    "extracted_entities": [],
    "execution_strategy": "sequential",
    "reasoning": "Test"
}
```'''
        
        result = _parse_llm_response(response)
        
        assert result["request_type"] == "question"
    
    def test_parse_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError."""
        from src.graph.task_planner import _parse_llm_response
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            _parse_llm_response("This is not JSON")
    
    def test_parse_json_with_extra_whitespace(self):
        """Test parsing JSON with extra whitespace."""
        from src.graph.task_planner import _parse_llm_response
        
        response = '''
        
        {
            "request_type": "workflow",
            "tasks": [],
            "extracted_entities": [],
            "execution_strategy": "parallel",
            "reasoning": "Whitespace test"
        }
        
        '''
        
        result = _parse_llm_response(response)
        assert result["execution_strategy"] == "parallel"


# =============================================================================
# TASK PLAN CREATION TESTS
# =============================================================================

class TestTaskPlanCreation:
    """Tests for creating TaskPlan from LLM response."""
    
    def test_create_task_plan_from_workflow_response(self):
        """Test creating a full task plan from workflow response."""
        from src.graph.task_planner import _create_task_plan_from_response
        
        response_data = {
            "request_type": "workflow",
            "extracted_entities": [
                {"entity_type": "company", "value": "Google", "confidence": 1.0},
                {"entity_type": "amount", "value": 1500, "confidence": 0.9},
            ],
            "tasks": [
                {
                    "id": "task_1",
                    "agent": "partnerships",
                    "action": "add_partnership",
                    "parameters": {
                        "sheet_name": "Boothing Companies",
                        "company": "Google",
                    },
                    "description": "Log Google sponsorship",
                    "depends_on": [],
                    "requires_approval": False
                },
                {
                    "id": "task_2",
                    "agent": "events",
                    "action": "send_team_message",
                    "parameters": {
                        "channel": "#partnerships",
                        "message": "New sponsor: Google"
                    },
                    "description": "Notify team",
                    "depends_on": ["task_1"],
                    "requires_approval": False
                }
            ],
            "execution_strategy": "sequential",
            "reasoning": "Log first, then notify"
        }
        
        plan = _create_task_plan_from_response(response_data, "req_123")
        
        assert plan.plan_id == "plan_req_123"
        assert plan.request_type == "workflow"
        assert len(plan.tasks) == 2
        assert len(plan.extracted_entities) == 2
        assert plan.execution_strategy == "sequential"
        
        # Check task dependencies
        assert plan.tasks[0].depends_on == []
        assert plan.tasks[1].depends_on == ["task_1"]
        
        # Check target agents extraction
        assert set(plan.target_agents) == {"partnerships", "events"}
    
    def test_create_task_plan_from_question_response(self):
        """Test creating task plan from question response."""
        from src.graph.task_planner import _create_task_plan_from_response
        
        response_data = {
            "request_type": "question",
            "extracted_entities": [
                {"entity_type": "search_term", "value": "teaser video", "confidence": 0.9},
            ],
            "tasks": [
                {
                    "id": "task_1",
                    "agent": "marketing",
                    "action": "search_notion",
                    "parameters": {
                        "query": "teaser video filming",
                        "database_type": "timeline"
                    },
                    "description": "Search for teaser video date",
                    "depends_on": [],
                    "requires_approval": False
                }
            ],
            "execution_strategy": "sequential",
            "reasoning": "Simple search query"
        }
        
        plan = _create_task_plan_from_response(response_data, "req_456")
        
        assert plan.request_type == "question"
        assert len(plan.tasks) == 1
        assert plan.tasks[0].action == "search_notion"
        assert plan.target_agents == ["marketing"]
    
    def test_create_task_plan_with_approval_required(self):
        """Test creating task plan with approval-required tasks."""
        from src.graph.task_planner import _create_task_plan_from_response
        
        response_data = {
            "request_type": "workflow",
            "extracted_entities": [],
            "tasks": [
                {
                    "id": "task_1",
                    "agent": "finance",
                    "action": "generate_invoice",
                    "parameters": {"company": "Google", "amount": 1500},
                    "description": "Create invoice",
                    "depends_on": [],
                    "requires_approval": True
                }
            ],
            "execution_strategy": "sequential",
            "reasoning": "Invoice needs approval"
        }
        
        plan = _create_task_plan_from_response(response_data, "req_789")
        
        assert plan.tasks[0].requires_approval is True


# =============================================================================
# PROMPT BUILDING TESTS
# =============================================================================

class TestPromptBuilding:
    """Tests for building task planner prompts."""
    
    def test_build_system_prompt_includes_org_context(self):
        """Test that system prompt includes organization context."""
        from src.graph.task_planner import _build_system_prompt
        
        org_context = """Organization: Test Org
Event: TestHack 2026
Sponsorship Goal: $100,000

Available Slack Channels (use EXACT names including #):
  - #test-partnerships (partnerships team)
  - #test-marketing (marketing team)

Available Data Sources (use EXACT names):
  Google Sheets:
    - "Test Sponsors" (boothing/booth sponsors)
"""
        
        prompt = _build_system_prompt(org_context)
        
        assert "Test Org" in prompt
        assert "TestHack" in prompt
        assert "#test-partnerships" in prompt
        assert "Test Sponsors" in prompt
    
    def test_build_system_prompt_extracts_example_values(self):
        """Test that prompt extracts example channel/sheet from context."""
        from src.graph.task_planner import _build_system_prompt
        
        org_context = """Organization: BizTech
Available Slack Channels:
  - #biz-partnerships (partnerships team)
  - #biz-marketing (marketing team)
"""
        
        prompt = _build_system_prompt(org_context)
        
        # Should use extracted channel in examples
        assert "#biz-partnerships" in prompt or "#partnerships" in prompt


# =============================================================================
# TASK PLANNER INTEGRATION TESTS (with mocking)
# =============================================================================

class TestTaskPlannerIntegration:
    """Integration tests for the task planner with mocked LLM."""
    
    @pytest.mark.asyncio
    async def test_plan_tasks_workflow(self):
        """Test full task planning for a workflow request."""
        from src.graph.task_planner import plan_tasks
        from src.models.state import GraphState
        from src.services.organization import _org_cache
        from src.models.organization import OrganizationConfig
        
        # Set up mock org config
        _org_cache["default"] = OrganizationConfig(
            org_id="default",
            org_name="Test Org",
        )
        
        # Mock LLM response
        mock_llm_response = MagicMock()
        mock_llm_response.content = json.dumps({
            "request_type": "workflow",
            "extracted_entities": [
                {"entity_type": "company", "value": "Google", "confidence": 1.0}
            ],
            "tasks": [
                {
                    "id": "task_1",
                    "agent": "partnerships",
                    "action": "add_partnership",
                    "parameters": {"company": "Google"},
                    "description": "Add Google",
                    "depends_on": [],
                    "requires_approval": False
                }
            ],
            "execution_strategy": "sequential",
            "reasoning": "Add sponsor"
        })
        
        with patch('src.graph.task_planner._get_planner_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.ainvoke = AsyncMock(return_value=mock_llm_response)
            mock_get_llm.return_value = mock_llm
            
            state = GraphState(
                user_message="Add Google as a sponsor",
                request_id="test_req",
                org_id="default"
            )
            
            result = await plan_tasks(state)
        
        assert "target_agents" in result
        assert "task_plan" in result
        assert result["target_agents"] == ["partnerships"]
        assert result["task_plan"].request_type == "workflow"
        
        # Clean up
        _org_cache.clear()
    
    @pytest.mark.asyncio
    async def test_plan_tasks_question(self):
        """Test task planning for a question request."""
        from src.graph.task_planner import plan_tasks
        from src.models.state import GraphState
        from src.services.organization import _org_cache
        from src.models.organization import OrganizationConfig
        
        # Set up mock org config
        _org_cache["default"] = OrganizationConfig(
            org_id="default",
            org_name="Test Org",
        )
        
        # Mock LLM response for question
        mock_llm_response = MagicMock()
        mock_llm_response.content = json.dumps({
            "request_type": "question",
            "extracted_entities": [
                {"entity_type": "search_term", "value": "filming date", "confidence": 0.9}
            ],
            "tasks": [
                {
                    "id": "task_1",
                    "agent": "marketing",
                    "action": "search_notion",
                    "parameters": {"query": "filming date"},
                    "description": "Search timeline",
                    "depends_on": [],
                    "requires_approval": False
                }
            ],
            "execution_strategy": "sequential",
            "reasoning": "Simple search"
        })
        
        with patch('src.graph.task_planner._get_planner_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.ainvoke = AsyncMock(return_value=mock_llm_response)
            mock_get_llm.return_value = mock_llm
            
            state = GraphState(
                user_message="When is the filming date?",
                request_id="test_req",
                org_id="default"
            )
            
            result = await plan_tasks(state)
        
        assert result["task_plan"].request_type == "question"
        assert result["target_agents"] == ["marketing"]
        
        # Clean up
        _org_cache.clear()
    
    @pytest.mark.asyncio
    async def test_plan_tasks_empty_message(self):
        """Test task planning with empty message."""
        from src.graph.task_planner import plan_tasks
        from src.models.state import GraphState
        
        state = GraphState(
            user_message="",
            request_id="test_req",
        )
        
        result = await plan_tasks(state)
        
        assert result["target_agents"] == []
        assert result["task_plan"] is None
    
    @pytest.mark.asyncio
    async def test_plan_tasks_llm_error_handling(self):
        """Test error handling when LLM fails."""
        from src.graph.task_planner import plan_tasks
        from src.models.state import GraphState
        from src.services.organization import _org_cache
        from src.models.organization import OrganizationConfig
        
        # Set up mock org config
        _org_cache["default"] = OrganizationConfig(
            org_id="default",
            org_name="Test Org",
        )
        
        with patch('src.graph.task_planner._get_planner_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM API error"))
            mock_get_llm.return_value = mock_llm
            
            state = GraphState(
                user_message="Add a sponsor",
                request_id="test_req",
                org_id="default"
            )
            
            result = await plan_tasks(state)
        
        assert result["target_agents"] == []
        assert result["task_plan"] is None
        assert "errors" in result
        
        # Clean up
        _org_cache.clear()


# =============================================================================
# STANDALONE FUNCTION TESTS
# =============================================================================

class TestStandaloneFunctions:
    """Tests for standalone planning functions."""
    
    @pytest.mark.asyncio
    async def test_plan_tasks_standalone(self):
        """Test standalone task planning."""
        from src.graph.task_planner import plan_tasks_standalone
        from src.services.organization import _org_cache
        from src.models.organization import OrganizationConfig
        
        # Set up mock org config
        _org_cache["default"] = OrganizationConfig(
            org_id="default",
            org_name="Test Org",
        )
        
        mock_llm_response = MagicMock()
        mock_llm_response.content = json.dumps({
            "request_type": "workflow",
            "extracted_entities": [],
            "tasks": [
                {
                    "id": "task_1",
                    "agent": "events",
                    "action": "send_team_message",
                    "parameters": {"channel": "#general"},
                    "description": "Send message",
                    "depends_on": [],
                    "requires_approval": False
                }
            ],
            "execution_strategy": "sequential",
            "reasoning": "Simple message"
        })
        
        with patch('src.graph.task_planner._get_planner_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.ainvoke = AsyncMock(return_value=mock_llm_response)
            mock_get_llm.return_value = mock_llm
            
            plan = await plan_tasks_standalone("Send a message to general")
        
        assert plan.request_type == "workflow"
        assert len(plan.tasks) == 1
        
        # Clean up
        _org_cache.clear()
    
    @pytest.mark.asyncio
    async def test_classify_to_agents(self):
        """Test backward-compatible classification function."""
        from src.graph.task_planner import classify_to_agents
        from src.services.organization import _org_cache
        from src.models.organization import OrganizationConfig
        
        # Set up mock org config
        _org_cache["default"] = OrganizationConfig(
            org_id="default",
            org_name="Test Org",
        )
        
        mock_llm_response = MagicMock()
        mock_llm_response.content = json.dumps({
            "request_type": "workflow",
            "extracted_entities": [],
            "tasks": [
                {"id": "t1", "agent": "partnerships", "action": "search", "parameters": {}, "description": "Search", "depends_on": [], "requires_approval": False},
                {"id": "t2", "agent": "events", "action": "notify", "parameters": {}, "description": "Notify", "depends_on": [], "requires_approval": False},
            ],
            "execution_strategy": "parallel",
            "reasoning": "Multi-agent"
        })
        
        with patch('src.graph.task_planner._get_planner_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.ainvoke = AsyncMock(return_value=mock_llm_response)
            mock_get_llm.return_value = mock_llm
            
            agents = await classify_to_agents("Search sponsors and notify team")
        
        assert set(agents) == {"partnerships", "events"}
        
        # Clean up
        _org_cache.clear()


# =============================================================================
# COMPLEX WORKFLOW TESTS
# =============================================================================

class TestComplexWorkflows:
    """Tests for complex multi-step workflow scenarios."""
    
    def test_sponsor_onboarding_workflow_structure(self):
        """Test the structure of a sponsor onboarding workflow."""
        from src.graph.task_planner import _create_task_plan_from_response
        
        # Simulated LLM response for:
        # "Add Google as sponsor, notify partnerships, notify marketing, create invoice"
        response_data = {
            "request_type": "workflow",
            "extracted_entities": [
                {"entity_type": "company", "value": "Google", "confidence": 1.0},
                {"entity_type": "amount", "value": 5000, "confidence": 0.9},
            ],
            "tasks": [
                {
                    "id": "task_1",
                    "agent": "partnerships",
                    "action": "add_partnership",
                    "parameters": {
                        "sheet_name": "Boothing Companies",
                        "company": "Google",
                        "status": "Confirmed"
                    },
                    "description": "Log Google in compendium",
                    "depends_on": [],
                    "requires_approval": False
                },
                {
                    "id": "task_2",
                    "agent": "events",
                    "action": "send_team_message",
                    "parameters": {
                        "channel": "#partnerships",
                        "message": "New sponsor: Google confirmed"
                    },
                    "description": "Notify partnerships channel",
                    "depends_on": ["task_1"],
                    "requires_approval": False
                },
                {
                    "id": "task_3",
                    "agent": "events",
                    "action": "send_team_message",
                    "parameters": {
                        "channel": "#marketing",
                        "message": "New sponsor Google - please request assets"
                    },
                    "description": "Notify marketing channel",
                    "depends_on": ["task_1"],
                    "requires_approval": False
                },
                {
                    "id": "task_4",
                    "agent": "finance",
                    "action": "generate_invoice",
                    "parameters": {
                        "company": "Google",
                        "amount": 5000
                    },
                    "description": "Create invoice for Google",
                    "depends_on": ["task_1"],
                    "requires_approval": True
                }
            ],
            "execution_strategy": "mixed",
            "reasoning": "Log first, then parallel notifications and invoice"
        }
        
        plan = _create_task_plan_from_response(response_data, "sponsor_req")
        
        # Verify structure
        assert len(plan.tasks) == 4
        assert plan.execution_strategy == "mixed"
        
        # Verify dependencies - task_1 has no deps, others depend on task_1
        assert plan.tasks[0].depends_on == []
        assert plan.tasks[1].depends_on == ["task_1"]
        assert plan.tasks[2].depends_on == ["task_1"]
        assert plan.tasks[3].depends_on == ["task_1"]
        
        # Verify ready tasks
        ready_initial = plan.get_ready_tasks(set())
        assert len(ready_initial) == 1
        assert ready_initial[0].id == "task_1"
        
        # After task_1, 3 tasks should be ready (parallel)
        ready_after = plan.get_ready_tasks({"task_1"})
        assert len(ready_after) == 3
        
        # Verify approval flag
        invoice_task = plan.get_task_by_id("task_4")
        assert invoice_task.requires_approval is True
    
    def test_sponsor_withdrawal_workflow_structure(self):
        """Test structure of sponsor withdrawal workflow."""
        from src.graph.task_planner import _create_task_plan_from_response
        
        # Simulated LLM response for:
        # "GitHub dropped out of Blueprint, update compendium and notify team"
        response_data = {
            "request_type": "status_update",
            "extracted_entities": [
                {"entity_type": "company", "value": "GitHub", "confidence": 1.0},
                {"entity_type": "event", "value": "Blueprint", "confidence": 0.9},
                {"entity_type": "status", "value": "Withdrawn", "confidence": 1.0},
            ],
            "tasks": [
                {
                    "id": "task_1",
                    "agent": "partnerships",
                    "action": "log_partnership_status",
                    "parameters": {
                        "sheet_name": "Boothing Companies",
                        "company": "GitHub",
                        "new_status": "Withdrawn",
                        "notes": "Internal change, no longer sponsoring Blueprint"
                    },
                    "description": "Update GitHub status to withdrawn",
                    "depends_on": [],
                    "requires_approval": False
                },
                {
                    "id": "task_2",
                    "agent": "events",
                    "action": "send_team_message",
                    "parameters": {
                        "channel": "#partnerships",
                        "message": "Update: GitHub has withdrawn from Blueprint sponsorship due to internal changes."
                    },
                    "description": "Notify partnerships channel",
                    "depends_on": ["task_1"],
                    "requires_approval": False
                }
            ],
            "execution_strategy": "sequential",
            "reasoning": "Update status first, then notify team"
        }
        
        plan = _create_task_plan_from_response(response_data, "withdrawal_req")
        
        assert plan.request_type == "status_update"
        assert len(plan.tasks) == 2
        assert plan.tasks[0].action == "log_partnership_status"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
