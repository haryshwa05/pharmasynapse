# backend/app/report/report_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from typing import Dict, Any, List
import os

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "reports"))
os.makedirs(OUT_DIR, exist_ok=True)


class ReportGenerator:
    """
    Enhanced Report Generator supporting:
    1. Legacy molecule analysis reports
    2. Comprehensive detailed reports with full agent outputs and visualizations
    """

    def _draw_header(self, c: canvas.Canvas, molecule: str):
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, f"PharmaSynapse Report — {molecule}")
        c.setStrokeColor(colors.grey)
        c.line(50, 745, 560, 745)

    def _draw_section_title(self, c: canvas.Canvas, title: str, y: int) -> int:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, title)
        return y - 16

    def _draw_bullets(self, c: canvas.Canvas, items: List[str], y: int) -> int:
        c.setFont("Helvetica", 10)
        for it in items:
            c.drawString(60, y, f"• {it}")
            y -= 14
            if y < 80:
                c.showPage()
                y = 750
        return y

    def _draw_simple_table(self, c: canvas.Canvas, rows: List[List[str]], y: int) -> int:
        c.setFont("Helvetica", 10)
        for row in rows:
            line = " | ".join(row)
            c.drawString(60, y, line)
            y -= 14
            if y < 80:
                c.showPage()
                y = 750
        return y

    def _safe_get(self, d: Dict[str, Any], key: str, default: str = "N/A") -> Any:
        return d.get(key, default) if isinstance(d, dict) else default

    def generate_pdf(self, analysis: Dict[str, Any]) -> str:
        molecule = analysis.get("molecule", "unknown")
        fname = f"report_{molecule}.pdf"
        path = os.path.join(OUT_DIR, fname)

        c = canvas.Canvas(path, pagesize=letter)
        y = 750
        self._draw_header(c, molecule)
        y -= 24

        # Executive Summary (from Synthesis)
        synthesis = analysis.get("synthesis", {})
        if synthesis:
            y = self._draw_section_title(c, "AI Executive Summary", y)
            exec_sum = synthesis.get("executive_summary", "")
            if exec_sum:
                # Simple text wrap logic could go here; for now just print line
                # Ideally reportlab Paragraph/Flowable is better, but keeping it simple:
                c.setFont("Helvetica", 10)
                # Split roughly
                words = exec_sum.split()
                line = ""
                for w in words:
                    if c.stringWidth(line + " " + w, "Helvetica", 10) < 450:
                        line += " " + w
                    else:
                        c.drawString(60, y, line)
                        y -= 12
                        line = w
                c.drawString(60, y, line)
                y -= 20

            # Recommendations
            recs = synthesis.get("strategic_recommendations", [])
            if recs:
                y = self._draw_section_title(c, "Strategic Recommendations", y)
                y = self._draw_bullets(c, recs, y)

        # Market (IQVIA)
        iq = analysis.get("iqvia", {}) or {}
        y = self._draw_section_title(c, "Market (IQVIA mock)", y)
        iq_rows = []
        regions = iq.get("regions", {}) if isinstance(iq, dict) else {}
        for rname, rdata in regions.items():
            iq_rows.append([
                rname,
                f"${rdata.get('market_size_usd_mn','?')}M",
                f"{rdata.get('cagr_5y_percent','?')}% CAGR",
                f"{len(rdata.get('competitors', []))} comps"
            ])
        if iq_rows:
            y = self._draw_simple_table(c, iq_rows, y)
        else:
            y = self._draw_bullets(c, [iq.get("message", "No market data found")], y)

        # Patents
        patents = analysis.get("patents", {}) or {}
        y = self._draw_section_title(c, "Patent Landscape", y)
        pov = patents.get("overview", {}) if isinstance(patents, dict) else {}
        patent_summary = patents.get("summary") or "No patent summary available."
        bullets = [
            f"Total: {pov.get('total','?')} | Active: {pov.get('active_count','?')} | Expired: {pov.get('expired_count','?')}",
            patent_summary
        ]
        y = self._draw_bullets(c, bullets, y)

        # Clinical trials
        trials = analysis.get("trials", {}) or {}
        y = self._draw_section_title(c, "Clinical Trials", y)
        tlist = trials.get("trials", []) if isinstance(trials, dict) else []
        trial_rows = []
        for t in tlist[:8]:
            trial_rows.append([
                t.get("trial_id", "N/A"),
                t.get("phase", "N/A"),
                t.get("status", "N/A"),
                t.get("condition", "N/A"),
            ])
        if trial_rows:
            y = self._draw_simple_table(c, trial_rows, y)
        else:
            y = self._draw_bullets(c, [trials.get("message", "No trials data found")], y)

        # Web intelligence
        web = analysis.get("web", {}) or {}
        y = self._draw_section_title(c, "Web Intelligence (guidelines/RWE/news)", y)
        web_summary = web.get("summary") or "No web results."
        y = self._draw_bullets(c, [web_summary], y)

        # EXIM
        exim = analysis.get("exim", {}) or {}
        y = self._draw_section_title(c, "EXIM Trade", y)
        exim_summary = exim.get("summary") or "No EXIM data."
        y = self._draw_bullets(c, [exim_summary], y)

        # Internal docs
        internal = analysis.get("internal", {}) or {}
        y = self._draw_section_title(c, "Internal Documents", y)
        docs = internal.get("documents", []) if isinstance(internal, dict) else []
        doc_rows = []
        for d in docs[:6]:
            doc_rows.append([
                d.get("title", "Untitled"),
                d.get("type", "doc"),
                str(d.get("year", "")),
            ])
        if doc_rows:
            y = self._draw_simple_table(c, doc_rows, y)
        else:
            y = self._draw_bullets(c, [internal.get("message", "No internal docs found")], y)

        c.showPage()
        c.save()
        return path

    def generate_comprehensive_report(self, workflow_result: Dict[str, Any]) -> str:
        """
        Generate comprehensive detailed PDF report with all agent outputs and visualizations.

        This creates a full detailed report including:
        - Strategic question and context
        - Complete agent outputs with detailed data
        - Market intelligence with charts/tables
        - Patent landscape analysis
        - Clinical trials data
        - Web intelligence with links
        - Strategic recommendations and insights
        """

        query_intent = workflow_result.get("query_intent", {})
        strategic_question = query_intent.get("strategic_question") or "Strategic Analysis"
        molecule = query_intent.get("primary_entity", "Analysis")
        disease = query_intent.get("disease_area", "")

        # Generate filename
        fname = f"comprehensive_{molecule}_{disease}".replace(" ", "_").replace("/", "_")
        fname = f"{fname}.pdf"
        path = os.path.join(OUT_DIR, fname)

        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter

        # ==================== PAGE 1: Cover & Strategic Question ====================
        self._draw_comprehensive_cover(c, query_intent, strategic_question)
        c.showPage()

        # ==================== PAGE 2: Agent Execution Summary ====================
        self._draw_agent_execution_summary(c, workflow_result)
        c.showPage()

        # ==================== PAGES 3+: Detailed Agent Outputs ====================
        self._draw_detailed_agent_outputs(c, workflow_result)

        c.save()
        return path

    def _draw_comprehensive_cover(self, c, query_intent, strategic_question):
        """Page 1: Cover page with strategic question and context"""

        # Header
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(300, 700, "PharmaSynapse")

        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(300, 670, "Comprehensive Strategic Intelligence Report")

        # Strategic Question Section
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 600, "Strategic Question:")

        # Question box
        c.setStrokeColor(colors.HexColor("#2196F3"))
        c.setFillColor(colors.HexColor("#E3F2FD"))
        c.rect(50, 520, 500, 70, fill=1, stroke=1)

        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        self._draw_wrapped_text(c, strategic_question, 60, 570, 480, 14)

        # Context Information
        y = 480
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Analysis Context:")
        y -= 25

        c.setFont("Helvetica", 11)
        context_items = [
            f"Intent Type: {query_intent.get('intent_type', 'N/A').replace('_', ' ').title()}",
            f"Molecule: {query_intent.get('primary_entity') or 'Not specified'}",
            f"Disease Area: {query_intent.get('disease_area') or 'Not specified'}",
            f"Geography: {query_intent.get('geography') or 'Global'}",
            f"Analysis Method: {'AI-Powered Prompt Analysis' if not query_intent.get('is_structured_input') else 'Structured Input Analysis'}",
            f"Report Generated: {workflow_result.get('end_time', 'Real-time')}",
        ]

        for item in context_items:
            c.drawString(60, y, f"• {item}")
            y -= 18

        # Footer
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(300, 50, "Comprehensive Strategic Intelligence Report | Powered by Multi-Agent AI")

    def _draw_agent_execution_summary(self, c, workflow_result):
        """Page 2: Agent execution summary and performance metrics"""

        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(300, 700, "Multi-Agent Execution Summary")

        execution_log = workflow_result.get("execution_log", [])
        agent_outputs = workflow_result.get("agent_outputs", {})

        y = 650

        # Execution Timeline
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Agent Execution Timeline:")
        y -= 25

        c.setFont("Helvetica", 11)

        # Draw timeline of agent execution
        for i, stage in enumerate(execution_log):
            stage_name = stage.get("stage", "")
            status = stage.get("status", "")
            timestamp = stage.get("timestamp", "")
            has_data = stage.get("has_data", False)

            # Status indicator
            if status == "success":
                c.setFillColor(colors.green)
                status_icon = "✓"
            else:
                c.setFillColor(colors.red)
                status_icon = "✗"

            # Timeline line
            if i > 0:
                c.setStrokeColor(colors.grey)
                c.line(70, y + 25, 70, y + 5)

            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(80, y, f"{status_icon} {stage_name.upper()}")

            c.setFont("Helvetica", 10)
            # Add descriptions for each agent
            descriptions = {
                "iqvia": "Market Intelligence & Competitive Analysis",
                "clinical_trials": "Clinical Trial Landscape & Pipeline",
                "patent": "Patent Landscape & IP Analysis",
                "exim": "Import/Export Trends & Supply Chain",
                "web_intelligence": "Web Research & Latest Intelligence",
                "strategic_opportunity": "AI Strategic Synthesis & Recommendations"
            }

            description = descriptions.get(stage_name, "Data Analysis")
            c.drawString(100, y - 15, description)

            c.setFont("Helvetica-Oblique", 9)
            data_status = f"Data: {'Retrieved' if has_data else 'Not available'}"
            c.drawString(100, y - 28, f"Time: {timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp}")

            y -= 50

            if y < 200:
                break

        # Performance Summary
        y = 180
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Performance Summary:")
        y -= 20

        c.setFont("Helvetica", 10)
        exec_time = workflow_result.get("execution_time_seconds", 0)
        total_agents = len(execution_log)
        successful_agents = len([e for e in execution_log if e.get("status") == "success"])
        data_sources = len([e for e in execution_log if e.get("has_data")])

        summary_items = [
            f"Total execution time: {exec_time:.2f} seconds",
            f"Agents executed: {total_agents}",
            f"Successful executions: {successful_agents}",
            f"Data sources accessed: {data_sources}",
            f"Analysis confidence: {query_intent.get('confidence', 0) * 100:.1f}%"
        ]

        for item in summary_items:
            c.drawString(60, y, f"• {item}")
            y -= 15

    def _draw_detailed_agent_outputs(self, c, workflow_result):
        """Pages 3+: Detailed outputs from each agent"""

        agent_outputs = workflow_result.get("agent_outputs", {})

        # IQVIA Market Intelligence
        if agent_outputs.get("iqvia", {}).get("available"):
            self._draw_iqvia_detailed_page(c, agent_outputs["iqvia"])
            c.showPage()

        # Patent Landscape
        if agent_outputs.get("patent", {}).get("available"):
            self._draw_patent_detailed_page(c, agent_outputs["patent"])
            c.showPage()

        # Clinical Trials
        if agent_outputs.get("clinical_trials", {}).get("available"):
            self._draw_trials_detailed_page(c, agent_outputs["clinical_trials"])
            c.showPage()

        # EXIM & Supply Chain
        if agent_outputs.get("exim", {}).get("available"):
            self._draw_exim_detailed_page(c, agent_outputs["exim"])
            c.showPage()

        # Web Intelligence
        if agent_outputs.get("web_intelligence", {}).get("available"):
            self._draw_web_detailed_page(c, agent_outputs["web_intelligence"])
            c.showPage()

        # Strategic Opportunity & Recommendations
        strategic = agent_outputs.get("strategic_opportunity", {})
        if strategic:
            self._draw_strategic_recommendations_page(c, strategic)

    def _draw_iqvia_detailed_page(self, c, iqvia_data):
        """Detailed IQVIA market intelligence page"""
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(300, 700, "Market Intelligence (IQVIA)")

        y = 650
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Market Analysis:")
        y -= 25

        # Market data table
        regions = iqvia_data.get("regions", {})
        if regions:
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "Regional Market Data:")
            y -= 20

            c.setFont("Helvetica", 9)
            headers = ["Region", "Market Size", "CAGR", "Competitors"]
            col_widths = [100, 80, 60, 80]
            x_pos = 50

            for i, header in enumerate(headers):
                c.drawString(x_pos, y, header)
                x_pos += col_widths[i]

            y -= 15
            c.line(50, y, 370, y)
            y -= 10

            for region_name, region_data in list(regions.items())[:8]:
                x_pos = 50
                row_data = [
                    region_name[:15],
                    f"${region_data.get('market_size_usd_mn', '?')}M",
                    f"{region_data.get('cagr_5y_percent', '?')}%",
                    str(len(region_data.get('competitors', [])))
                ]

                for i, data in enumerate(row_data):
                    c.drawString(x_pos, y, data)
                    x_pos += col_widths[i]
                y -= 12

        # Summary
        if iqvia_data.get("summary"):
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Market Summary:")
            y -= 15
            c.setFont("Helvetica", 10)
            self._draw_wrapped_text(c, iqvia_data["summary"], 60, y, 480, 12)

    def _draw_patent_detailed_page(self, c, patent_data):
        """Detailed patent landscape page"""
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(300, 700, "Patent Landscape Analysis")

        y = 650

        # Overview stats
        overview = patent_data.get("overview", {})
        if overview:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "Patent Portfolio Overview:")
            y -= 25

            c.setFont("Helvetica", 11)
            stats = [
                f"Total Patents: {overview.get('total', 'N/A')}",
                f"Active Patents: {overview.get('active_count', 'N/A')}",
                f"Expired Patents: {overview.get('expired_count', 'N/A')}",
                f"Pending Applications: {overview.get('pending_count', 'N/A')}"
            ]

            for stat in stats:
                c.drawString(60, y, f"• {stat}")
                y -= 15

        # Summary
        if patent_data.get("summary"):
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Patent Analysis Summary:")
            y -= 15
            c.setFont("Helvetica", 10)
            self._draw_wrapped_text(c, patent_data["summary"], 60, y, 480, 12)

    def _draw_trials_detailed_page(self, c, trials_data):
        """Detailed clinical trials page"""
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(300, 700, "Clinical Trials Landscape")

        y = 650

        # Phase distribution
        phase_dist = trials_data.get("overview", {}).get("phase_distribution", {})
        if phase_dist:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "Clinical Development Pipeline:")
            y -= 25

            c.setFont("Helvetica", 11)
            for phase, count in phase_dist.items():
                c.drawString(60, y, f"• Phase {phase}: {count} trials")
                y -= 15

        # Summary
        if trials_data.get("summary"):
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Clinical Trials Summary:")
            y -= 15
            c.setFont("Helvetica", 10)
            self._draw_wrapped_text(c, trials_data["summary"], 60, y, 480, 12)

    def _draw_exim_detailed_page(self, c, exim_data):
        """Detailed EXIM & supply chain page"""
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(300, 700, "Import/Export & Supply Chain")

        y = 650

        # Trade data
        overview = exim_data.get("overview", {})
        if overview:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "Trade Overview:")
            y -= 25

            c.setFont("Helvetica", 11)
            trade_stats = [
                f"Total Export Value: ${overview.get('total_export_value_usd_mn', 0):.1f}M",
                f"Total Import Value: ${overview.get('total_import_value_usd_mn', 0):.1f}M",
                f"Total Export Volume: {overview.get('total_export_volume_tons', 0):.1f} tons",
                f"Total Import Volume: {overview.get('total_import_volume_tons', 0):.1f} tons"
            ]

            for stat in trade_stats:
                c.drawString(60, y, f"• {stat}")
                y -= 15

        # Summary
        if exim_data.get("summary"):
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Supply Chain Analysis:")
            y -= 15
            c.setFont("Helvetica", 10)
            self._draw_wrapped_text(c, exim_data["summary"], 60, y, 480, 12)

    def _draw_web_detailed_page(self, c, web_data):
        """Detailed web intelligence page"""
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(300, 700, "Web Intelligence & Latest Insights")

        y = 650

        # Guidelines
        guidelines = web_data.get("guidelines", [])
        if guidelines:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "Regulatory Guidelines:")
            y -= 20

            c.setFont("Helvetica", 10)
            for guideline in guidelines[:5]:
                title = guideline.get("title", "Untitled")[:50]
                c.drawString(60, y, f"• {title}")
                if guideline.get("url"):
                    c.setFont("Helvetica-Oblique", 8)
                    c.drawString(70, y - 10, f"URL: {guideline['url'][:60]}...")
                    c.setFont("Helvetica", 10)
                    y -= 5
                y -= 15

        # News & Updates
        news = web_data.get("news", [])
        if news:
            y -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Latest News & Updates:")
            y -= 15

            c.setFont("Helvetica", 9)
            for item in news[:8]:
                title = item.get("title", "Untitled")[:60]
                c.drawString(60, y, f"• {title}")
                if item.get("url"):
                    c.setFont("Helvetica-Oblique", 7)
                    c.drawString(70, y - 8, f"Source: {item['url'][:50]}...")
                    c.setFont("Helvetica", 9)
                    y -= 3
                y -= 12

        # Summary
        if web_data.get("summary"):
            y -= 15
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "Web Intelligence Summary:")
            y -= 12
            c.setFont("Helvetica", 9)
            self._draw_wrapped_text(c, web_data["summary"], 60, y, 480, 10)

    def _draw_strategic_recommendations_page(self, c, strategic_data):
        """Strategic recommendations and final insights page"""
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(300, 700, "Strategic Recommendations & Insights")

        y = 650

        # Decision Framework
        decision = strategic_data.get("decision_framework", {})
        if decision.get("recommendation"):
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y, "GO/NO-GO Recommendation:")
            y -= 25

            # Recommendation box
            c.setFillColor(colors.HexColor("#E8F5E8") if decision["recommendation"].upper() == "YES" else colors.HexColor("#FFF3E0"))
            c.setStrokeColor(colors.HexColor("#4CAF50") if decision["recommendation"].upper() == "YES" else colors.HexColor("#FF9800"))
            c.rect(50, y - 30, 200, 35, fill=1, stroke=1)

            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(60, y - 15, decision["recommendation"].upper())

            if decision.get("confidence"):
                c.setFont("Helvetica", 10)
                c.drawString(60, y - 28, f"Confidence: {decision['confidence']}")
            y -= 50

        # Key Recommendations
        recommendations = strategic_data.get("recommendations", [])
        if recommendations:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "Strategic Action Plan:")
            y -= 25

            c.setFont("Helvetica", 11)
            for i, rec in enumerate(recommendations[:8], 1):
                rec_text = rec.get("action", rec) if isinstance(rec, dict) else rec
                c.drawString(60, y, f"{i}. {rec_text[:80]}...")
                if isinstance(rec, dict) and rec.get("rationale"):
                    c.setFont("Helvetica-Oblique", 9)
                    c.drawString(70, y - 12, f"Rationale: {rec['rationale'][:60]}...")
                    c.setFont("Helvetica", 11)
                    y -= 5
                y -= 20

        # Innovation Story
        innovation_story = strategic_data.get("innovation_story", "")
        if innovation_story:
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Innovation Narrative:")
            y -= 15
            c.setFont("Helvetica", 10)
            self._draw_wrapped_text(c, innovation_story, 60, y, 480, 12)

    def _draw_wrapped_text(self, c, text, x, y, max_width, line_height):
        """Draw text with wrapping."""
        words = str(text).split()
        line = ""

        for word in words:
            test_line = line + " " + word if line else word
            if c.stringWidth(test_line, "Helvetica", 10) < max_width:
                line = test_line
            else:
                c.drawString(x, y, line)
                y -= line_height
                line = word

                if y < 80:
                    return y

        if line:
            c.drawString(x, y, line)
            y -= line_height

        return y
        if iqvia_data and iqvia_data.get("available"):
            y = self._draw_data_section(c, "Market Intelligence (IQVIA)", iqvia_data, y)
        
        # Patent Data
        patent_data = agent_outputs.get("patent", {})
        if patent_data and patent_data.get("available"):
            y = self._draw_data_section(c, "Patent Landscape (PatentsView)", patent_data, y)
        
        # Clinical Trials
        trials_data = agent_outputs.get("clinical_trials", {})
        if trials_data and trials_data.get("available"):
            y = self._draw_data_section(c, "Clinical Trials", trials_data, y)
        
        # EXIM
        exim_data = agent_outputs.get("exim", {})
        if exim_data and exim_data.get("available"):
            y = self._draw_data_section(c, "Import/Export Trends", exim_data, y)
        
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(300, 50, "Slide 3 of 5 | Data Synthesis")
    
    def _draw_slide_4_strategic_opportunity(self, c, workflow_result):
        """Slide 4: Strategic Opportunity & Innovation Story"""
        
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(300, 700, "Strategic Opportunity")
        
        agent_outputs = workflow_result.get("agent_outputs", {})
        strategic_output = agent_outputs.get("strategic_opportunity", {})
        
        y = 660
        
        # Innovation Story
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Innovation Narrative:")
        y -= 20
        
        innovation_story = strategic_output.get("innovation_story", "Analysis in progress...")
        c.setFont("Helvetica", 10)
        y = self._draw_wrapped_text(c, innovation_story, 60, y, 480, 12)
        y -= 30
        
        # Feasibility Score (if repurposing)
        if strategic_output.get("opportunity_type") == "repurposing":
            feasibility = strategic_output.get("feasibility_score", 0.0)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"Feasibility Score: {feasibility}/1.0")
            
            # Visual bar
            bar_width = feasibility * 200
            c.setFillColor(colors.HexColor("#4CAF50") if feasibility > 0.7 else colors.HexColor("#FF9800"))
            c.rect(220, y - 5, bar_width, 15, fill=1)
            y -= 30
        
        # Key Insights
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Key Insights:")
        y -= 18
        
        key_insights = strategic_output.get("key_insights", [])
        c.setFont("Helvetica", 10)
        for insight in key_insights[:5]:
            y = self._draw_wrapped_text(c, f"• {insight}", 60, y, 480, 12)
            y -= 5
        
        # Unmet Needs
        if strategic_output.get("unmet_needs"):
            y -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Unmet Medical Needs:")
            y -= 18
            
            c.setFont("Helvetica", 10)
            for need in strategic_output.get("unmet_needs", [])[:3]:
                y = self._draw_wrapped_text(c, f"• {need}", 60, y, 480, 12)
                y -= 5
        
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(300, 50, "Slide 4 of 5 | Strategic Opportunity & Innovation Story")
    
    def _draw_slide_5_recommendations(self, c, workflow_result):
        """Slide 5: Recommendations & Next Steps"""
        
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(300, 700, "Recommendations & Next Steps")
        
        agent_outputs = workflow_result.get("agent_outputs", {})
        strategic_output = agent_outputs.get("strategic_opportunity", {})
        
        y = 660
        
        # Recommendations
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Strategic Recommendations:")
        y -= 25
        
        recommendations = strategic_output.get("recommendations", [
            "Complete detailed mechanism-of-action analysis",
            "Engage with key opinion leaders in target indication",
            "Conduct market research and competitive intelligence",
            "Evaluate regulatory pathway and requirements",
            "Design proof-of-concept clinical study"
        ])
        
        c.setFont("Helvetica", 11)
        for i, rec in enumerate(recommendations[:6], 1):
            # Draw box for each recommendation
            c.setStrokeColor(colors.grey)
            c.setFillColor(colors.HexColor("#F5F5F5"))
            c.rect(60, y - 35, 480, 40, fill=1, stroke=1)
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(70, y - 15, f"{i}.")
            
            c.setFont("Helvetica", 10)
            self._draw_wrapped_text(c, rec, 90, y - 15, 440, 11)
            
            y -= 50
            
            if y < 200:
                break
        
        # Summary footer
        y = 150
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Summary:")
        c.setFont("Helvetica", 10)
        summary = workflow_result.get("summary", "Complete multi-agent strategic analysis")
        self._draw_wrapped_text(c, summary, 60, y - 18, 480, 12)
        
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(300, 50, "Slide 5 of 5 | Recommendations & Next Steps")
        
        # Report metadata
        c.setFont("Helvetica", 8)
        c.drawRightString(550, 35, f"Generated: {workflow_result.get('end_time', 'N/A')}")
    
    # ==================== HELPER METHODS ====================
    
    def _draw_data_section(self, c, title, data, y):
        """Draw a data section with title and summary."""
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"{title}:")
        y -= 18
        
        summary = data.get("summary") or data.get("overview", {})
        if isinstance(summary, str):
            c.setFont("Helvetica", 10)
            y = self._draw_wrapped_text(c, summary, 60, y, 480, 11)
        elif isinstance(summary, dict):
            c.setFont("Helvetica", 9)
            for key, value in list(summary.items())[:3]:
                c.drawString(60, y, f"• {key}: {value}")
                y -= 12
        
        y -= 15
        return y
    
    def _draw_wrapped_text(self, c, text, x, y, max_width, line_height):
        """Draw text with wrapping."""
        words = str(text).split()
        line = ""
        
        for word in words:
            test_line = line + " " + word if line else word
            if c.stringWidth(test_line, "Helvetica", 10) < max_width:
                line = test_line
            else:
                c.drawString(x, y, line)
                y -= line_height
                line = word
                
                if y < 80:
                    return y
        
        if line:
            c.drawString(x, y, line)
            y -= line_height
        
        return y
