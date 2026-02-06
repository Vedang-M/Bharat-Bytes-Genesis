/**
 * Developer Documentation Page
 * Hidden route for viewing ML model metrics and system documentation.
 * Access: /documentation (not linked in main navigation)
 */

import { useEffect, useState } from "react";
import {
  Code2,
  Database,
  Brain,
  Activity,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ExternalLink,
  Server,
  Cpu,
  RefreshCw,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const Documentation = () => {
  const [docs, setDocs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedModels, setExpandedModels] = useState({});

  useEffect(() => {
    fetchDocs();
  }, []);

  const fetchDocs = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/dev/doc`);
      if (!response.ok) throw new Error("Failed to fetch documentation");
      const data = await response.json();
      setDocs(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleModelExpand = (modelName) => {
    setExpandedModels((prev) => ({
      ...prev,
      [modelName]: !prev[modelName],
    }));
  };

  const getConfidenceColor = (confidence) => {
    if (!confidence) return "text-gray-400";
    if (confidence.includes("High")) return "text-green-400";
    if (confidence.includes("Moderate")) return "text-yellow-400";
    return "text-red-400";
  };

  const getConfidenceIcon = (confidence) => {
    if (!confidence) return AlertTriangle;
    if (confidence.includes("High")) return CheckCircle2;
    if (confidence.includes("Moderate")) return AlertTriangle;
    return XCircle;
  };

  const formatMetricValue = (value, isPercent = false) => {
    if (value === null || value === undefined) return "N/A";
    if (typeof value === "number") {
      return isPercent ? `${(value * 100).toFixed(2)}%` : value.toFixed(4);
    }
    return value;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0d1117] text-gray-100 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <RefreshCw className="w-12 h-12 text-blue-500 animate-spin" />
          <p className="text-gray-400 font-mono">Loading documentation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#0d1117] text-gray-100 flex items-center justify-center">
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-8 max-w-md text-center">
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-red-400 mb-2">Failed to Load</h2>
          <p className="text-gray-400 font-mono text-sm mb-4">{error}</p>
          <button
            onClick={fetchDocs}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg font-medium transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0d1117] text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-[#161b22]">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="bg-blue-600 p-3 rounded-xl">
                <Code2 className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">{docs?.system?.name || "Water Wallet API"}</h1>
                <p className="text-gray-400 text-sm font-mono">
                  v{docs?.system?.version || "1.0.0"} • Developer Documentation
                </p>
              </div>
            </div>
            <div className="text-right text-sm">
              <p className="text-gray-500">Last Updated</p>
              <p className="text-gray-300 font-mono">
                {docs?.system?.documentation_generated
                  ? new Date(docs.system.documentation_generated).toLocaleString()
                  : "N/A"}
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* System Overview */}
        <section className="mb-10">
          <p className="text-lg text-gray-300 mb-6">{docs?.system?.description}</p>
          <p className="text-gray-400">{docs?.system?.tagline}</p>
        </section>

        {/* Quick Stats */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10">
          <div className="bg-[#161b22] border border-gray-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-2">
              <Brain className="w-5 h-5 text-purple-400" />
              <span className="text-gray-400 text-sm">ML Models</span>
            </div>
            <p className="text-3xl font-bold text-white">
              {docs?.ml_models?.models?.length || 0}
            </p>
          </div>
          <div className="bg-[#161b22] border border-gray-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-2">
              <Database className="w-5 h-5 text-blue-400" />
              <span className="text-gray-400 text-sm">Data Sources</span>
            </div>
            <p className="text-3xl font-bold text-white">
              {docs?.data_sources?.length || 0}
            </p>
          </div>
          <div className="bg-[#161b22] border border-gray-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-2">
              <Server className="w-5 h-5 text-green-400" />
              <span className="text-gray-400 text-sm">API Endpoints</span>
            </div>
            <p className="text-3xl font-bold text-white">
              {Object.keys(docs?.api_endpoints || {}).length}
            </p>
          </div>
          <div className="bg-[#161b22] border border-gray-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-2">
              <Activity className="w-5 h-5 text-yellow-400" />
              <span className="text-gray-400 text-sm">Crops Supported</span>
            </div>
            <p className="text-3xl font-bold text-white">
              {docs?.crop_database?.total_crops || 20}
            </p>
          </div>
        </section>

        {/* Prediction Confidence */}
        <section className="mb-10">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-green-400" />
            Prediction Confidence Scores
          </h2>
          <div className="bg-[#161b22] border border-gray-800 rounded-xl overflow-hidden">
            {docs?.prediction_confidence &&
            Object.keys(docs.prediction_confidence).length > 0 ? (
              <div className="divide-y divide-gray-800">
                {Object.entries(docs.prediction_confidence).map(([model, confidence]) => {
                  const ConfIcon = getConfidenceIcon(confidence);
                  return (
                    <div
                      key={model}
                      className="px-6 py-4 flex items-center justify-between hover:bg-gray-800/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <ConfIcon className={`w-5 h-5 ${getConfidenceColor(confidence)}`} />
                        <span className="font-mono text-gray-300">{model}</span>
                      </div>
                      <span className={`font-mono text-sm ${getConfidenceColor(confidence)}`}>
                        {confidence}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-6 text-center text-gray-500">
                <p>No confidence metrics available. Train models first.</p>
                <code className="text-xs text-blue-400 mt-2 block">
                  python -m ml.scripts.train_models
                </code>
              </div>
            )}
          </div>
        </section>

        {/* ML Models */}
        <section className="mb-10">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-400" />
            ML Model Metrics
          </h2>

          {docs?.ml_models?.models?.length > 0 ? (
            <div className="space-y-4">
              {docs.ml_models.models.map((model) => (
                <div
                  key={model.name}
                  className="bg-[#161b22] border border-gray-800 rounded-xl overflow-hidden"
                >
                  {/* Model Header */}
                  <div
                    onClick={() => toggleModelExpand(model.name)}
                    className="px-6 py-4 flex items-center justify-between cursor-pointer hover:bg-gray-800/50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <Cpu className="w-5 h-5 text-blue-400" />
                      <div>
                        <h3 className="font-bold text-white">{model.name}</h3>
                        <p className="text-sm text-gray-500 font-mono">
                          {model.type} • v{model.version}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {model.metrics && (
                        <div className="text-right hidden md:block">
                          {model.type === "classification" && (
                            <span className="text-green-400 font-mono text-sm">
                              F1: {formatMetricValue(model.metrics.f1_score)}
                            </span>
                          )}
                          {model.type === "regression" && (
                            <span className="text-green-400 font-mono text-sm">
                              R²: {formatMetricValue(model.metrics.r2_score)}
                            </span>
                          )}
                        </div>
                      )}
                      {expandedModels[model.name] ? (
                        <ChevronUp className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {expandedModels[model.name] && (
                    <div className="border-t border-gray-800 px-6 py-4 bg-[#0d1117]">
                      {/* Metrics Grid */}
                      {model.metrics && (
                        <div className="mb-4">
                          <h4 className="text-sm font-bold text-gray-400 uppercase tracking-wide mb-3">
                            Performance Metrics
                          </h4>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {Object.entries(model.metrics).map(([key, value]) => (
                              <div
                                key={key}
                                className="bg-[#161b22] rounded-lg p-3 border border-gray-800"
                              >
                                <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">
                                  {key.replace(/_/g, " ")}
                                </p>
                                <p className="text-lg font-mono text-green-400">
                                  {key.includes("accuracy") || key.includes("precision") || key.includes("recall")
                                    ? formatMetricValue(value, true)
                                    : formatMetricValue(value)}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Per-Class Metrics */}
                      {model.per_class_metrics && (
                        <div className="mb-4">
                          <h4 className="text-sm font-bold text-gray-400 uppercase tracking-wide mb-3">
                            Per-Class Performance
                          </h4>
                          <div className="overflow-x-auto">
                            <table className="w-full text-sm font-mono">
                              <thead>
                                <tr className="text-gray-500 border-b border-gray-800">
                                  <th className="text-left py-2 px-3">Class</th>
                                  <th className="text-right py-2 px-3">Precision</th>
                                  <th className="text-right py-2 px-3">Recall</th>
                                  <th className="text-right py-2 px-3">F1-Score</th>
                                  <th className="text-right py-2 px-3">Support</th>
                                </tr>
                              </thead>
                              <tbody>
                                {Object.entries(model.per_class_metrics).map(([cls, metrics]) => (
                                  <tr key={cls} className="border-b border-gray-800/50">
                                    <td className="py-2 px-3 text-gray-300">{cls}</td>
                                    <td className="py-2 px-3 text-right text-blue-400">
                                      {metrics.precision?.toFixed(3)}
                                    </td>
                                    <td className="py-2 px-3 text-right text-purple-400">
                                      {metrics.recall?.toFixed(3)}
                                    </td>
                                    <td className="py-2 px-3 text-right text-green-400">
                                      {metrics.f1_score?.toFixed(3)}
                                    </td>
                                    <td className="py-2 px-3 text-right text-gray-400">
                                      {metrics.support}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}

                      {/* Confusion Matrix */}
                      {model.confusion_matrix && (
                        <div className="mb-4">
                          <h4 className="text-sm font-bold text-gray-400 uppercase tracking-wide mb-3">
                            Confusion Matrix
                          </h4>
                          <div className="inline-block">
                            <table className="font-mono text-sm">
                              <tbody>
                                {model.confusion_matrix.map((row, i) => (
                                  <tr key={i}>
                                    {row.map((cell, j) => (
                                      <td
                                        key={j}
                                        className={`px-4 py-2 text-center border border-gray-700 ${
                                          i === j
                                            ? "bg-green-900/30 text-green-400"
                                            : "bg-gray-800/30 text-gray-400"
                                        }`}
                                      >
                                        {cell}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}

                      {/* Evaluation Info */}
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Clock className="w-4 h-4" />
                        <span>
                          Last evaluated:{" "}
                          {model.last_evaluated
                            ? new Date(model.last_evaluated).toLocaleString()
                            : "N/A"}
                        </span>
                        <span className="mx-2">•</span>
                        <span>{model.total_samples?.toLocaleString() || "N/A"} samples</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-[#161b22] border border-gray-800 rounded-xl p-8 text-center">
              <Brain className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 mb-2">No model metrics available</p>
              <code className="text-xs text-blue-400">python -m ml.scripts.train_models</code>
            </div>
          )}
        </section>

        {/* Data Sources */}
        <section className="mb-10">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-400" />
            Data Sources (Active)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {docs?.data_sources?.map((source) => (
              <div
                key={source.name}
                className="bg-[#161b22] border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-white">{source.name}</h3>
                    {source.status === "Active" && (
                      <span className="text-xs bg-green-900/30 text-green-400 px-2 py-1 rounded-full">
                        Active
                      </span>
                    )}
                  </div>
                  <span className="text-xs bg-blue-900/30 text-blue-400 px-2 py-1 rounded-full font-mono">
                    {source.update_frequency}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-3">{source.description}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500 font-mono mb-2">
                  <span>📍 {source.coverage}</span>
                  <span>🔗 {source.api_type}</span>
                </div>
                {source.used_in && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {source.used_in.map((model) => (
                      <span
                        key={model}
                        className="text-xs bg-purple-900/30 text-purple-400 px-2 py-0.5 rounded"
                      >
                        {model}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* API Endpoints */}
        <section className="mb-10">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Server className="w-5 h-5 text-green-400" />
            API Endpoints
          </h2>
          <div className="bg-[#161b22] border border-gray-800 rounded-xl overflow-hidden">
            <div className="divide-y divide-gray-800">
              {docs?.api_endpoints &&
                Object.entries(docs.api_endpoints).map(([key, endpoint]) => (
                  <div
                    key={key}
                    className="px-6 py-4 flex items-center justify-between hover:bg-gray-800/30 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <span
                        className={`px-2 py-1 rounded text-xs font-bold ${
                          endpoint.method === "GET"
                            ? "bg-green-900/30 text-green-400"
                            : "bg-blue-900/30 text-blue-400"
                        }`}
                      >
                        {endpoint.method}
                      </span>
                      <code className="text-gray-300 font-mono text-sm">{endpoint.path}</code>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-gray-500 text-sm hidden md:inline">
                        {endpoint.description}
                      </span>
                      {endpoint.auth_required && (
                        <span className="text-xs bg-yellow-900/30 text-yellow-400 px-2 py-1 rounded-full">
                          Auth Required
                        </span>
                      )}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </section>

        {/* Technical Stack */}
        <section className="mb-10">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-purple-400" />
            Technical Stack
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {docs?.technical_stack &&
              Object.entries(docs.technical_stack).map(([key, value]) => (
                <div
                  key={key}
                  className="bg-[#161b22] border border-gray-800 rounded-xl p-4 text-center"
                >
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">
                    {key.replace(/_/g, " ")}
                  </p>
                  <p className="text-sm text-gray-300 font-mono">{value}</p>
                </div>
              ))}
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-gray-800 pt-6 mt-10 text-center text-sm text-gray-500">
          <p>
            Water Wallet API • Built for{" "}
            <span className="text-green-400">Small & Marginal Farmers</span>
          </p>
          <p className="mt-2 font-mono text-xs">
            Evaluation Date: {docs?.evaluation_summary?.latest_evaluation || "N/A"}
          </p>
        </footer>
      </main>
    </div>
  );
};

export default Documentation;
