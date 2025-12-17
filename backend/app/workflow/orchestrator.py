"""
Workflow Orchestrator - Multi-stage analysis execution engine.
Manages the end-to-end flow from QueryIntent to final report.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.query_intent import QueryIntent
from app.agents.iqvia_agent import IQVIAInsightsAgent
from app.agents.clinical_trials_agent import ClinicalTrialsAgent
from app.agents.patent_agent import PatentLandscapeAgent
from app.agents.exim_trends_agent import EximTrendsAgent
from app.agents.web_intelligence_agent import WebIntelligenceAgent
from app.agents.strategic_opportunity_agent import StrategicOpportunityAgent


class WorkflowOrchestrator:
    """
    Orchestrates multi-stage workflows based on QueryIntent.
    Manages agent execution, context passing, and result aggregation.
    """
    
    def __init__(self):
        # Initialize all agents
        self.agents = {
            "iqvia": IQVIAInsightsAgent(),
            "clinical_trials": ClinicalTrialsAgent(),
            "patent": PatentLandscapeAgent(),
            "exim": EximTrendsAgent(),
            "web_intelligence": WebIntelligenceAgent(),
            "strategic_opportunity": StrategicOpportunityAgent(),
        }
        
        self.execution_log = []
    
    def execute(self, query_intent: QueryIntent) -> Dict[str, Any]:
        """
        Execute workflow based on QueryIntent.
        
        Args:
            query_intent: Parsed query intent with workflow plan
            
        Returns:
            Aggregated results from all stages
        """
        self.execution_log = []
        start_time = datetime.now()
        
        # Initialize result container
        result = {
            "query_intent": query_intent.to_dict(),
            "agent_outputs": {},
            "execution_log": [],
            "start_time": start_time.isoformat(),
        }
        
        # Execute workflow stages
        workflow_stages = query_intent.workflow_stages
        
        if not workflow_stages:
            # Default to basic analysis
            workflow_stages = ["iqvia", "clinical_trials", "patent"]
        
        # Execute each stage
        for stage in workflow_stages:
            try:
                stage_result = self._execute_stage(
                    stage,
                    query_intent,
                    result["agent_outputs"]
                )
                
                result["agent_outputs"][stage] = stage_result
                
                self._log_stage(stage, "success", stage_result)
                
            except Exception as e:
                error_msg = f"Stage '{stage}' failed: {str(e)}"
                self._log_stage(stage, "error", {"error": error_msg})
                result["agent_outputs"][stage] = {"error": error_msg, "available": False}
        
        # Final synthesis stage
        if "strategic_opportunity" in workflow_stages:
            # Already executed as part of workflow
            strategic_output = result["agent_outputs"].get("strategic_opportunity", {})
        else:
            # Execute strategic synthesis at the end
            try:
                strategic_output = self._synthesize_final_insights(
                    query_intent,
                    result["agent_outputs"]
                )
                result["agent_outputs"]["strategic_opportunity"] = strategic_output
                self._log_stage("strategic_opportunity", "success", strategic_output)
            except Exception as e:
                strategic_output = {"error": str(e)}
                self._log_stage("strategic_opportunity", "error", strategic_output)
        
        # Add execution metadata
        end_time = datetime.now()
        result["end_time"] = end_time.isoformat()
        result["execution_time_seconds"] = (end_time - start_time).total_seconds()
        result["execution_log"] = self.execution_log
        result["success"] = all(
            output.get("available", False) != False 
            for output in result["agent_outputs"].values()
            if "error" not in output
        )
        
        # Extract summary
        result["summary"] = self._build_summary(result, strategic_output)
        
        return result
    
    def _execute_stage(
        self,
        stage: str,
        query_intent: QueryIntent,
        previous_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single workflow stage.
        
        Args:
            stage: Stage name (agent identifier)
            query_intent: Original query intent
            previous_outputs: Results from previous stages
            
        Returns:
            Stage execution result
        """
        agent = self.agents.get(stage)
        
        if not agent:
            return {"error": f"Unknown stage: {stage}", "available": False}
        
        # Build agent query from QueryIntent
        agent_query = self._build_agent_query(stage, query_intent, previous_outputs)
        
        # Execute agent
        return agent.run(agent_query)
    
    def _build_agent_query(
        self,
        stage: str,
        query_intent: QueryIntent,
        previous_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build agent-specific query from QueryIntent.
        Each agent may need different input formats.
        """
        
        base_query = {
            "molecule": query_intent.primary_entity,
            "disease": query_intent.disease_area,
            "region": query_intent.geography,
            "indication": query_intent.disease_area,  # alias for disease
        }
        
        # Stage-specific customization
        if stage == "strategic_opportunity":
            # Strategic agent needs all previous outputs
            base_query.update({
                "intent_type": query_intent.intent_type,
                "agent_outputs": previous_outputs,
                "strategic_question": query_intent.strategic_question
            })
        
        elif stage == "web_intelligence":
            # Web intelligence needs the strategic question
            if query_intent.strategic_question:
                base_query["query"] = query_intent.strategic_question
            else:
                # Build query from entities
                parts = []
                if query_intent.primary_entity:
                    parts.append(query_intent.primary_entity)
                if query_intent.disease_area:
                    parts.append(query_intent.disease_area)
                if query_intent.geography:
                    parts.append(f"in {query_intent.geography}")
                base_query["query"] = " ".join(parts)
        
        elif stage == "clinical_trials":
            # Clinical trials can search by molecule or disease
            if not query_intent.primary_entity and query_intent.disease_area:
                base_query["condition"] = query_intent.disease_area
        
        # Add context from QueryIntent
        if query_intent.context:
            base_query.update(query_intent.context)
        
        return base_query
    
    def _synthesize_final_insights(
        self,
        query_intent: QueryIntent,
        agent_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Final strategic synthesis if not already done.
        """
        strategic_agent = self.agents["strategic_opportunity"]
        
        synthesis_query = {
            "intent_type": query_intent.intent_type,
            "molecule": query_intent.primary_entity,
            "disease_area": query_intent.disease_area,
            "geography": query_intent.geography,
            "agent_outputs": agent_outputs,
            "strategic_question": query_intent.strategic_question
        }
        
        return strategic_agent.run(synthesis_query)
    
    def _log_stage(self, stage: str, status: str, result: Any):
        """Log stage execution."""
        self.execution_log.append({
            "stage": stage,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "has_data": result.get("available", False) if isinstance(result, dict) else False
        })
    
    def _build_summary(
        self,
        result: Dict[str, Any],
        strategic_output: Dict[str, Any]
    ) -> str:
        """Build executive summary of the analysis."""
        
        query_intent = result.get("query_intent", {})
        intent_type = query_intent.get("intent_type", "analysis")
        
        # Get innovation story from strategic synthesis
        innovation_story = strategic_output.get("innovation_story", "")
        
        if innovation_story:
            return innovation_story
        
        # Fallback summary
        molecule = query_intent.get("primary_entity")
        disease = query_intent.get("disease_area")
        geography = query_intent.get("geography")
        
        summary_parts = []
        
        if intent_type == "repurposing":
            summary_parts.append(f"Repurposing analysis for {molecule or 'candidate molecule'}")
            if disease:
                summary_parts.append(f"in {disease}")
        elif intent_type == "market_discovery":
            summary_parts.append(f"Market opportunity analysis")
            if disease:
                summary_parts.append(f"for {disease}")
            if geography:
                summary_parts.append(f"in {geography}")
        else:
            summary_parts.append(f"Strategic analysis")
            if molecule:
                summary_parts.append(f"of {molecule}")
            if disease:
                summary_parts.append(f"for {disease}")
        
        summary = " ".join(summary_parts)
        summary += f". Analyzed {len(result.get('agent_outputs', {}))} data sources."
        
        return summary


# Quick self-test
if __name__ == "__main__":
    from app.models.query_intent import QueryIntent
    
    orchestrator = WorkflowOrchestrator()
    
    # Test structured input
    intent1 = QueryIntent.from_structured_input(
        molecule="Metformin",
        disease="Diabetes",
        region="India"
    )
    
    print("=" * 60)
    print("Test 1: Structured Input (Metformin)")
    print("=" * 60)
    result1 = orchestrator.execute(intent1)
    print(f"Success: {result1.get('success')}")
    print(f"Stages executed: {list(result1.get('agent_outputs', {}).keys())}")
    print(f"Execution time: {result1.get('execution_time_seconds')}s")
    print(f"\nSummary:\n{result1.get('summary')}\n")
    
    # Test repurposing workflow
    intent2 = QueryIntent(
        intent_type="repurposing",
        primary_entity="Metformin",
        disease_area="NAFLD",
        geography="US",
        strategic_question="Is metformin suitable for NAFLD repurposing?",
        workflow_stages=["clinical_trials", "patent", "iqvia", "strategic_opportunity"]
    )
    
    print("=" * 60)
    print("Test 2: Repurposing Workflow")
    print("=" * 60)
    result2 = orchestrator.execute(intent2)
    print(f"Success: {result2.get('success')}")
    print(f"Stages executed: {list(result2.get('agent_outputs', {}).keys())}")
    print(f"Execution time: {result2.get('execution_time_seconds')}s")
    print(f"\nSummary:\n{result2.get('summary')}\n")
