"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { BarChart3, TrendingUp, FileText, Globe, Zap, Target, CheckCircle, XCircle, Clock, Download, Brain, Database, Activity, ArrowRight, Sparkles, Printer } from "lucide-react";
import toast, { Toaster } from "react-hot-toast";
import { BeatLoader } from "react-spinners";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell } from "recharts";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

// --- Types ---

type AnalysisResult = {
  molecule: string;
  disease?: string | null;
  region?: string | null;
  synthesis?: {
    executive_summary: string;
    strategic_recommendations: Array<{
      priority?: number;
      action?: string;
      rationale?: string;
      next_steps?: string;
      timeline?: string;
      investment?: string;
    }>;
    swot: {
      strengths: string[];
      weaknesses: string[];
      opportunities: string[];
      threats: string[];
    };
    key_insights: {
      market: string;
      clinical: string;
      patent: string;
      supply_chain: string;
    };
  };
  iqvia?: IQVIAResult;
  patents?: PatentResult;
  trials?: TrialsResult;
  web?: WebResult;
  exim?: EximResult;
  internal?: InternalResult;
};

// NEW: Workflow result types for prompt-based analysis
type AgentOutput = {
  available?: boolean;
  summary?: string;
  overview?: Record<string, unknown>;
  [key: string]: unknown;
};

type DecisionFramework = {
  confidence_level?: string;
  key_success_factors?: string[];
  deal_breakers?: string[];
  data_gaps?: string[];
  [key: string]: unknown;
};

type StrategicOpportunityOutput = {
  opportunity_type?: string;
  innovation_story?: string;
  executive_summary?: string;
  flexible_sections?: Array<{ heading: string; content: string }>;
  feasibility_score?: number;
  key_insights?: string[];
  recommendations?: Array<{
    priority?: number;
    action?: string;
    rationale?: string;
    next_steps?: string;
    timeline?: string;
    investment?: string;
  }>;
  unmet_needs?: string[];
  decision_framework?: DecisionFramework;
  go_no_go_recommendation?: string;
  [key: string]: unknown;
};

type WorkflowResult = {
  success: boolean;
  query_intent: QueryIntent;
  results: {
    agent_outputs: Record<string, AgentOutput | StrategicOpportunityOutput>;
    execution_log: ExecutionLogEntry[];
    summary: string;
    execution_time_seconds: number;
  };
  execution_time_seconds: number;
  message?: string;
};

type QueryIntent = {
  intent_type: string;
  primary_entity?: string | null;
  disease_area?: string | null;
  geography?: string | null;
  strategic_question?: string | null;
  is_structured_input: boolean;
  workflow_stages: string[];
  confidence: number;
};

type ExecutionLogEntry = {
  stage: string;
  status: string;
  timestamp: string;
  has_data: boolean;
};

type RegionData = {
  market_size_usd_mn?: number;
  cagr_5y_percent?: number;
  competitors?: { company: string; share_percent: number }[];
  volume_trend?: string;
};

type IQVIAResult = {
  molecule?: string;
  atc_class?: string;
  regions?: Record<string, RegionData>;
  therapy_dynamics?: string[];
  sales_trends?: { year: number; revenue_usd_mn: number }[];
  volume_shifts?: { channel: string; delta_percent: number }[];
  therapy_competition?: { therapy_area: string; key_players: string[]; price_pressure: string }[];
  summary?: string;
  message?: string;
};

type PatentItem = {
  patent_number?: string;
  title?: string;
  assignee?: string;
  jurisdiction?: string;
  status?: string;
  expiry_date?: string;
  family_id?: string;
  focus?: string;
  fto_risk?: string;
};

type PatentResult = {
  patents?: PatentItem[];
  overview?: {
    total?: number;
    active_count?: number;
    expired_count?: number;
    pending_count?: number;
  };
  status_table?: { status: string; count: number }[];
  filing_heatmap?: Record<string, Record<string, number>>;
  summary?: string;
  message?: string;
};

type TrialsResult = {
  trials?: { trial_id?: string; phase?: string; status?: string; condition?: string; sponsor?: string }[];
  overview?: {
    phase_distribution?: Record<string, number>;
    status_distribution?: Record<string, number>;
    trials_in_scope?: number;
    total_trials_for_molecule?: number;
  };
  sponsor_profiles?: { sponsor: string; trials: number; focus?: string; regions?: string[] }[];
  summary?: string;
  message?: string;
};

type EximResult = {
  exports?: { country: string; year: number; volume_tons?: number; value_usd_mn?: number }[];
  imports?: { country: string; year: number; volume_tons?: number; value_usd_mn?: number }[];
  overview?: {
    total_export_value_usd_mn?: number;
    total_import_value_usd_mn?: number;
    total_export_volume_tons?: number;
    total_import_volume_tons?: number;
  };
  import_dependency?: { country: string; year?: number; value_usd_mn?: number; volume_tons?: number; share_percent?: number }[];
  insights?: string[];
  sourcing_insights?: string[];
  summary?: string;
  message?: string;
};

type WebResult = {
  guidelines?: { title?: string; url?: string; snippet?: string }[];
  rwe?: { title?: string; url?: string; snippet?: string }[];
  news?: { title?: string; url?: string; snippet?: string }[];
  regulatory?: { title?: string; url?: string; snippet?: string }[];
  publications?: { title?: string; url?: string; snippet?: string }[];
  market_news?: { title?: string; url?: string; snippet?: string }[];
  summary?: string;
  message?: string;
  as_of?: string;
};

type InternalDoc = { title?: string; type?: string; year?: number | null; pdf_url?: string; id?: string };
type InternalResult = {
  documents?: InternalDoc[];
  key_takeaways?: string[];
  comparative_tables?: unknown[];
  summary?: string;
  message?: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api";

export default function Home() {
  const [inputMode, setInputMode] = useState<"structured" | "prompt">("structured");

  // Structured input state
  const [form, setForm] = useState({
    molecule: "metformin",
    disease: "NAFLD",
    region: "US",
  });

  // Prompt input state
  const [prompt, setPrompt] = useState("");
  const [promptExamples] = useState([
    "Which respiratory diseases show low competition in India?",
    "Is metformin suitable for NAFLD repurposing?",
    "Analyze the patent landscape for diabetes drugs in US",
    "What are unmet needs in oncology?",
  ]);

  // Results
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [workflowResult, setWorkflowResult] = useState<WorkflowResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reportUrl, setReportUrl] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  const [agentProgress, setAgentProgress] = useState<{ [key: string]: { status: 'pending' | 'running' | 'completed', progress: number } }>({});

  // --- Handlers ---

  const handleChange = (field: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setWorkflowResult(null);
    setReportUrl(null);

    // Initialize agent progress
    const agents = ['nlp_agent', 'iqvia_agent', 'clinical_trials_agent', 'patent_agent', 'exim_agent'];
    const initialProgress: { [key: string]: { status: 'pending' | 'running' | 'completed', progress: number } } = {};
    agents.forEach(agent => {
      initialProgress[agent] = { status: 'pending', progress: 0 };
    });
    setAgentProgress(initialProgress);

    // Advanced Simulation Logic for Structured Mode
    let progressInterval: NodeJS.Timeout | null = null;

    if (inputMode === "structured") {
      // Individual progress trackers
      const agentStates = agents.map(agent => ({
        id: agent,
        progress: 0,
        speed: Math.random() * 2 + 0.5, // Random speed
        max: Math.floor(Math.random() * 15) + 80, // Random stop point between 80-95%
        delay: Math.random() * 2000 // Random start delay
      }));

      const startTime = Date.now();

      progressInterval = setInterval(() => {
        const now = Date.now();
        setAgentProgress((prev) => {
          const nextState = { ...prev };

          agentStates.forEach((agentState, idx) => {
            // Staggered start logic
            const shouldStart = (idx === 0) || (now - startTime > agentState.delay) || (idx > 0 && nextState[agentStates[idx - 1].id].progress > 30);

            if (nextState[agentState.id].status === 'pending' && shouldStart) {
              nextState[agentState.id].status = 'running';
            }

            if (nextState[agentState.id].status === 'running') {
              // Simulate work with two phases: Fast Ramp -> Slow Crawl
              if (agentState.progress < agentState.max) {
                // Phase 1: Fast ramp up to random threshold (80-95%)
                agentState.progress += agentState.speed;
                // Add occasional random jumps
                if (Math.random() > 0.9) agentState.progress += 5;
              } else {
                // Phase 2: Slow crawl to keep UI alive (asymptotic to 99%)
                // This prevents the "static" feeling while waiting for API
                if (agentState.progress < 99) {
                  agentState.progress += 0.05;
                }
              }

              // Clamp to 99% max (100% is set only when API returns)
              if (agentState.progress > 99) agentState.progress = 99;

              nextState[agentState.id].progress = agentState.progress;
            }
          });

          return nextState;
        });
      }, 100);
    }

    const loadingToast = toast.loading(
      inputMode === "prompt"
        ? "🤖 AI analyzing your strategic question..."
        : "🚀 Initiating multi-agent analysis...",
      {
        duration: 30000,
        style: {
          background: 'rgba(0, 0, 0, 0.8)',
          color: '#fff',
          borderRadius: '10px'
        }
      }
    );

    try {
      let res;
      if (inputMode === "prompt" && prompt.trim()) {
        // AI-powered prompt analysis
        res = await fetch(`${API_BASE}/prompt/analyze-prompt`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: prompt.trim(), use_gemini: true }),
        });
        if (!res.ok) throw new Error(`AI Analysis failed: ${res.status}`);
        const data = await res.json();
        setWorkflowResult(data);
        setActiveTab("workflow");

        toast.success("✅ Strategic analysis complete!", {
          id: loadingToast,
          duration: 5000,
        });

      } else {
        // Structured molecule analysis
        res = await fetch(`${API_BASE}/analyze-molecule`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        });
        if (!res.ok) throw new Error(`Analysis failed: ${res.status}`);
        const data = await res.json();

        // Mark agents as completed only after successful return
        setAgentProgress((prev) => {
          const completed = { ...prev };
          Object.keys(completed).forEach(agent => {
            completed[agent] = { status: 'completed', progress: 100 };
          });
          return completed;
        });

        setResult(data);
        setActiveTab("dashboard");

        toast.success("✅ Analysis complete! Results ready.", {
          id: loadingToast,
          duration: 5000,
        });
      }

    } catch (e) {
      const msg = e instanceof Error ? e.message : "Analysis failed";
      setError(msg);
      toast.error(`❌ ${msg}`, {
        id: loadingToast,
        duration: 5000,
      });
    } finally {
      if (progressInterval) clearInterval(progressInterval);
      setLoading(false);
    }
  };

  const runReport = async () => {
    setError(null);
    setReportUrl(null);

    const loadingToast = toast.loading("📊 Generating comprehensive report...", {
      duration: 30000
    });

    try {
      if (workflowResult) {
        // Generate comprehensive detailed report
        const res = await fetch(`${API_BASE}/report/generate-comprehensive`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(workflowResult),
        });
        if (!res.ok) throw new Error(`Report generation failed: ${res.status}`);
        const data = await res.json();

        const url = data?.download_url ? `http://localhost:8000${data.download_url}` : null;
        setReportUrl(url);

        toast.success("📄 Comprehensive report generated successfully!", {
          id: loadingToast,
          duration: 5000,
        });
      } else {
        // Legacy report
        const res = await fetch(`${API_BASE}/report/generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        });
        if (!res.ok) throw new Error(`Report generation failed: ${res.status}`);
        const data = await res.json();

        const url = data?.report_pdf?.url
          ? data.report_pdf.url.startsWith("http")
            ? data.report_pdf.url
            : `${API_BASE.replace(/\/$/, "")}${data.report_pdf.url}`
          : null;
        setReportUrl(url);

        if (data?.analysis) setResult(data.analysis);

        toast.success("📄 Report generated successfully!", {
          id: loadingToast,
          duration: 5000,
        });
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Report generation failed";
      setError(msg);
      toast.error(`❌ ${msg}`, {
        id: loadingToast,
        duration: 5000,
      });
    }
  };

  const handleUpload = async (file: File | null) => {
    if (!file) return;
    setUploadStatus("Uploading...");
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${API_BASE}/internal/upload`, {
        method: "POST",
        body: fd,
      });
      if (!res.ok) throw new Error("Upload failed");
      const data = await res.json();
      setUploadStatus(`Uploaded: ${data.filename}`);
      toast.success("Document uploaded successfully!");
    } catch {
      setUploadStatus("Error uploading file");
      toast.error("Failed to upload document");
    }
  };

  const exportToPDF = async () => {
    const loadingToast = toast.loading("Generating PDF report...");

    try {
      // Generate server-side PDF first
      await runReport();

      // If server-side PDF is available, download it
      if (reportUrl) {
        // Create a temporary link to download the PDF
        const link = document.createElement('a');
        link.href = reportUrl;
        link.download = `pharma_analysis_${Date.now()}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        toast.success("PDF downloaded successfully!", { id: loadingToast });
      } else {
        // Fallback: Generate client-side PDF using html2canvas + jsPDF
        const element = document.querySelector('[data-pdf-content]') as HTMLElement;
        if (element) {
          const canvas = await html2canvas(element, {
            scale: 2,
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#0f0f23'
          });

          const imgData = canvas.toDataURL('image/png');
          const pdf = new jsPDF('p', 'mm', 'a4');

          const imgWidth = 210; // A4 width in mm
          const pageHeight = 295; // A4 height in mm
          const imgHeight = (canvas.height * imgWidth) / canvas.width;
          let heightLeft = imgHeight;

          let position = 0;

          pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
          heightLeft -= pageHeight;

          while (heightLeft >= 0) {
            position = heightLeft - imgHeight;
            pdf.addPage();
            pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
            heightLeft -= pageHeight;
          }

          pdf.save(`pharma_analysis_${Date.now()}.pdf`);
          toast.success("Client-side PDF generated successfully!", { id: loadingToast });
        } else {
          throw new Error("No content to export");
        }
      }
    } catch {
      toast.error("Failed to generate PDF", { id: loadingToast });
    }
  };

  // --- Render Components ---

  const renderInputSection = () => {
    return (
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="glass rounded-2xl shadow-2xl p-8 mb-12 border border-black/30 hover-lift"
      >
        {/* Hero Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="text-center mb-8"
        >
          <h2 className="text-3xl font-bold text-primary mb-3">
            Strategic Pharmaceutical Intelligence
          </h2>
          <p className="text-slate-600 text-lg max-w-2xl mx-auto">
            Harness the power of multi-agent AI to analyze markets, patents, clinical trials, and strategic opportunities in real-time
          </p>
        </motion.div>

        {/* Enhanced Input Mode Selector */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex gap-4 mb-8 justify-center"
        >
          <motion.button
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              setInputMode("structured");
              setResult(null);
              setWorkflowResult(null);
            }}
            className={`px-8 py-4 font-bold rounded-xl transition-all duration-300 flex items-center gap-3 ${inputMode === "structured"
              ? "btn-primary shadow-sm"
              : "glass hover:bg-black/10 border border-black/20 text-slate-800 hover:text-foreground"
              }`}
          >
            <Target className="w-5 h-5" />
            Quick Analysis
            <ArrowRight className="w-4 h-4" />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              setInputMode("prompt");
              setResult(null);
              setWorkflowResult(null);
            }}
            className={`px-8 py-4 font-bold rounded-xl transition-all duration-300 flex items-center gap-3 ${inputMode === "prompt"
              ? "btn-secondary shadow-sm"
              : "glass hover:bg-black/10 border border-black/20 text-slate-800 hover:text-foreground"
              }`}
          >
            <Brain className="w-5 h-5" />
            AI Strategic Prompt
            <Sparkles className="w-4 h-4" />
          </motion.button>
        </motion.div>

        <AnimatePresence mode="wait">
          {inputMode === "structured" ? (
            <motion.div
              key="structured"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.4 }}
              className="grid grid-cols-1 md:grid-cols-4 gap-6 items-end"
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="space-y-2"
              >
                <label className="block text-sm font-bold text-slate-800 uppercase tracking-wide">
                  Molecule
                </label>
                <input
                  className="w-full glass border border-black/30 rounded-xl px-4 py-3 text-foreground placeholder-slate-500 focus-ring bg-black/5 focus:bg-black/10 transition-all duration-300"
                  placeholder="e.g., metformin, aspirin"
                  value={form.molecule}
                  onChange={handleChange("molecule")}
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="space-y-2"
              >
                <label className="block text-sm font-bold text-slate-800 uppercase tracking-wide">
                  Disease/Indication
                </label>
                <input
                  className="w-full glass border border-black/30 rounded-xl px-4 py-3 text-foreground placeholder-slate-500 focus-ring bg-black/5 focus:bg-black/10 transition-all duration-300"
                  placeholder="e.g., NAFLD, diabetes"
                  value={form.disease}
                  onChange={handleChange("disease")}
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="space-y-2"
              >
                <label className="block text-sm font-bold text-slate-800 uppercase tracking-wide">
                  Geography
                </label>
                <input
                  className="w-full glass border border-black/30 rounded-xl px-4 py-3 text-foreground placeholder-slate-500 focus-ring bg-black/5 focus:bg-black/10 transition-all duration-300"
                  placeholder="e.g., US, India, Global"
                  value={form.region}
                  onChange={handleChange("region")}
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="flex gap-3"
              >
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={runAnalysis}
                  disabled={loading}
                  className="flex-1 btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <BeatLoader size={8} color="#ffffff" />
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Zap className="w-5 h-5" />
                      <span>Launch Analysis</span>
                    </>
                  )}
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={exportToPDF}
                  disabled={loading}
                  className="px-6 py-3 glass border border-black/30 rounded-xl text-slate-800 hover:text-foreground font-semibold hover:bg-black/10 transition-all duration-300 disabled:opacity-50 flex items-center gap-2"
                >
                  <Printer className="w-5 h-5" />
                  <span>PDF</span>
                </motion.button>
              </motion.div>

              <div className="col-span-1 md:col-span-4 mt-2 flex flex-wrap items-center gap-3">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">Popular Examples:</span>
                <button
                  type="button"
                  onClick={() => setForm({ molecule: 'Metformin', disease: 'NAFLD', region: 'US' })}
                  className="px-3 py-1 rounded-full bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200 hover:bg-white hover:border-primary hover:text-primary transition-colors cursor-pointer"
                >
                  Metformin (NAFLD)
                </button>
                <button
                  type="button"
                  onClick={() => setForm({ molecule: 'Keytruda', disease: 'Lung Cancer', region: 'Global' })}
                  className="px-3 py-1 rounded-full bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200 hover:bg-white hover:border-primary hover:text-primary transition-colors cursor-pointer"
                >
                  Keytruda (Oncology)
                </button>
                <button
                  type="button"
                  onClick={() => setForm({ molecule: 'Humira', disease: 'Rheumatoid Arthritis', region: 'EU5' })}
                  className="px-3 py-1 rounded-full bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200 hover:bg-white hover:border-primary hover:text-primary transition-colors cursor-pointer"
                >
                  Humira (RA)
                </button>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="prompt"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.4 }}
              className="space-y-6"
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="space-y-3"
              >
                <label className="block text-lg font-bold text-foreground">
                  Strategic Question
                </label>
                <textarea
                  className="w-full glass border border-black/30 rounded-xl px-6 py-4 text-foreground placeholder-slate-500 focus-ring bg-black/5 focus:bg-black/10 transition-all duration-300 resize-none text-lg"
                  rows={4}
                  placeholder="Ask any strategic pharmaceutical question..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="flex gap-3 flex-wrap items-center"
              >
                <span className="text-sm font-semibold text-slate-600">Try these examples:</span>
                {promptExamples.map((ex, i) => (
                  <motion.button
                    key={i}
                    whileHover={{ scale: 1.05, y: -1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setPrompt(ex)}
                    className="text-sm px-4 py-2 glass border border-black/20 text-slate-800 hover:text-foreground rounded-full hover:bg-black/10 transition-all duration-300"
                  >
                    {ex}
                  </motion.button>
                ))}
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="flex gap-4"
              >
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={runAnalysis}
                  disabled={loading || !prompt.trim()}
                  className="flex-1 btn-secondary flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <BeatLoader size={8} color="#ffffff" />
                      <span>AI Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Brain className="w-6 h-6" />
                      <span>🚀 Launch AI Analysis</span>
                    </>
                  )}
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={exportToPDF}
                  disabled={loading}
                  className="px-8 py-4 glass border-2 border-black/30 rounded-xl text-foreground font-bold hover:bg-black/10 transition-all duration-300 disabled:opacity-50 flex items-center gap-3"
                >
                  <Printer className="w-5 h-5" />
                  <span>Export PDF Report</span>
                </motion.button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 pt-6 border-t border-black/20 flex items-center justify-between"
        >
          <motion.div
            className="flex items-center gap-4"
            whileHover={{ scale: 1.02 }}
          >
            <Database className="w-5 h-5 text-slate-600" />
            <span className="text-slate-600 font-medium">Internal Knowledge Base:</span>
            <motion.label
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="cursor-pointer text-primary hover:text-secondary font-bold underline decoration-2 underline-offset-2"
            >
              Upload PDF Document
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={(e) => handleUpload(e.target.files?.[0] || null)}
              />
            </motion.label>
            {uploadStatus && (
              <motion.span
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-slate-400 text-sm ml-2 px-2 py-1 bg-white/10 rounded-full"
              >
                {uploadStatus}
              </motion.span>
            )}
          </motion.div>

          <AnimatePresence>
            {reportUrl && (
              <motion.a
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                href={reportUrl}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 text-success font-bold hover:text-foreground px-4 py-2 rounded-xl bg-success/20 hover:bg-success/30 transition-all duration-300"
              >
                <Download className="w-5 h-5" />
                <span>Download Comprehensive Report</span>
              </motion.a>
            )}
          </AnimatePresence>
        </motion.div>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-6 p-4 bg-red-500/20 border border-red-500/30 text-red-700 rounded-xl flex items-center gap-3"
            >
              <XCircle className="w-5 h-5 flex-shrink-0" />
              <span className="font-medium">{error}</span>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.section>
    );
  };

  const renderWorkflowView = (): React.JSX.Element | null => {
    if (!workflowResult) return null;

    const workflowResultTyped = workflowResult as WorkflowResult;
    const { query_intent, results } = workflowResultTyped;

    if (!results) return null;
    const strategic = (results.agent_outputs?.strategic_opportunity || {}) as StrategicOpportunityOutput;

    return (
      <motion.div key="workflow-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="space-y-8"
      >
        {/* Enhanced Query Intent Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1, duration: 0.5 }}
          className="glass rounded-2xl p-8 border border-black/20 shadow-2xl"
        >
          <motion.h3
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent mb-6 flex items-center gap-3"
          >
            <Brain className="w-7 h-7" />
            AI Query Analysis
          </motion.h3>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm"
          >
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="p-4 glass rounded-xl border border-black/20 bg-black/5"
            >
              <span className="text-slate-600 block mb-2 uppercase tracking-wide text-xs font-bold">Intent Type</span>
              <span className="font-bold text-foreground text-lg capitalize">{query_intent.intent_type.replace("_", " ")}</span>
            </motion.div>

            {query_intent.primary_entity && (
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="p-4 glass rounded-xl border border-black/20 bg-black/5"
              >
                <span className="text-slate-600 block mb-2 uppercase tracking-wide text-xs font-bold">Molecule</span>
                <span className="font-bold text-success text-lg">{query_intent.primary_entity}</span>
              </motion.div>
            )}

            {query_intent.disease_area && (
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="p-4 glass rounded-xl border border-black/20 bg-black/5"
              >
                <span className="text-slate-600 block mb-2 uppercase tracking-wide text-xs font-bold">Disease Area</span>
                <span className="font-bold text-warning text-lg">{query_intent.disease_area}</span>
              </motion.div>
            )}

            {query_intent.geography && (
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="p-4 glass rounded-xl border border-black/20 bg-black/5"
              >
                <span className="text-slate-600 block mb-2 uppercase tracking-wide text-xs font-bold">Geography</span>
                <span className="font-bold text-accent text-lg">{query_intent.geography}</span>
              </motion.div>
            )}
          </motion.div>

          {query_intent.strategic_question && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mt-8 pt-6 border-t border-black/20"
            >
              <span className="text-slate-600 text-sm block mb-4 uppercase tracking-wide font-bold">Original Strategic Question:</span>
              <div className="p-6 bg-gradient-to-r from-primary/20 via-secondary/20 to-accent/20 rounded-xl border border-black/30">
                <p className="text-foreground text-lg font-medium italic leading-relaxed">
                  &ldquo;{query_intent.strategic_question}&rdquo;
                </p>
              </div>
            </motion.div>
          )}
        </motion.div>


        {/* Enhanced Decision Framework - MOST IMPORTANT */}
        {strategic.decision_framework && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.6, type: "spring" }}
            className="relative glass rounded-3xl p-8 border-2 border-success/50 shadow-glow-success overflow-hidden"
          >
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-success/10 via-primary/5 to-secondary/10 rounded-3xl"></div>

            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="relative z-10"
            >
              <h3 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-success via-primary to-secondary mb-6 flex items-center gap-4">
                <Target className="w-8 h-8 text-success" />
                Strategic Decision Framework
              </h3>

              {/* Main Recommendation */}
              {strategic.go_no_go_recommendation && typeof strategic.go_no_go_recommendation === 'string' && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.6, type: "spring" }}
                  className="mb-8 p-8 bg-gradient-to-r from-success/20 via-primary/10 to-secondary/20 rounded-2xl border-2 border-success/30 shadow-lg"
                >
                  <div className="text-center">
                    <motion.div
                      animate={{
                        scale: strategic.go_no_go_recommendation.toUpperCase() === "YES" ? [1, 1.1, 1] : [1],
                        rotate: strategic.go_no_go_recommendation.toUpperCase() === "YES" ? [0, 5, -5, 0] : [0]
                      }}
                      transition={{
                        duration: 2,
                        repeat: strategic.go_no_go_recommendation.toUpperCase() === "YES" ? Infinity : 0,
                        ease: "easeInOut"
                      }}
                      className="text-sm font-bold text-slate-600 mb-3 uppercase tracking-widest"
                    >
                      Strategic Recommendation
                    </motion.div>
                    <motion.div
                      initial={{ scale: 0.5, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ delay: 0.8, type: "spring" }}
                      className={`text-5xl font-black mb-4 ${strategic.go_no_go_recommendation.toUpperCase() === "YES"
                        ? "text-success drop-shadow-lg"
                        : strategic.go_no_go_recommendation.toUpperCase() === "NO"
                          ? "text-red-400"
                          : "text-warning"
                        }`}
                    >
                      {strategic.go_no_go_recommendation.toUpperCase()}
                    </motion.div>
                    <div className="text-lg text-slate-800 font-medium">
                      {strategic.go_no_go_recommendation.toUpperCase() === "YES"
                        ? "Proceed with confidence - strong strategic fit identified"
                        : strategic.go_no_go_recommendation.toUpperCase() === "NO"
                          ? "Strategic concerns identified - reassess opportunity"
                          : "Further analysis required - mixed signals detected"
                      }
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Confidence Level */}
              {strategic.decision_framework && strategic.decision_framework.confidence_level && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.7 }}
                  className="mb-6 flex items-center gap-4"
                >
                  <span className="text-lg font-bold text-foreground">Analysis Confidence:</span>
                  <motion.span
                    whileHover={{ scale: 1.05 }}
                    className={`px-6 py-3 rounded-full text-lg font-black border-2 ${strategic.decision_framework.confidence_level === 'HIGH'
                      ? 'bg-success/20 text-success border-success/50 shadow-glow-success'
                      : strategic.decision_framework.confidence_level === 'LOW'
                        ? 'bg-red-500/20 text-red-700 border-red-500/50'
                        : 'bg-warning/20 text-warning border-warning/50 shadow-glow-warning'
                      }`}
                  >
                    {strategic.decision_framework.confidence_level}
                  </motion.span>
                </motion.div>
              )}

              {/* Success Factors & Deal Breakers */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="grid grid-cols-1 gap-6"
              >
                {strategic.decision_framework.key_success_factors && Array.isArray(strategic.decision_framework.key_success_factors) && strategic.decision_framework.key_success_factors.length > 0 && (
                  <motion.div
                    whileHover={{ scale: 1.02, y: -2 }}
                    className="glass p-6 rounded-2xl border border-success/30 bg-success/10"
                  >
                    <h4 className="font-bold text-success mb-4 flex items-center gap-2 text-lg">
                      <CheckCircle className="w-6 h-6" />
                      Success Factors
                    </h4>
                    <ul className="space-y-3">
                      {strategic.decision_framework.key_success_factors.map((factor: string, i: number) => (
                        <motion.li
                          key={i}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.1 + 0.9 }}
                          className="flex items-start gap-3 text-slate-800"
                        >
                          <span className="text-success mt-1 flex-shrink-0">✓</span>
                          <span className="leading-relaxed">{factor}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </motion.div>
                )}

                {strategic.decision_framework.deal_breakers && Array.isArray(strategic.decision_framework.deal_breakers) && strategic.decision_framework.deal_breakers.length > 0 && (
                  <motion.div
                    whileHover={{ scale: 1.02, y: -2 }}
                    className="glass p-6 rounded-2xl border border-red-400/30 bg-red-500/10"
                  >
                    <h4 className="font-bold text-red-700 mb-4 flex items-center gap-2 text-lg">
                      <XCircle className="w-6 h-6" />
                      Critical Concerns
                    </h4>
                    <ul className="space-y-3">
                      {strategic.decision_framework.deal_breakers.map((breaker: string, i: number) => (
                        <motion.li
                          key={i}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.1 + 1.0 }}
                          className="flex items-start gap-3 text-slate-800"
                        >
                          <span className="text-red-400 mt-1 flex-shrink-0">⚠️</span>
                          <span className="leading-relaxed">{breaker}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </motion.div>
                )}
              </motion.div>

              {/* Data Gaps */}
              {strategic.decision_framework.data_gaps && Array.isArray(strategic.decision_framework.data_gaps) && strategic.decision_framework.data_gaps.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.1 }}
                  className="mt-6 glass p-6 rounded-2xl border border-primary/30 bg-primary/10"
                >
                  <h4 className="font-bold text-primary mb-4 flex items-center gap-2 text-lg">
                    <Database className="w-6 h-6" />
                    Additional Analysis Needed
                  </h4>
                  <ul className="space-y-2">
                    {strategic.decision_framework.data_gaps.map((gap: string, i: number) => (
                      <motion.li
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 + 1.2 }}
                        className="flex items-start gap-3 text-slate-800"
                      >
                        <span className="text-primary mt-1 flex-shrink-0">•</span>
                        <span className="leading-relaxed">{gap}</span>
                      </motion.li>
                    ))}
                  </ul>
                </motion.div>
              )}
            </motion.div>
          </motion.div>
        )}

        {/* Enhanced Answer Highlights */}
        {strategic.answer_highlights && Array.isArray(strategic.answer_highlights) && strategic.answer_highlights.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="glass rounded-2xl p-8 border border-primary/30 shadow-glow"
          >
            <motion.h3
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
              className="text-2xl font-bold text-primary mb-6 flex items-center gap-3"
            >
              <Sparkles className="w-7 h-7" />
              Key Strategic Insights
            </motion.h3>
            <div className="space-y-4">
              {strategic.answer_highlights.map((highlight: string, i: number) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 + 0.6, duration: 0.5 }}
                  whileHover={{ scale: 1.02, x: 5 }}
                  className="flex gap-4 items-start p-6 glass rounded-xl border border-black/20 bg-primary/5 hover:bg-primary/10 transition-all duration-300"
                >
                  <motion.span
                    animate={{ rotate: [0, 10, -10, 0] }}
                    transition={{ duration: 2, repeat: Infinity, delay: i * 0.5 }}
                    className="text-primary font-bold text-2xl mt-1 flex-shrink-0"
                  >
                    →
                  </motion.span>
                  <p className="text-foreground leading-relaxed text-lg font-medium">{highlight}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Executive Summary Card */}
        <div className="bg-primary/5 p-6 rounded-xl border border-primary/20 shadow-sm">
          <h3 className="text-xl font-bold text-primary mb-3">Executive Summary</h3>
          <p className="text-slate-700 leading-relaxed">{strategic.executive_summary}</p>
        </div>

        {/* Dynamic Flexible Sections */}
        {strategic.flexible_sections && strategic.flexible_sections.map((section: { heading: string; content: string }, i: number) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm"
          >
            <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
              {section.heading}
            </h3>
            <div className="prose prose-sm max-w-none text-slate-700 leading-relaxed whitespace-pre-wrap">
              {section.content}
            </div>
          </motion.div>
        ))}

        {/* Recommendations / Follow up */}
        {((strategic.recommendations && strategic.recommendations.length > 0) ||
          (strategic.decision_framework?.key_success_factors && strategic.decision_framework.key_success_factors.length > 0)) && (
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                🚀 Actionable Intelligence / Next Steps
              </h3>

              <div className="space-y-4">
                {/* Primary recommendations */}
                {strategic.recommendations && strategic.recommendations.map((rec: string | { action?: string; rationale?: string }, i: number) => (
                  <div key={i} className="flex gap-4 items-start p-4 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="font-bold text-primary text-xl">#{i + 1}</span>
                    <div>
                      <p className="font-bold text-slate-800">{typeof rec === 'string' ? rec : rec.action}</p>
                      {typeof rec !== 'string' && rec.rationale && (
                        <p className="text-sm text-slate-600 mt-1">{rec.rationale}</p>
                      )}
                    </div>
                  </div>
                ))}

                {/* Follow Up / Single Key Success Factor (mapped from follow_up_recommendation in backend) */}
                {strategic.decision_framework?.key_success_factors?.map((factor, i) => (
                  <div key={`followup-${i}`} className="mt-4 pt-4 border-t border-slate-100">
                    <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wide mb-2">Key Follow-Up</h4>
                    <p className="text-slate-700 font-medium leading-relaxed">{factor}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
      </motion.div>
    );
  };

  const renderDashboard = () => {
    if (!result?.synthesis) return <div className="p-4 text-slate-500">No synthesis data available.</div>;
    const { synthesis } = result;

    return (
      <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        {/* Executive Summary Card */}
        <div className="bg-gradient-to-br from-indigo-50 to-white p-6 rounded-xl border border-indigo-100 shadow-sm">
          <h3 className="text-xl font-bold text-indigo-900 mb-3">Executive Summary</h3>
          <p className="text-slate-700 leading-relaxed">{synthesis.executive_summary}</p>
        </div>

        {/* Recommendations */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
              🚀 Strategic Recommendations
            </h3>
            <ul className="space-y-2">
              {synthesis.strategic_recommendations.map((rec: string | { priority?: number; action?: string; rationale?: string; next_steps?: string; timeline?: string; investment?: string; }, i: number) => (
                <li key={i} className="flex items-start gap-2 text-slate-700">
                  <span className="text-indigo-500 mt-1">•</span>
                  {typeof rec === 'string' ? rec : rec.action || JSON.stringify(rec)}
                </li>
              ))}
            </ul>
          </div>

          {/* Key Insights Grid */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-lg font-bold text-slate-800 mb-4">Key Insights</h3>
            <div className="space-y-3">
              <InsightRow label="Market" value={synthesis.key_insights.market} color="bg-blue-100 text-blue-800" />
              <InsightRow label="Clinical" value={synthesis.key_insights.clinical} color="bg-emerald-100 text-emerald-800" />
              <InsightRow label="Patent" value={synthesis.key_insights.patent} color="bg-amber-100 text-amber-800" />
              <InsightRow label="Supply Chain" value={synthesis.key_insights.supply_chain} color="bg-purple-100 text-purple-800" />
            </div>
          </div>
        </div>

        {/* SWOT Analysis */}
        <div>
          <h3 className="text-xl font-bold text-slate-800 mb-4">SWOT Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SwotCard title="Strengths" items={synthesis.swot.strengths} type="strength" />
            <SwotCard title="Weaknesses" items={synthesis.swot.weaknesses} type="weakness" />
            <SwotCard title="Opportunities" items={synthesis.swot.opportunities} type="opportunity" />
            <SwotCard title="Threats" items={synthesis.swot.threats} type="threat" />
          </div>
        </div>

        {/* Data Highlights */}
        <div className="space-y-6">
          <h3 className="text-xl font-bold text-slate-800">Data Highlights</h3>

          {/* Top Tier: Market & Clinical */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <MarketHighlights iqvia={result.iqvia} />
            <TrialsHighlights trials={result.trials} />
          </div>

          {/* Middle Tier: Intelligence Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <PatentHighlights patents={result.patents} />
            <EximHighlights exim={result.exim} />

            {/* Full width Internal Knowledge */}
            <div className="lg:col-span-2">
              <InternalHighlights internal={result.internal} />
            </div>
          </div>

          {/* Bottom Tier: Web Intelligence (Full Width) */}
          <div className="w-full">
            <WebHighlights web={result.web} />
          </div>
        </div>
      </div>
    );
  };

  const renderDataView = () => {
    const data = workflowResult ? workflowResult.results.agent_outputs : result;
    if (!data) return null;

    const sections = Object.entries(data).map(([key, value]) => ({
      title: key.toUpperCase().replace("_", " "),
      data: value,
    }));

    return (
      <div className="space-y-6">
        {sections.map((sec, i) => (
          <div key={i} className="bg-white border rounded-lg p-5 shadow-sm">
            <h4 className="font-bold text-slate-700 mb-3 border-b pb-2">{sec.title}</h4>
            <pre className="bg-slate-50 p-3 rounded text-xs overflow-auto max-h-60">
              {JSON.stringify(sec.data, null, 2)}
            </pre>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen font-sans text-foreground">
      {/* Enhanced Navbar */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="glass sticky top-0 z-50 border-b border-black/20"
      >
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <motion.div
            className="flex items-center gap-4"
            whileHover={{ scale: 1.02 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary font-bold text-xl border border-primary/20">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                PharmaSynapse
              </h1>
              <p className="text-xs text-slate-500">AI-Powered Strategic Intelligence</p>
            </div>
          </motion.div>

          <div className="flex items-center gap-6">
            <motion.div
              className="flex items-center gap-2 text-sm text-slate-600"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <Activity className="w-4 h-4 text-success" />
              <span>v3.0</span>
            </motion.div>
            <motion.div
              className="flex items-center gap-1 text-xs text-slate-500"
              whileHover={{ scale: 1.05 }}
            >
              <Sparkles className="w-3 h-3" />
              <span>Multi-Agent AI</span>
            </motion.div>
          </div>
        </div>
      </motion.nav>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Input Section */}
        {renderInputSection()}

        {/* Real-time Progress Indicator */}
        <AnimatePresence>
          {loading && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="glass rounded-2xl p-8 border border-black/20 shadow-2xl mb-8"
            >
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-8"
              >
                <h3 className="text-2xl font-bold text-primary mb-2">
                  {inputMode === "prompt" ? "Analyzing Strategic Query..." : "Multi-Agent Analysis in Progress"}
                </h3>
                <p className="text-slate-600">AI agents are working together to provide comprehensive insights</p>
              </motion.div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Agent Grid - Only show for Structured/Molecule mode */}
                {inputMode !== "prompt" && Object.entries(agentProgress).map(([agent, progress], i) => (
                  <motion.div
                    key={agent}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="glass p-4 rounded-xl border border-black/20 bg-black/5"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-slate-800 font-semibold text-sm capitalize">
                        {agent.replace('_', ' ')}
                      </span>
                      <div className={`w-3 h-3 rounded-full ${progress.status === 'completed' ? 'bg-success animate-pulse-glow' :
                        progress.status === 'running' ? 'bg-primary animate-pulse' :
                          'bg-slate-500'
                        }`} />
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-xs text-slate-500">
                        <span>Progress</span>
                        <span>{Math.round(progress.progress)}%</span>
                      </div>
                      <div className="w-full bg-white/20 rounded-full h-2">
                        <motion.div
                          className={`h-2 rounded-full ${progress.status === 'completed' ? 'bg-success' :
                            progress.status === 'running' ? 'bg-primary' :
                              'bg-slate-500'
                            }`}
                          initial={{ width: 0 }}
                          animate={{ width: `${progress.progress}%` }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                    </div>

                    <div className="mt-2 text-xs text-slate-500">
                      {progress.status === 'completed' ? '✅ Complete' :
                        progress.status === 'running' ? '🔄 Processing...' :
                          '⏳ Waiting...'}
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Simple Loader for Prompt Mode */}
              {inputMode === "prompt" && (
                <div className="flex flex-col items-center justify-center py-12 space-y-6">
                  <div className="relative">
                    <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center animate-pulse">
                      <Brain className="w-10 h-10 text-primary" />
                    </div>
                    <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-success rounded-full border-4 border-white flex items-center justify-center shadow-sm">
                      <Sparkles className="w-4 h-4 text-white animate-spin-slow" />
                    </div>
                  </div>
                  <div className="text-center space-y-2">
                    <h3 className="font-bold text-xl text-slate-800">LLM Agent Running</h3>
                    <p className="text-sm text-slate-500 max-w-xs mx-auto">Synthesizing strategic intelligence from multiple sources. This usually takes 10-20 seconds.</p>
                  </div>
                </div>
              )}

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 }}
                className="text-center mt-8"
              >
                <div className="inline-flex items-center gap-2 text-slate-600">
                  <Brain className="w-5 h-5 animate-pulse" />
                  <span>AI agents collaborating for optimal results...</span>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Content Area */}
        <AnimatePresence mode="wait">
          {(result || workflowResult) && !loading ? (
            <motion.div
              key="results"
              data-pdf-content
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="space-y-8"
            >
              {/* Enhanced Tabs */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="flex glass rounded-2xl p-2 border border-black/20"
              >
                {workflowResult && (
                  <TabButton
                    active={activeTab === "workflow"}
                    onClick={() => setActiveTab("workflow")}
                  >
                    <Brain className="w-5 h-5" />
                    AI Strategic Report
                  </TabButton>
                )}

                {!workflowResult && (
                  <TabButton active={activeTab === "dashboard"} onClick={() => setActiveTab("dashboard")}>
                    <BarChart3 className="w-5 h-5" />
                    AI Report
                  </TabButton>
                )}

                <TabButton active={activeTab === "data"} onClick={() => setActiveTab("data")}>
                  <Database className="w-5 h-5" />
                  Raw Data
                </TabButton>
              </motion.div>

              <AnimatePresence mode="wait">
                {activeTab === "workflow" && workflowResult && (
                  <motion.div
                    key="workflow"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.4 }}
                  >
                    {renderWorkflowView()}
                  </motion.div>
                )}
                {activeTab === "dashboard" && (
                  <motion.div
                    key="dashboard"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.4 }}
                  >
                    {renderDashboard()}
                  </motion.div>
                )}
                {activeTab === "data" && (
                  <motion.div
                    key="data"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.4 }}
                  >
                    {renderDataView()}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ) : (
            !loading && (
              <motion.div
                key="empty"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.5 }}
                className="text-center py-32"
              >
                <motion.div
                  animate={{
                    scale: [1, 1.1, 1],
                    rotate: [0, 5, -5, 0]
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className="mb-8 text-8xl opacity-20"
                >
                  💊
                </motion.div>
                <motion.h3
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="text-2xl font-bold text-slate-600 mb-4"
                >
                  {inputMode === "prompt"
                    ? "Ready for Strategic Intelligence"
                    : "Ready for Molecule Analysis"}
                </motion.h3>
                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-lg text-slate-600 mb-6 max-w-2xl mx-auto leading-relaxed"
                >
                  {inputMode === "prompt"
                    ? "Ask any strategic pharmaceutical question and let our AI-powered multi-agent system provide comprehensive insights with real-time data from patents, clinical trials, markets, and web intelligence."
                    : "Enter molecule details to unleash the power of multi-agent pharmaceutical intelligence with IQVIA market data, PatentsView IP analysis, and regulatory insights."}
                </motion.p>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="flex flex-wrap justify-center gap-4 mb-6"
                >
                  <div className="flex items-center gap-2 text-sm text-slate-600 bg-black/5 px-3 py-2 rounded-full">
                    <Brain className="w-4 h-4 text-primary" />
                    <span>AI-Powered Analysis</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-slate-600 bg-black/5 px-3 py-2 rounded-full">
                    <Database className="w-4 h-4 text-secondary" />
                    <span>Multi-Agent System</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-slate-600 bg-black/5 px-3 py-2 rounded-full">
                    <BarChart3 className="w-4 h-4 text-accent" />
                    <span>Real-time Data</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-slate-600 bg-black/5 px-3 py-2 rounded-full">
                    <FileText className="w-4 h-4 text-success" />
                    <span>PDF Reports</span>
                  </div>
                </motion.div>

                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="text-sm text-slate-500 bg-primary/10 border border-primary/20 rounded-lg px-4 py-3 inline-block"
                >
                  💡 <strong>Example:</strong> {inputMode === "prompt"
                    ? "'Which respiratory diseases show low competition in India?'"
                    : "metformin for NAFLD in US"}
                </motion.p>
              </motion.div>
            )
          )}
        </AnimatePresence>
      </div>

      {/* Toast Notifications */}
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: 'rgba(0, 0, 0, 0.8)',
            color: '#ffffff',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
          },
          success: {
            icon: '🎉',
          },
          error: {
            icon: '❌',
          },
          loading: {
            icon: '⏳',
          },
        }}
      />
    </div>
  );
}

// --- Enhanced Subcomponents ---

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`flex-1 px-6 py-4 font-bold text-sm rounded-xl transition-all duration-300 flex items-center justify-center gap-3 ${active
        ? "bg-primary text-white shadow-sm"
        : "text-slate-600 hover:text-foreground hover:bg-black/10"
        }`}
    >
      {children}
    </motion.button>
  );
}

function InsightRow({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -1 }}
      className="flex items-start gap-4 p-4 rounded-xl glass border border-black/20 hover:bg-black/10 transition-all duration-300"
    >
      <span className={`text-xs font-bold px-3 py-2 rounded-lg uppercase tracking-wider ${color} min-w-24 text-center shrink-0 shadow-lg`}>
        {label}
      </span>
      <p className="text-sm text-slate-800 leading-relaxed flex-1">{value}</p>
    </motion.div>
  );
}

function SwotCard({ title, items, type }: { title: string; items: string[]; type: "strength" | "weakness" | "opportunity" | "threat" }) {
  const configs = {
    strength: {
      bg: "bg-success/10",
      border: "border-success/30",
      text: "text-success",
      icon: "💪"
    },
    weakness: {
      bg: "bg-error/10",
      border: "border-error/30",
      text: "text-error",
      icon: "⚠️"
    },
    opportunity: {
      bg: "bg-primary/10",
      border: "border-primary/30",
      text: "text-primary",
      icon: "🚀"
    },
    threat: {
      bg: "bg-warning/10",
      border: "border-warning/30",
      text: "text-warning",
      icon: "⚡"
    },
  };

  const config = configs[type];

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className={`p-6 rounded-2xl border ${config.bg} ${config.border} hover-lift`}
    >
      <h4 className={`font-bold mb-4 uppercase text-sm tracking-wide flex items-center gap-2 ${config.text}`}>
        <span className="text-lg">{config.icon}</span>
        {title}
      </h4>
      <ul className="space-y-3">
        {items.map((item, i) => (
          <motion.li
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="text-sm flex items-start gap-3 text-slate-800"
          >
            <span className="mt-1 opacity-60 text-primary">•</span>
            <span className="leading-relaxed">{item}</span>
          </motion.li>
        ))}
      </ul>
    </motion.div>
  );
}

// --- Highlight sections (keeping existing components) ---

function MarketHighlights({ iqvia }: { iqvia?: IQVIAResult }) {
  if (!iqvia) return null;
  const regions = iqvia.regions || {};
  const regionEntries = Object.entries(regions);

  // Prepare chart data
  const chartData = regionEntries.map(([name, r]) => ({
    name: name.length > 10 ? name.substring(0, 10) + "..." : name,
    marketSize: r?.market_size_usd_mn || 0,
    cagr: r?.cagr_5y_percent || 0,
    competitors: r?.competitors ? r.competitors.length : 0
  }));

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className="glass rounded-2xl p-6 border border-black/20 space-y-6 h-fit"
    >
      <h4 className="font-bold text-foreground flex items-center gap-3 text-lg">
        <BarChart3 className="w-6 h-6 text-primary" />
        Market Intelligence (IQVIA)
      </h4>

      {/* Market Size Chart */}
      {chartData.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-4"
        >
          <h5 className="font-semibold text-slate-600 text-sm uppercase tracking-wide">Market Size by Region</h5>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis
                  dataKey="name"
                  stroke="#94a3b8"
                  fontSize={12}
                  tick={{ fill: '#94a3b8' }}
                />
                <YAxis
                  stroke="#94a3b8"
                  fontSize={12}
                  tick={{ fill: '#94a3b8' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    color: '#ffffff'
                  }}
                  formatter={(value) => [`$${value}M`, 'Market Size']}
                />
                <Bar dataKey="marketSize" fill="#667eea" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      )}

      {/* Data Table */}
      {regionEntries.length > 0 && (
        <div className="overflow-hidden rounded-xl border border-black/10">
          <table className="w-full text-sm">
            <thead className="bg-white/10">
              <tr className="text-left text-slate-600">
                <th className="p-4 font-bold">Region</th>
                <th className="p-4 font-bold">Market Size</th>
                <th className="p-4 font-bold">CAGR</th>
                <th className="p-4 font-bold">Competitors</th>
              </tr>
            </thead>
            <tbody>
              {regionEntries.map(([name, r], i) => (
                <motion.tr
                  key={name}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="border-t border-black/10 hover:bg-black/5 transition-colors"
                >
                  <td className="p-4 text-foreground font-medium">{name}</td>
                  <td className="p-4 text-success font-bold">${r?.market_size_usd_mn ?? "?"}M</td>
                  <td className="p-4 text-warning font-bold">{r?.cagr_5y_percent ?? "?"}%</td>
                  <td className="p-4 text-slate-600">{r?.competitors ? r.competitors.length : 0}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {iqvia.summary && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 p-4 bg-primary/20 rounded-xl border border-primary/30"
        >
          <p className="text-slate-800 text-sm leading-relaxed">{iqvia.summary}</p>
        </motion.div>
      )}
    </motion.div>
  );
}

function PatentHighlights({ patents }: { patents?: PatentResult }) {
  if (!patents) return null;

  const overview = patents.overview || {};

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className="glass rounded-2xl p-6 border border-black/20 space-y-4 h-full"
    >
      <h4 className="font-bold text-foreground flex items-center gap-3 text-lg">
        <FileText className="w-6 h-6 text-secondary" />
        Patent Landscape (PatentsView)
      </h4>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="text-center p-4 bg-white/10 rounded-xl border border-black/20"
        >
          <div className="text-2xl font-bold text-success">{overview.total || 0}</div>
          <div className="text-xs text-slate-600 uppercase tracking-wide">Total Patents</div>
        </motion.div>
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="text-center p-4 bg-white/10 rounded-xl border border-black/20"
        >
          <div className="text-2xl font-bold text-primary">{overview.active_count || 0}</div>
          <div className="text-xs text-slate-600 uppercase tracking-wide">Active</div>
        </motion.div>
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="text-center p-4 bg-white/10 rounded-xl border border-black/20"
        >
          <div className="text-2xl font-bold text-warning">{overview.expired_count || 0}</div>
          <div className="text-xs text-slate-600 uppercase tracking-wide">Expired</div>
        </motion.div>
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="text-center p-4 bg-white/10 rounded-xl border border-black/20"
        >
          <div className="text-2xl font-bold text-accent">{overview.pending_count || 0}</div>
          <div className="text-xs text-slate-600 uppercase tracking-wide">Pending</div>
        </motion.div>
      </div>

      {patents.summary && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-4 bg-secondary/20 rounded-xl border border-secondary/30"
        >
          <p className="text-slate-800 text-sm leading-relaxed">{patents.summary}</p>
        </motion.div>
      )}
    </motion.div>
  );
}

function TrialsHighlights({ trials }: { trials?: TrialsResult }) {
  if (!trials) return null;
  const phase = trials.overview?.phase_distribution || {};
  const status = trials.overview?.status_distribution || {};

  // Prepare chart data
  const phaseChartData = Object.entries(phase).map(([phaseName, count]) => ({
    name: `Phase ${phaseName}`,
    value: count as number,
    phase: phaseName
  }));

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className="glass rounded-2xl p-6 border border-black/20 space-y-6 h-fit"
    >
      <h4 className="font-bold text-foreground flex items-center gap-3 text-lg">
        <Activity className="w-6 h-6 text-accent" />
        Clinical Trials Pipeline
      </h4>

      {/* Phase Distribution Chart */}
      {phaseChartData.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-4"
        >
          <h5 className="font-semibold text-slate-600 text-sm uppercase tracking-wide">Clinical Development Pipeline</h5>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  data={phaseChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {phaseChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    color: '#ffffff'
                  }}
                />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      )}

      {/* Phase Distribution Cards */}
      {Object.keys(phase).length > 0 && (
        <div className="space-y-3">
          <h5 className="font-semibold text-slate-600 text-sm uppercase tracking-wide">Phase Breakdown</h5>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.entries(phase).map(([phaseName, count], i) => (
              <motion.div
                key={phaseName}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
                whileHover={{ scale: 1.05 }}
                className="text-center p-4 bg-gradient-to-br from-accent/20 to-purple-600/20 rounded-xl border border-black/20"
              >
                <div className="text-xl font-bold text-foreground">{count}</div>
                <div className="text-xs text-slate-600 uppercase tracking-wide">Phase {phaseName}</div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Status Distribution */}
      {Object.keys(status).length > 0 && (
        <div className="space-y-3">
          <h5 className="font-semibold text-slate-600 text-sm uppercase tracking-wide">Trial Status Overview</h5>
          <div className="space-y-2">
            {Object.entries(status).map(([statusName, count]) => (
              <motion.div
                key={statusName}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                className="flex justify-between items-center p-3 bg-black/5 rounded-lg border border-black/10 hover:bg-black/10 transition-colors"
              >
                <span className="text-slate-800 capitalize font-medium">{statusName}</span>
                <span className="text-primary font-bold">{count}</span>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {trials.summary && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-4 bg-accent/20 rounded-xl border border-accent/30"
        >
          <p className="text-slate-800 text-sm leading-relaxed">{trials.summary}</p>
        </motion.div>
      )}
    </motion.div>
  );
}

function EximHighlights({ exim }: { exim?: EximResult }) {
  if (!exim) return null;

  const overview = exim.overview || {};

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className="glass rounded-2xl p-6 border border-black/20 space-y-4 h-full"
    >
      <h4 className="font-bold text-foreground flex items-center gap-3 text-lg">
        <Globe className="w-6 h-6 text-warning" />
        Trade & Supply Chain
      </h4>

      {/* Trade Statistics */}
      <div className="grid grid-cols-2 gap-4">
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="text-center p-4 bg-success/20 rounded-xl border border-success/30"
        >
          <div className="text-xl font-bold text-success">${overview.total_export_value_usd_mn?.toFixed(1) || 0}M</div>
          <div className="text-xs text-slate-600 uppercase tracking-wide">Export Value</div>
        </motion.div>
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="text-center p-4 bg-primary/20 rounded-xl border border-primary/30"
        >
          <div className="text-xl font-bold text-primary">${overview.total_import_value_usd_mn?.toFixed(1) || 0}M</div>
          <div className="text-xs text-slate-600 uppercase tracking-wide">Import Value</div>
        </motion.div>
      </div>

      {exim.summary && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-4 bg-warning/20 rounded-xl border border-warning/30"
        >
          <p className="text-slate-800 text-sm leading-relaxed">{exim.summary}</p>
        </motion.div>
      )}
    </motion.div>
  );
}

function WebHighlights({ web }: { web?: WebResult }) {
  if (!web) return null;

  const guidelines = web.guidelines || [];
  const news = web.news || [];
  const rwe = web.rwe || [];
  const regulatory = web.regulatory || [];
  const publications = web.publications || [];
  const marketNews = web.market_news || [];

  const totalSources = guidelines.length + news.length + rwe.length + regulatory.length + publications.length + marketNews.length;

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className="glass rounded-2xl p-6 border border-black/20 space-y-6 h-fit"
    >
      <div className="flex items-center justify-between">
        <h4 className="font-bold text-foreground flex items-center gap-3 text-lg">
          <TrendingUp className="w-6 h-6 text-success" />
          Web Intelligence & Sources
        </h4>
        <div className="text-right">
          <div className="text-2xl font-bold text-success">{totalSources}</div>
          <div className="text-xs text-slate-600">Total Sources</div>
        </div>
      </div>

      {/* Intelligence Stats */}
      <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
        {[
          { count: guidelines.length, label: "Guidelines", color: "primary" },
          { count: rwe.length, label: "RWE", color: "secondary" },
          { count: regulatory.length, label: "Regulatory", color: "accent" },
          { count: publications.length, label: "Publications", color: "success" },
          { count: marketNews.length, label: "Market", color: "warning" },
          { count: news.length, label: "News", color: "error" },
        ].map((stat) => (
          <motion.div
            key={stat.label}
            whileHover={{ scale: 1.05 }}
            className={`text-center p-3 bg-${stat.color}/20 rounded-lg border border-${stat.color}/30`}
          >
            <div className={`text-lg font-bold text-${stat.color}`}>{stat.count}</div>
            <div className="text-xs text-slate-600">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Detailed Links Sections */}
      <div className="grid grid-cols-1 gap-8">
        {/* Guidelines */}
        {guidelines.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="space-y-3"
          >
            <h5 className="font-semibold text-primary text-sm uppercase tracking-wide flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Clinical Practice Guidelines
            </h5>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {guidelines.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="p-4 glass rounded-lg border border-black/20 bg-black/5 hover:bg-black/10 transition-all duration-300"
                >
                  <div className="flex items-start gap-3">
                    <span className="text-primary mt-1">📋</span>
                    <div className="flex-1">
                      <h6 className="font-semibold text-foreground text-sm leading-tight mb-2">
                        {item.title}
                      </h6>
                      {item.snippet && (
                        <p className="text-slate-600 text-xs leading-relaxed mb-3">
                          {item.snippet.length > 120 ? `${item.snippet.substring(0, 120)}...` : item.snippet}
                        </p>
                      )}
                      {item.url && (
                        <motion.a
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-primary hover:text-secondary font-medium text-sm transition-colors"
                        >
                          <Globe className="w-3 h-3" />
                          <span>View Guideline</span>
                          <ArrowRight className="w-3 h-3" />
                        </motion.a>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Real World Evidence */}
        {rwe.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-3"
          >
            <h5 className="font-semibold text-accent text-sm uppercase tracking-wide flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Real World Evidence Studies
            </h5>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {rwe.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="p-4 glass rounded-lg border border-black/20 bg-black/5 hover:bg-black/10 transition-all duration-300"
                >
                  <div className="flex items-start gap-3">
                    <span className="text-accent mt-1">📊</span>
                    <div className="flex-1">
                      <h6 className="font-semibold text-foreground text-sm leading-tight mb-2">
                        {item.title}
                      </h6>
                      {item.snippet && (
                        <p className="text-slate-600 text-xs leading-relaxed mb-3">
                          {item.snippet.length > 120 ? `${item.snippet.substring(0, 120)}...` : item.snippet}
                        </p>
                      )}
                      {item.url && (
                        <motion.a
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-accent hover:text-warning font-medium text-sm transition-colors"
                        >
                          <Globe className="w-3 h-3" />
                          <span>View Study</span>
                          <ArrowRight className="w-3 h-3" />
                        </motion.a>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Regulatory Updates */}
        {regulatory.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-3"
          >
            <h5 className="font-semibold text-error text-sm uppercase tracking-wide flex items-center gap-2">
              <Target className="w-4 h-4" />
              Regulatory Updates
            </h5>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {regulatory.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="p-4 glass rounded-lg border border-black/20 bg-black/5 hover:bg-black/10 transition-all duration-300"
                >
                  <div className="flex items-start gap-3">
                    <span className="text-error mt-1">🏛️</span>
                    <div className="flex-1">
                      <h6 className="font-semibold text-foreground text-sm leading-tight mb-2">
                        {item.title}
                      </h6>
                      {item.snippet && (
                        <p className="text-slate-600 text-xs leading-relaxed mb-3">
                          {item.snippet.length > 120 ? `${item.snippet.substring(0, 120)}...` : item.snippet}
                        </p>
                      )}
                      {item.url && (
                        <motion.a
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-error hover:text-red-400 font-medium text-sm transition-colors"
                        >
                          <Globe className="w-3 h-3" />
                          <span>View Update</span>
                          <ArrowRight className="w-3 h-3" />
                        </motion.a>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Scientific Publications */}
        {publications.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="space-y-3"
          >
            <h5 className="font-semibold text-success text-sm uppercase tracking-wide flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Scientific Publications
            </h5>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {publications.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="p-4 glass rounded-lg border border-black/20 bg-black/5 hover:bg-black/10 transition-all duration-300"
                >
                  <div className="flex items-start gap-3">
                    <span className="text-success mt-1">📚</span>
                    <div className="flex-1">
                      <h6 className="font-semibold text-foreground text-sm leading-tight mb-2">
                        {item.title}
                      </h6>
                      {item.snippet && (
                        <p className="text-slate-600 text-xs leading-relaxed mb-3">
                          {item.snippet.length > 120 ? `${item.snippet.substring(0, 120)}...` : item.snippet}
                        </p>
                      )}
                      {item.url && (
                        <motion.a
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-success hover:text-green-400 font-medium text-sm transition-colors"
                        >
                          <Globe className="w-3 h-3" />
                          <span>View Publication</span>
                          <ArrowRight className="w-3 h-3" />
                        </motion.a>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Market News */}
        {marketNews.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="space-y-3"
          >
            <h5 className="font-semibold text-warning text-sm uppercase tracking-wide flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Market Intelligence
            </h5>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {marketNews.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="p-4 glass rounded-lg border border-black/20 bg-black/5 hover:bg-black/10 transition-all duration-300"
                >
                  <div className="flex items-start gap-3">
                    <span className="text-warning mt-1">📈</span>
                    <div className="flex-1">
                      <h6 className="font-semibold text-foreground text-sm leading-tight mb-2">
                        {item.title}
                      </h6>
                      {item.snippet && (
                        <p className="text-slate-600 text-xs leading-relaxed mb-3">
                          {item.snippet.length > 120 ? `${item.snippet.substring(0, 120)}...` : item.snippet}
                        </p>
                      )}
                      {item.url && (
                        <motion.a
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-warning hover:text-orange-400 font-medium text-sm transition-colors"
                        >
                          <Globe className="w-3 h-3" />
                          <span>View Analysis</span>
                          <ArrowRight className="w-3 h-3" />
                        </motion.a>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Latest News */}
        {news.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="space-y-3"
          >
            <h5 className="font-semibold text-accent text-sm uppercase tracking-wide flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Latest News & Updates
            </h5>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {news.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="p-4 glass rounded-lg border border-black/20 bg-black/5 hover:bg-black/10 transition-all duration-300"
                >
                  <div className="flex items-start gap-3">
                    <span className="text-accent mt-1">📰</span>
                    <div className="flex-1">
                      <h6 className="font-semibold text-foreground text-sm leading-tight mb-2">
                        {item.title}
                      </h6>
                      {item.snippet && (
                        <p className="text-slate-600 text-xs leading-relaxed mb-3">
                          {item.snippet.length > 120 ? `${item.snippet.substring(0, 120)}...` : item.snippet}
                        </p>
                      )}
                      {item.url && (
                        <motion.a
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-accent hover:text-purple-400 font-medium text-sm transition-colors"
                        >
                          <Globe className="w-3 h-3" />
                          <span>Read Article</span>
                          <ArrowRight className="w-3 h-3" />
                        </motion.a>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {web.summary && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-4 bg-gradient-to-r from-primary/20 to-secondary/20 rounded-xl border border-black/20"
        >
          <p className="text-slate-800 text-sm leading-relaxed">{web.summary}</p>
        </motion.div>
      )}
    </motion.div>
  );
}

function InternalHighlights({ internal }: { internal?: InternalResult }) {
  if (!internal) return null;
  const docs = internal.documents || [];
  const takeaways = internal.key_takeaways || [];

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className="glass rounded-2xl p-6 border border-black/20 space-y-4 h-full"
    >
      <h4 className="font-bold text-foreground flex items-center gap-3 text-lg">
        <Database className="w-6 h-6 text-accent" />
        Internal Knowledge Base
      </h4>

      {/* Document Stats */}
      <motion.div
        whileHover={{ scale: 1.05 }}
        className="text-center p-6 bg-gradient-to-br from-accent/20 to-purple-600/20 rounded-xl border border-accent/30"
      >
        <div className="text-3xl font-bold text-accent">{docs.length}</div>
        <div className="text-sm text-slate-600 uppercase tracking-wide">Documents Available</div>
      </motion.div>

      {/* Key Takeaways */}
      {takeaways.length > 0 && (
        <div className="space-y-2">
          <h5 className="font-semibold text-slate-600 text-sm uppercase tracking-wide">Key Insights</h5>
          {takeaways.slice(0, 3).map((takeaway, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-start gap-3 p-3 bg-black/5 rounded-lg border border-black/10"
            >
              <span className="text-primary mt-1">•</span>
              <span className="text-slate-800 text-sm leading-relaxed">{takeaway}</span>
            </motion.div>
          ))}
        </div>
      )}

      {internal.summary && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-4 bg-gradient-to-r from-secondary/20 to-accent/20 rounded-xl border border-black/20"
        >
          <p className="text-slate-800 text-sm leading-relaxed">{internal.summary}</p>
        </motion.div>
      )}
    </motion.div>
  );
}
