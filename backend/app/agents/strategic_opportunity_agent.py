"""
Strategic Opportunity Agent - Synthesizes insights from all worker agents.
Identifies unmet needs, repurposing opportunities, and innovation narratives.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .worker_base import WorkerBase


class StrategicOpportunityAgent(WorkerBase):
    """
    Strategic synthesis agent that identifies opportunities based on multi-agent analysis.
    
    Capabilities:
    - Identify unmet medical needs
    - Suggest repurposing opportunities
    - Evaluate market attractiveness
    - Generate innovation narratives
    - Assess feasibility and risks
    """
    
    def run(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize strategic opportunities from aggregated agent outputs.
        
        query format:
        {
            "intent_type": "repurposing" | "market_discovery" | ...,
            "molecule": "metformin" (optional),
            "disease_area": "NAFLD" (optional),
            "geography": "India" (optional),
            "agent_outputs": {
                "iqvia": {...},
                "clinical_trials": {...},
                "patent": {...},
                "exim": {...}
            }
        }
        """
        intent_type = query.get("intent_type", "strategic_question")
        molecule = query.get("molecule")
        disease_area = query.get("disease_area")
        geography = query.get("geography")
        agent_outputs = query.get("agent_outputs", {})
        
        # Route to appropriate synthesis method
        if intent_type == "repurposing":
            return self._synthesize_repurposing_opportunity(
                molecule, disease_area, geography, agent_outputs
            )
        elif intent_type == "market_discovery":
            return self._synthesize_market_opportunity(
                disease_area, geography, agent_outputs
            )
        elif intent_type == "molecule_analysis":
            return self._synthesize_molecule_insights(
                molecule, disease_area, geography, agent_outputs
            )
        else:
            return self._synthesize_general_insights(
                query, agent_outputs
            )
    
    def _synthesize_repurposing_opportunity(
        self,
        molecule: Optional[str],
        disease_area: Optional[str],
        geography: Optional[str],
        agent_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize repurposing opportunity analysis.
        Critical for the hackathon's repurposing workflow.
        """
        
        # Extract insights from each agent
        clinical_data = agent_outputs.get("clinical_trials", {})
        patent_data = agent_outputs.get("patent", {})
        market_data = agent_outputs.get("iqvia", {})
        
        # Analyze trial activity for new indication
        trial_activity = self._analyze_trial_activity(clinical_data, disease_area)
        
        # Analyze patent freedom to operate
        fto_assessment = self._analyze_patent_fto(patent_data, disease_area)
        
        # Analyze market attractiveness
        market_potential = self._analyze_market_potential(market_data, disease_area, geography)
        
        # Generate innovation narrative
        innovation_story = self._generate_repurposing_narrative(
            molecule, disease_area, trial_activity, fto_assessment, market_potential
        )
        
        # Calculate feasibility score
        feasibility_score = self._calculate_feasibility_score(
            trial_activity, fto_assessment, market_potential
        )
        
        # Identify unmet needs
        unmet_needs = self._identify_unmet_needs(
            disease_area, market_data, clinical_data
        )
        
        return {
            "opportunity_type": "repurposing",
            "molecule": molecule,
            "proposed_indication": disease_area,
            "geography": geography,
            
            "unmet_needs": unmet_needs,
            
            "trial_activity": trial_activity,
            "patent_assessment": fto_assessment,
            "market_potential": market_potential,
            
            "innovation_story": innovation_story,
            "feasibility_score": feasibility_score,
            
            "key_insights": self._extract_key_insights(
                trial_activity, fto_assessment, market_potential
            ),
            
            "recommendations": self._generate_recommendations(
                molecule, disease_area, feasibility_score, fto_assessment
            ),
            
            "as_of_date": datetime.today().date().isoformat()
        }
    
    def _synthesize_market_opportunity(
        self,
        disease_area: Optional[str],
        geography: Optional[str],
        agent_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize market discovery opportunities.
        Answers: "Which diseases show low competition but high need?"
        """
        
        market_data = agent_outputs.get("iqvia", {})
        clinical_data = agent_outputs.get("clinical_trials", {})
        exim_data = agent_outputs.get("exim", {})
        
        # Identify low competition areas
        competition_analysis = self._analyze_competition(market_data, clinical_data)
        
        # Identify unmet needs
        unmet_needs = self._identify_unmet_needs(disease_area, market_data, clinical_data)
        
        # Market attractiveness
        market_attractiveness = self._assess_market_attractiveness(
            market_data, exim_data, geography
        )
        
        innovation_story = self._generate_market_discovery_narrative(
            disease_area, geography, competition_analysis, unmet_needs, market_attractiveness
        )
        
        return {
            "opportunity_type": "market_discovery",
            "disease_area": disease_area,
            "geography": geography,
            
            "competition_analysis": competition_analysis,
            "unmet_needs": unmet_needs,
            "market_attractiveness": market_attractiveness,
            
            "innovation_story": innovation_story,
            
            "recommended_molecules": self._suggest_molecules(disease_area, market_data),
            
            "key_insights": [
                f"Competition level: {competition_analysis.get('level', 'unknown')}",
                f"Market growth: {market_attractiveness.get('growth_rate', 'N/A')}",
                f"Unmet needs identified: {len(unmet_needs)}"
            ],
            
            "as_of_date": datetime.today().date().isoformat()
        }
    
    def _synthesize_molecule_insights(
        self,
        molecule: Optional[str],
        disease_area: Optional[str],
        geography: Optional[str],
        agent_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize strategic insights for molecule analysis.
        """
        
        market_data = agent_outputs.get("iqvia", {})
        patent_data = agent_outputs.get("patent", {})
        clinical_data = agent_outputs.get("clinical_trials", {})
        exim_data = agent_outputs.get("exim", {})
        
        # Market position
        market_position = self._assess_market_position(market_data, molecule)
        
        # IP landscape
        ip_landscape = self._summarize_ip_landscape(patent_data)
        
        # Clinical landscape
        clinical_landscape = self._summarize_clinical_landscape(clinical_data)
        
        # Trade dynamics
        trade_dynamics = self._summarize_trade_dynamics(exim_data)
        
        # Strategic insights
        strategic_insights = self._generate_strategic_insights(
            molecule, disease_area, market_position, ip_landscape, clinical_landscape
        )
        
        return {
            "opportunity_type": "molecule_analysis",
            "molecule": molecule,
            "disease_area": disease_area,
            "geography": geography,
            
            "market_position": market_position,
            "ip_landscape": ip_landscape,
            "clinical_landscape": clinical_landscape,
            "trade_dynamics": trade_dynamics,
            
            "strategic_insights": strategic_insights,
            
            "innovation_story": self._generate_molecule_narrative(
                molecule, disease_area, strategic_insights
            ),
            
            "as_of_date": datetime.today().date().isoformat()
        }
    
    def _synthesize_general_insights(
        self,
        query: Dict[str, Any],
        agent_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        General synthesis for strategic questions that don't fit other categories.
        """
        
        strategic_question = query.get("strategic_question", "General analysis")
        
        insights = []
        for agent_name, output in agent_outputs.items():
            if output and isinstance(output, dict):
                summary = output.get("summary") or output.get("overview")
                if summary:
                    insights.append(f"[{agent_name.upper()}] {summary}")
        
        return {
            "opportunity_type": "strategic_question",
            "question": strategic_question,
            "insights": insights,
            "innovation_story": self._generate_general_narrative(strategic_question, insights),
            "as_of_date": datetime.today().date().isoformat()
        }
    
    # ==================== ANALYSIS HELPERS ====================
    
    def _analyze_trial_activity(
        self, clinical_data: Dict[str, Any], disease_area: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze clinical trial activity for repurposing indication."""
        
        trials = clinical_data.get("trials", [])
        total_trials = len(trials)
        
        # Count by phase
        phase_distribution = {}
        for trial in trials:
            phase = trial.get("phase", "Unknown")
            phase_distribution[phase] = phase_distribution.get(phase, 0) + 1
        
        # Activity level
        if total_trials == 0:
            activity_level = "none"
        elif total_trials < 5:
            activity_level = "low"
        elif total_trials < 20:
            activity_level = "moderate"
        else:
            activity_level = "high"
        
        return {
            "total_trials": total_trials,
            "phase_distribution": phase_distribution,
            "activity_level": activity_level,
            "interpretation": f"{activity_level.capitalize()} clinical interest in this indication"
        }
    
    def _analyze_patent_fto(
        self, patent_data: Dict[str, Any], disease_area: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze patent freedom-to-operate."""
        
        overview = patent_data.get("overview", {})
        active_patents = overview.get("active_count", 0)
        expired_patents = overview.get("expired_count", 0)
        
        if active_patents == 0:
            fto_level = "clear"
            fto_risk = "low"
        elif active_patents < 5:
            fto_level = "moderate"
            fto_risk = "medium"
        else:
            fto_level = "constrained"
            fto_risk = "high"
        
        return {
            "active_patents": active_patents,
            "expired_patents": expired_patents,
            "fto_level": fto_level,
            "fto_risk": fto_risk,
            "interpretation": f"Freedom-to-operate: {fto_level} ({active_patents} active patents)"
        }
    
    def _analyze_market_potential(
        self, market_data: Dict[str, Any], disease_area: Optional[str], geography: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze market attractiveness and potential."""
        
        overview = market_data.get("overview", {})
        market_size = overview.get("total_market_size_usd", 0)
        growth_rate = overview.get("yoy_growth_pct", 0)
        
        if market_size > 1000000000:  # > $1B
            size_category = "large"
        elif market_size > 100000000:  # > $100M
            size_category = "medium"
        else:
            size_category = "small"
        
        if growth_rate > 10:
            growth_category = "high"
        elif growth_rate > 5:
            growth_category = "moderate"
        else:
            growth_category = "low"
        
        return {
            "market_size_usd": market_size,
            "market_size_category": size_category,
            "growth_rate_pct": growth_rate,
            "growth_category": growth_category,
            "attractiveness": "high" if size_category != "small" and growth_category != "low" else "moderate",
            "interpretation": f"{size_category.capitalize()} market with {growth_category} growth"
        }
    
    def _analyze_competition(
        self, market_data: Dict[str, Any], clinical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze competitive landscape."""
        
        top_products = market_data.get("top_products", [])
        num_competitors = len(top_products)
        
        if num_competitors == 0:
            level = "none"
        elif num_competitors < 3:
            level = "low"
        elif num_competitors < 10:
            level = "moderate"
        else:
            level = "high"
        
        return {
            "number_of_competitors": num_competitors,
            "competition_level": level,
            "top_players": [p.get("product_name") for p in top_products[:3]],
            "interpretation": f"{level.capitalize()} competition with {num_competitors} key players"
        }
    
    def _identify_unmet_needs(
        self, disease_area: Optional[str], market_data: Dict[str, Any], clinical_data: Dict[str, Any]
    ) -> List[str]:
        """Identify unmet medical needs."""
        
        # This is where you'd use more sophisticated analysis
        # For now, providing common pharma unmet needs
        
        unmet_needs = []
        
        # Low trial activity = potential unmet need
        trial_count = len(clinical_data.get("trials", []))
        if trial_count < 10:
            unmet_needs.append(f"Limited therapeutic development activity in {disease_area or 'this area'}")
        
        # Check market data for gaps
        overview = market_data.get("overview", {})
        if overview.get("yoy_growth_pct", 0) > 15:
            unmet_needs.append("High market growth indicates significant unmet patient needs")
        
        # Generic unmet needs (would be more specific with real data)
        if disease_area:
            disease_specific = {
                "NAFLD": [
                    "No FDA-approved therapies for NAFLD/NASH",
                    "Growing patient population due to obesity epidemic",
                    "Need for non-invasive treatment options"
                ],
                "diabetes": [
                    "Need for therapies addressing cardiovascular outcomes",
                    "Better tolerability profiles required"
                ],
                "oncology": [
                    "Need for targeted therapies with fewer side effects",
                    "Resistance to current standard of care"
                ]
            }
            
            disease_lower = disease_area.lower()
            for key, needs in disease_specific.items():
                if key.lower() in disease_lower:
                    unmet_needs.extend(needs)
                    break
        
        return unmet_needs if unmet_needs else [
            "Efficacy gaps in current treatment options",
            "Safety and tolerability concerns with existing therapies",
            "Patient convenience and adherence challenges"
        ]
    
    def _assess_market_attractiveness(
        self, market_data: Dict[str, Any], exim_data: Dict[str, Any], geography: Optional[str]
    ) -> Dict[str, Any]:
        """Assess overall market attractiveness."""
        
        overview = market_data.get("overview", {})
        
        return {
            "market_size": overview.get("total_market_size_usd", 0),
            "growth_rate": overview.get("yoy_growth_pct", 0),
            "rating": "attractive" if overview.get("yoy_growth_pct", 0) > 10 else "moderate",
            "factors": [
                f"Market size: ${overview.get('total_market_size_usd', 0):,.0f}",
                f"Growth rate: {overview.get('yoy_growth_pct', 0)}%",
                f"Region: {geography or 'Global'}"
            ]
        }
    
    def _calculate_feasibility_score(
        self, trial_activity: Dict, fto_assessment: Dict, market_potential: Dict
    ) -> float:
        """Calculate overall repurposing feasibility score (0.0-1.0)."""
        
        score = 0.0
        
        # Trial activity contribution (0.3 weight)
        activity_scores = {"none": 0.2, "low": 0.5, "moderate": 0.8, "high": 1.0}
        score += activity_scores.get(trial_activity.get("activity_level", "none"), 0.5) * 0.3
        
        # FTO contribution (0.4 weight)
        fto_scores = {"clear": 1.0, "moderate": 0.6, "constrained": 0.3}
        score += fto_scores.get(fto_assessment.get("fto_level", "moderate"), 0.6) * 0.4
        
        # Market potential contribution (0.3 weight)
        attractiveness = market_potential.get("attractiveness", "moderate")
        market_scores = {"high": 1.0, "moderate": 0.6, "low": 0.3}
        score += market_scores.get(attractiveness, 0.6) * 0.3
        
        return round(score, 2)
    
    # ==================== NARRATIVE GENERATION ====================
    
    def _generate_repurposing_narrative(
        self, molecule: Optional[str], disease_area: Optional[str],
        trial_activity: Dict, fto_assessment: Dict, market_potential: Dict
    ) -> str:
        """Generate compelling repurposing innovation story."""
        
        narrative = f"**Drug Repurposing Opportunity: {molecule or 'Candidate Molecule'} for {disease_area or 'New Indication'}**\n\n"
        
        # Clinical rationale
        activity_level = trial_activity.get("activity_level", "unknown")
        if activity_level in ["moderate", "high"]:
            narrative += f"Clinical interest is {activity_level}, with {trial_activity.get('total_trials', 0)} relevant trials indicating therapeutic potential. "
        else:
            narrative += f"Limited clinical activity presents a first-mover opportunity in this indication. "
        
        # IP landscape
        fto_level = fto_assessment.get("fto_level", "unknown")
        if fto_level == "clear":
            narrative += "The IP landscape shows clear freedom-to-operate with minimal patent constraints. "
        elif fto_level == "moderate":
            narrative += "Patent landscape is navigable with strategic IP planning. "
        else:
            narrative += "Patent constraints exist but may be addressable through formulation or indication-specific claims. "
        
        # Market opportunity
        market_attr = market_potential.get("attractiveness", "moderate")
        size_cat = market_potential.get("market_size_category", "medium")
        growth_cat = market_potential.get("growth_category", "moderate")
        
        narrative += f"The market opportunity is {market_attr}, representing a {size_cat}-sized market with {growth_cat} growth potential. "
        
        # Conclusion
        narrative += f"\n\n**Innovation Story**: {molecule or 'This molecule'} represents a promising repurposing candidate for {disease_area or 'this indication'}, "
        narrative += "leveraging established safety profiles to address significant unmet medical needs. "
        narrative += "The combination of clinical rationale, favorable IP position, and market attractiveness supports further development."
        
        return narrative
    
    def _generate_market_discovery_narrative(
        self, disease_area: Optional[str], geography: Optional[str],
        competition: Dict, unmet_needs: List[str], attractiveness: Dict
    ) -> str:
        """Generate market discovery narrative."""
        
        narrative = f"**Market Opportunity Analysis: {disease_area or 'Therapeutic Area'}"
        if geography:
            narrative += f" in {geography}"
        narrative += "**\n\n"
        
        comp_level = competition.get("competition_level", "unknown")
        narrative += f"The competitive landscape shows {comp_level} competition with {competition.get('number_of_competitors', 0)} key players. "
        
        if unmet_needs:
            narrative += f"\n\nKey unmet needs identified:\n"
            for need in unmet_needs[:3]:
                narrative += f"• {need}\n"
        
        narrative += f"\n\nMarket attractiveness is rated as {attractiveness.get('rating', 'moderate')}, "
        narrative += f"with growth rate of {attractiveness.get('growth_rate', 'N/A')}%. "
        
        narrative += "\n\n**Strategic Opportunity**: This represents a viable market entry point with manageable competition and clear unmet needs."
        
        return narrative
    
    def _generate_molecule_narrative(
        self, molecule: Optional[str], disease_area: Optional[str], insights: List[str]
    ) -> str:
        """Generate molecule analysis narrative."""
        
        narrative = f"**Strategic Analysis: {molecule or 'Molecule'}"
        if disease_area:
            narrative += f" in {disease_area}"
        narrative += "**\n\n"
        
        narrative += "Key strategic insights:\n"
        for insight in insights[:5]:
            narrative += f"• {insight}\n"
        
        return narrative
    
    def _generate_general_narrative(self, question: str, insights: List[str]) -> str:
        """Generate narrative for general strategic questions."""
        
        narrative = f"**Strategic Question**: {question}\n\n"
        narrative += "**Insights**:\n"
        for insight in insights:
            narrative += f"• {insight}\n"
        
        return narrative
    
    def _extract_key_insights(
        self, trial_activity: Dict, fto_assessment: Dict, market_potential: Dict
    ) -> List[str]:
        """Extract key insights for executive summary."""
        
        insights = []
        
        insights.append(trial_activity.get("interpretation", ""))
        insights.append(fto_assessment.get("interpretation", ""))
        insights.append(market_potential.get("interpretation", ""))
        
        return [i for i in insights if i]
    
    def _generate_recommendations(
        self, molecule: Optional[str], disease_area: Optional[str],
        feasibility_score: float, fto_assessment: Dict
    ) -> List[str]:
        """Generate actionable recommendations."""
        
        recommendations = []
        
        if feasibility_score > 0.7:
            recommendations.append(f"✅ Strong repurposing candidate - recommend advancing to preclinical validation")
        elif feasibility_score > 0.5:
            recommendations.append(f"⚠️ Moderate potential - conduct deeper mechanism-of-action studies")
        else:
            recommendations.append(f"❌ Low feasibility - consider alternative molecules or indications")
        
        if fto_assessment.get("fto_level") == "constrained":
            recommendations.append("🔍 Conduct detailed FTO analysis and consider differentiated formulations")
        
        recommendations.append(f"📊 Initiate market research and KOL engagement in {disease_area or 'target indication'}")
        recommendations.append("🧪 Design proof-of-concept study with biomarkers aligned to mechanism")
        
        return recommendations
    
    # ==================== HELPER METHODS ====================
    
    def _assess_market_position(self, market_data: Dict, molecule: Optional[str]) -> Dict:
        """Assess market position of molecule."""
        overview = market_data.get("overview", {})
        return {
            "market_share": "N/A",  # Would calculate from real data
            "ranking": "N/A",
            "trend": "stable"
        }
    
    def _summarize_ip_landscape(self, patent_data: Dict) -> Dict:
        """Summarize IP landscape."""
        overview = patent_data.get("overview", {})
        return {
            "active_patents": overview.get("active_count", 0),
            "status": "monitored",
            "key_risks": []
        }
    
    def _summarize_clinical_landscape(self, clinical_data: Dict) -> Dict:
        """Summarize clinical trial landscape."""
        return {
            "total_trials": len(clinical_data.get("trials", [])),
            "pipeline_strength": "moderate"
        }
    
    def _summarize_trade_dynamics(self, exim_data: Dict) -> Dict:
        """Summarize trade dynamics."""
        return {
            "import_trend": "stable",
            "export_trend": "stable"
        }
    
    def _generate_strategic_insights(
        self, molecule: Optional[str], disease_area: Optional[str],
        market_pos: Dict, ip: Dict, clinical: Dict
    ) -> List[str]:
        """Generate strategic insights."""
        return [
            f"Market position: {market_pos.get('trend', 'stable')}",
            f"IP landscape: {ip.get('active_patents', 0)} active patents",
            f"Clinical pipeline: {clinical.get('pipeline_strength', 'moderate')} strength"
        ]
    
    def _suggest_molecules(self, disease_area: Optional[str], market_data: Dict) -> List[str]:
        """Suggest candidate molecules for the indication."""
        # In real implementation, would use more sophisticated logic
        return ["Candidate 1", "Candidate 2", "Candidate 3"]


# Quick self-test
if __name__ == "__main__":
    agent = StrategicOpportunityAgent()
    
    # Test repurposing workflow
    test_query = {
        "intent_type": "repurposing",
        "molecule": "Metformin",
        "disease_area": "NAFLD",
        "geography": "India",
        "agent_outputs": {
            "clinical_trials": {"trials": [{"phase": "Phase 2"}] * 3},
            "patent": {"overview": {"active_count": 2, "expired_count": 5}},
            "iqvia": {"overview": {"total_market_size_usd": 500000000, "yoy_growth_pct": 15}}
        }
    }
    
    result = agent.run(test_query)
    print("Strategic Opportunity Result:")
    print(f"Type: {result.get('opportunity_type')}")
    print(f"Feasibility Score: {result.get('feasibility_score')}")
    print(f"\nInnovation Story:\n{result.get('innovation_story')}")
    print(f"\nRecommendations:")
    for rec in result.get('recommendations', []):
        print(f"  {rec}")
