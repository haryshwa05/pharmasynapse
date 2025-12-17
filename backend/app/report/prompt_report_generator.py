"""
Enhanced PDF Report Generator for Prompt-Based Analysis
Creates beautiful, comprehensive reports that will impress judges.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Dict, Any, List
import os


class PromptReportGenerator:
    """
    Generates beautiful, comprehensive PDF reports for prompt-based analysis.
    
    Features:
    - Professional branding and layout
    - Multi-section structure
    - Data visualizations as tables
    - Color-coded insights
    - Executive-ready formatting
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Create custom paragraph styles for professional formatting."""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#5c6bc0'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#3f51b5'),
            borderPadding=5,
            backColor=colors.HexColor('#e8eaf6')
        ))
        
        # Subsection header
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#3949ab'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text justified
        self.styles.add(ParagraphStyle(
            name='BodyJustify',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
        
        # Highlight box
        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=self.styles['Normal'],
            fontSize=10,
            backColor=colors.HexColor('#fff9c4'),
            borderWidth=1,
            borderColor=colors.HexColor('#fbc02d'),
            borderPadding=10,
            spaceAfter=15
        ))
    
    def generate_report(self, analysis_result: Dict[str, Any], output_path: str):
        """
        Generate comprehensive PDF report from prompt analysis results.
        
        Args:
            analysis_result: The output from EnhancedPromptWorkflow
            output_path: Where to save the PDF
        """
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build the story (content)
        story = []
        
        # 1. Cover Page
        story.extend(self._create_cover_page(analysis_result))
        story.append(PageBreak())
        
        # 2. Executive Summary
        story.extend(self._create_executive_summary(analysis_result))
        story.append(Spacer(1, 0.3*inch))
        
        # 3. Key Findings
        story.extend(self._create_key_findings(analysis_result))
        story.append(Spacer(1, 0.2*inch))
        
        # 4. Market Analysis
        story.extend(self._create_market_analysis(analysis_result))
        story.append(Spacer(1, 0.2*inch))
        
        # 5. Competitive Landscape
        story.extend(self._create_competitive_landscape(analysis_result))
        story.append(PageBreak())
        
        # 6. Strategic Recommendations
        story.extend(self._create_strategic_recommendations(analysis_result))
        story.append(Spacer(1, 0.2*inch))
        
        # 7. SWOT Analysis
        story.extend(self._create_swot_analysis(analysis_result))
        story.append(PageBreak())
        
        # 8. Opportunities & Risks
        story.extend(self._create_opportunities_risks(analysis_result))
        story.append(Spacer(1, 0.2*inch))
        
        # 9. Innovation Story
        story.extend(self._create_innovation_story(analysis_result))
        story.append(Spacer(1, 0.2*inch))
        
        # 10. Data Sources & Methodology
        story.extend(self._create_data_sources(analysis_result))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return output_path
    
    def _create_cover_page(self, result: Dict[str, Any]) -> List:
        """Create impressive cover page."""
        elements = []
        
        # Logo/Branding space
        elements.append(Spacer(1, 1*inch))
        
        # Title
        elements.append(Paragraph(
            "PharmaSynapse Intelligence Report",
            self.styles['CustomTitle']
        ))
        
        # Subtitle - the user's question
        query = result.get('query_analysis', {}).get('original_question', 'Strategic Analysis')
        elements.append(Paragraph(
            f'<i>"{query}"</i>',
            self.styles['CustomSubtitle']
        ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Key metadata table
        query_analysis = result.get('query_analysis', {})
        metadata = [
            ['Analysis Type:', query_analysis.get('detected_intent', 'N/A').replace('_', ' ').title()],
            ['Molecule:', query_analysis.get('extracted_entities', {}).get('molecule') or 'Not specified'],
            ['Disease Area:', query_analysis.get('extracted_entities', {}).get('disease_area') or 'Not specified'],
            ['Geography:', query_analysis.get('extracted_entities', {}).get('geography') or 'Not specified'],
            ['Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Analysis Depth:', 'Comprehensive'],
            ['Confidence:', f"{query_analysis.get('confidence_score', 0.9) * 100:.0f}%"]
        ]
        
        t = Table(metadata, colWidths=[2*inch, 3.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eaf6')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#283593')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 1*inch))
        
        # Disclaimer
        elements.append(Paragraph(
            "<i>This report contains strategic pharmaceutical intelligence generated by AI-powered analysis "
            "of multiple data sources including market data, clinical trials, patents, and trade information.</i>",
            self.styles['BodyJustify']
        ))
        
        return elements
    
    def _create_executive_summary(self, result: Dict[str, Any]) -> List:
        """Create executive summary section."""
        elements = []
        
        analysis = result.get('comprehensive_analysis', {})
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        summary = analysis.get('executive_summary', 'No summary available.')
        elements.append(Paragraph(summary, self.styles['BodyJustify']))
        
        # Add executive dashboard highlights
        dashboard = result.get('executive_dashboard', {})
        if dashboard:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Key Highlights", self.styles['SubsectionHeader']))
            
            highlights = dashboard.get('top_insights', [])
            if highlights:
                for highlight in highlights[:3]:
                    elements.append(Paragraph(f"• {highlight}", self.styles['Normal']))
        
        return elements
    
    def _create_key_findings(self, result: Dict[str, Any]) -> List:
        """Create key findings section with multiple categories."""
        elements = []
        
        analysis = result.get('comprehensive_analysis', {})
        findings = analysis.get('key_findings', {})
        
        elements.append(Paragraph("Key Findings", self.styles['SectionHeader']))
        
        # Market Insights
        if findings.get('market_insights'):
            elements.append(Paragraph("Market Insights", self.styles['SubsectionHeader']))
            for insight in findings['market_insights']:
                elements.append(Paragraph(f"✓ {insight}", self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Clinical Insights
        if findings.get('clinical_insights'):
            elements.append(Paragraph("Clinical & Pipeline Insights", self.styles['SubsectionHeader']))
            for insight in findings['clinical_insights']:
                elements.append(Paragraph(f"✓ {insight}", self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # IP Insights
        if findings.get('ip_insights'):
            elements.append(Paragraph("Intellectual Property Insights", self.styles['SubsectionHeader']))
            for insight in findings['ip_insights']:
                elements.append(Paragraph(f"✓ {insight}", self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Strategic Insights
        if findings.get('strategic_insights'):
            elements.append(Paragraph("Strategic Insights", self.styles['SubsectionHeader']))
            for insight in findings['strategic_insights']:
                elements.append(Paragraph(f"★ {insight}", self.styles['Normal']))
        
        return elements
    
    def _create_market_analysis(self, result: Dict[str, Any]) -> List:
        """Create market analysis section."""
        elements = []
        
        analysis = result.get('comprehensive_analysis', {})
        market = analysis.get('market_analysis', {})
        
        elements.append(Paragraph("Market Analysis", self.styles['SectionHeader']))
        
        # Market overview table
        market_data = [
            ['Metric', 'Value'],
            ['Market Size', market.get('market_size', 'N/A')],
            ['Growth Rate', market.get('growth_rate', 'N/A')],
            ['Competitive Intensity', market.get('competitive_intensity', 'N/A')]
        ]
        
        t = Table(market_data, colWidths=[2.5*inch, 4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3f51b5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#e8eaf6')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')])
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 0.15*inch))
        
        # Market dynamics
        dynamics = market.get('market_dynamics', '')
        if dynamics:
            elements.append(Paragraph("Market Dynamics", self.styles['SubsectionHeader']))
            elements.append(Paragraph(dynamics, self.styles['BodyJustify']))
        
        # Key players
        players = market.get('key_players', [])
        if players:
            elements.append(Paragraph("Key Market Players", self.styles['SubsectionHeader']))
            for player in players:
                elements.append(Paragraph(f"• {player}", self.styles['Normal']))
        
        return elements
    
    def _create_competitive_landscape(self, result: Dict[str, Any]) -> List:
        """Create competitive landscape section."""
        elements = []
        
        analysis = result.get('comprehensive_analysis', {})
        competitive = analysis.get('competitive_landscape', {})
        
        elements.append(Paragraph("Competitive Landscape", self.styles['SectionHeader']))
        
        # Competition level
        comp_level = competitive.get('competition_level', 'Unknown')
        elements.append(Paragraph(
            f"<b>Competition Level:</b> {comp_level}",
            self.styles['HighlightBox']
        ))
        
        # Key competitors
        competitors = competitive.get('key_competitors', [])
        if competitors:
            elements.append(Paragraph("Key Competitors", self.styles['SubsectionHeader']))
            for comp in competitors:
                if isinstance(comp, dict):
                    name = comp.get('name', 'Unknown')
                    strengths = comp.get('strengths', 'N/A')
                    elements.append(Paragraph(f"<b>{name}</b>: {strengths}", self.styles['Normal']))
                    elements.append(Spacer(1, 0.05*inch))
        
        # Competitive gaps
        gaps = competitive.get('competitive_gaps', [])
        if gaps:
            elements.append(Paragraph("Identified Competitive Gaps", self.styles['SubsectionHeader']))
            for gap in gaps:
                elements.append(Paragraph(f"→ {gap}", self.styles['Normal']))
        
        return elements
    
    def _create_strategic_recommendations(self, result: Dict[str, Any]) -> List:
        """Create strategic recommendations section."""
        elements = []
        
        analysis = result.get('comprehensive_analysis', {})
        recommendations = analysis.get('strategic_recommendations', [])
        
        elements.append(Paragraph("Strategic Recommendations", self.styles['SectionHeader']))
        
        for rec in recommendations:
            if isinstance(rec, dict):
                priority = rec.get('priority', '')
                recommendation = rec.get('recommendation', '')
                rationale = rec.get('rationale', '')
                metrics = rec.get('success_metrics', '')
                
                # Recommendation box
                rec_text = f"""
                <b>Priority {priority}: {recommendation}</b><br/>
                <i>Rationale:</i> {rationale}<br/>
                <i>Success Metrics:</i> {metrics}
                """
                elements.append(Paragraph(rec_text, self.styles['HighlightBox']))
        
        return elements
    
    def _create_swot_analysis(self, result: Dict[str, Any]) -> List:
        """Create SWOT analysis section."""
        elements = []
        
        analysis = result.get('comprehensive_analysis', {})
        swot = analysis.get('swot_analysis', {})
        
        elements.append(Paragraph("SWOT Analysis", self.styles['SectionHeader']))
        
        # Create SWOT table
        swot_data = [
            ['Strengths', 'Weaknesses'],
            [self._format_list(swot.get('strengths', [])), self._format_list(swot.get('weaknesses', []))],
            ['Opportunities', 'Threats'],
            [self._format_list(swot.get('opportunities', [])), self._format_list(swot.get('threats', []))]
        ]
        
        t = Table(swot_data, colWidths=[3.25*inch, 3.25*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#4caf50')),
            ('BACKGROUND', (0, 2), (1, 2), colors.HexColor('#2196f3')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('TEXTCOLOR', (0, 2), (1, 2), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 1), (1, 1), colors.HexColor('#e8f5e9')),
            ('BACKGROUND', (0, 3), (1, 3), colors.HexColor('#e3f2fd'))
        ]))
        elements.append(t)
        
        return elements
    
    def _create_opportunities_risks(self, result: Dict[str, Any]) -> List:
        """Create opportunities and risks section."""
        elements = []
        
        analysis = result.get('comprehensive_analysis', {})
        opp_risks = analysis.get('opportunities_and_risks', {})
        
        elements.append(Paragraph("Opportunities & Risks Assessment", self.styles['SectionHeader']))
        
        # Opportunities
        opportunities = opp_risks.get('opportunities', [])
        if opportunities:
            elements.append(Paragraph("Opportunities", self.styles['SubsectionHeader']))
            for opp in opportunities:
                if isinstance(opp, dict):
                    title = opp.get('title', 'Opportunity')
                    desc = opp.get('description', '')
                    impact = opp.get('potential_impact', 'Medium')
                    timeframe = opp.get('timeframe', 'Medium term')
                    
                    opp_text = f"<b>{title}</b> (Impact: {impact}, Timeframe: {timeframe})<br/>{desc}"
                    elements.append(Paragraph(opp_text, self.styles['Normal']))
                    elements.append(Spacer(1, 0.1*inch))
        
        # Risks
        risks = opp_risks.get('risks', [])
        if risks:
            elements.append(Paragraph("Risks", self.styles['SubsectionHeader']))
            for risk in risks:
                if isinstance(risk, dict):
                    title = risk.get('title', 'Risk')
                    desc = risk.get('description', '')
                    severity = risk.get('severity', 'Medium')
                    mitigation = risk.get('mitigation', 'To be determined')
                    
                    risk_text = f"<b>{title}</b> (Severity: {severity})<br/>{desc}<br/><i>Mitigation: {mitigation}</i>"
                    elements.append(Paragraph(risk_text, self.styles['Normal']))
                    elements.append(Spacer(1, 0.1*inch))
        
        # Unmet needs
        unmet = opp_risks.get('unmet_needs', [])
        if unmet:
            elements.append(Paragraph("Identified Unmet Needs", self.styles['SubsectionHeader']))
            for need in unmet:
                elements.append(Paragraph(f"• {need}", self.styles['Normal']))
        
        return elements
    
    def _create_innovation_story(self, result: Dict[str, Any]) -> List:
        """Create innovation story section."""
        elements = []
        
        analysis = result.get('comprehensive_analysis', {})
        story = analysis.get('innovation_story', '')
        
        if story:
            elements.append(Paragraph("Innovation Story", self.styles['SectionHeader']))
            
            # Split story into paragraphs if it's long
            paragraphs = story.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    elements.append(Paragraph(para.strip(), self.styles['BodyJustify']))
                    elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_data_sources(self, result: Dict[str, Any]) -> List:
        """Create data sources and methodology section."""
        elements = []
        
        data_sources = result.get('data_sources', {})
        
        elements.append(Paragraph("Data Sources & Methodology", self.styles['SectionHeader']))
        
        sources = data_sources.get('sources_consulted', [])
        if sources:
            elements.append(Paragraph("Intelligence Sources Consulted:", self.styles['SubsectionHeader']))
            source_names = {
                'iqvia': 'Market Intelligence (IQVIA)',
                'clinical_trials': 'Clinical Trials Database',
                'patent': 'Patent Landscape Analysis',
                'exim': 'Import/Export Trade Data',
                'web_intelligence': 'Web Intelligence & Research'
            }
            
            for source in sources:
                name = source_names.get(source, source.replace('_', ' ').title())
                elements.append(Paragraph(f"✓ {name}", self.styles['Normal']))
        
        elements.append(Spacer(1, 0.15*inch))
        
        metadata = result.get('report_metadata', {})
        method = metadata.get('synthesis_method', 'Unknown')
        
        methodology_text = f"""
        <b>Analysis Methodology:</b><br/>
        This report was generated using {method} synthesis, combining data from multiple pharmaceutical 
        intelligence sources. The analysis includes market data, clinical pipeline information, patent landscapes, 
        and trade dynamics to provide a comprehensive strategic perspective.
        """
        elements.append(Paragraph(methodology_text, self.styles['BodyJustify']))
        
        return elements
    
    def _format_list(self, items: List[str]) -> str:
        """Format list for table cells."""
        if not items:
            return "None identified"
        return "<br/>".join([f"• {item}" for item in items[:5]])  # Limit to 5 items
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()
        
        # Footer
        footer_text = f"PharmaSynapse Intelligence Platform | Generated {datetime.now().strftime('%B %Y')} | Page {doc.page}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(4.25*inch, 0.5*inch, footer_text)
        
        # Header line on non-cover pages
        if doc.page > 1:
            canvas.setStrokeColor(colors.HexColor('#3f51b5'))
            canvas.setLineWidth(2)
            canvas.line(0.75*inch, 10.5*inch, 7.75*inch, 10.5*inch)
        
        canvas.restoreState()


# Convenience function
def generate_prompt_report(analysis_result: Dict[str, Any], output_dir: str = "reports") -> str:
    """
    Generate PDF report from prompt analysis.
    
    Args:
        analysis_result: Output from EnhancedPromptWorkflow
        output_dir: Directory to save the report
        
    Returns:
        Path to generated PDF
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename from query
    query = analysis_result.get('query_analysis', {}).get('original_question', 'analysis')
    safe_filename = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in query)
    safe_filename = safe_filename[:50]  # Limit length
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"pharmasynapse_report_{safe_filename}_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    generator = PromptReportGenerator()
    generator.generate_report(analysis_result, output_path)
    
    return output_path

