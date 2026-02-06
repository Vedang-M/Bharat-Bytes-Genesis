import { useState } from "react";
import {
  Copy,
  Check,
  Key,
  Book,
  Code,
  Lock,
  ChevronDown,
  ChevronUp,
  Play,
  Home,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

const ApiDocumentation = () => {
  const navigate = useNavigate();
  const [copiedKey, setCopiedKey] = useState(false);
  const [apiKey, setApiKey] = useState("sk_live_1234567890abcdef");
  const [expandedEndpoint, setExpandedEndpoint] = useState(null);
  const [testResponse, setTestResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const glassCardClass =
    "bg-gradient-to-b from-white/20 to-white/5 backdrop-blur-xl border border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.1)]";
  const glassPillClass =
    "bg-gradient-to-b from-white/20 to-white/5 backdrop-blur-lg border border-white/10 shadow-sm";

  const handleCopyKey = () => {
    navigator.clipboard.writeText(apiKey);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  const generateNewKey = () => {
    const newKey =
      "sk_live_" +
      Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15);
    setApiKey(newKey);
  };

  const apiEndpoints = [
    {
      id: "water-status",
      method: "GET",
      path: "/api/water-status",
      description: "Get current water availability status for a location",
      parameters: [
        {
          name: "district",
          type: "string",
          required: true,
          description: "District name",
        },
        {
          name: "state",
          type: "string",
          required: true,
          description: "State name",
        },
      ],
      response: {
        location: { district: "पुणे", state: "महाराष्ट्र" },
        waterAvailability: 400,
        status: "limited",
        timestamp: "2026-02-05T15:52:29+05:30",
      },
    },
    {
      id: "crop-recommendation",
      method: "POST",
      path: "/api/crop-recommendation",
      description:
        "Get crop recommendations based on water availability and soil conditions",
      parameters: [
        {
          name: "waterAvailability",
          type: "number",
          required: true,
          description: "Water availability in mm",
        },
        {
          name: "soilType",
          type: "string",
          required: true,
          description: "Type of soil",
        },
        {
          name: "season",
          type: "string",
          required: true,
          description: "Current season",
        },
      ],
      response: {
        recommendations: [
          { crop: "गेहूं", suitability: "high", waterRequirement: 350 },
          { crop: "बाजरा", suitability: "medium", waterRequirement: 250 },
        ],
      },
    },
    {
      id: "crop-advice",
      method: "GET",
      path: "/api/crop-advice/:cropId",
      description: "Get detailed advice for a specific crop",
      parameters: [
        {
          name: "cropId",
          type: "string",
          required: true,
          description: "Crop identifier",
        },
      ],
      response: {
        crop: "गेहूं",
        wateringSchedule: "Every 7-10 days",
        fertilizer: "NPK 120:60:40",
        pestControl: "Monitor for aphids",
        harvestTime: "120-150 days",
      },
    },
    {
      id: "user-profile",
      method: "GET",
      path: "/api/user/profile",
      description: "Get user profile information",
      parameters: [],
      response: {
        name: "किसान नाम",
        phone: "+91 98765 43210",
        location: { district: "पुणे", state: "महाराष्ट्र" },
        language: "hi",
      },
    },
  ];

  const handleTestEndpoint = async (endpoint) => {
    setIsLoading(true);
    setTestResponse(null);

    // Simulate API call
    setTimeout(() => {
      setTestResponse({
        status: 200,
        data: endpoint.response,
      });
      setIsLoading(false);
    }, 1000);
  };

  const toggleEndpoint = (id) => {
    setExpandedEndpoint(expandedEndpoint === id ? null : id);
  };

  return (
    <div className="min-h-screen bg-[#FAFAF7] font-hindi overflow-auto relative">
      {/* Background Images */}
      <img
        src="/Hero-image-desktop.webp"
        alt=""
        className="fixed inset-0 w-full h-full object-cover hidden md:block"
      />
      <img
        src="/Hero-inmage-mobile.webp"
        alt=""
        className="fixed inset-0 w-full h-full object-cover block md:hidden"
      />
      <div className="fixed inset-0 bg-gradient-to-b from-[#422B06]/80 to-[#422B06]/50" />

      {/* Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-5 py-8">
        {/* Header */}
        <header className={`${glassPillClass} p-6 rounded-3xl mb-8`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-[#2E7D32] to-[#43A047] flex items-center justify-center">
                <Code size={24} className="text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-black text-white">
                  API Documentation
                </h1>
                <p className="text-white/70 text-sm">
                  Developer Resources & API Reference
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate("/")}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-xl text-white transition-colors"
            >
              <Home size={20} />
              <span className="font-bold">Home</span>
            </button>
          </div>
        </header>

        {/* API Credentials Section */}
        <section className={`${glassCardClass} p-6 rounded-3xl mb-8`}>
          <div className="flex items-center gap-3 mb-6">
            <Key size={24} className="text-[#A5D6A7]" />
            <h2 className="text-2xl font-black text-white">API Credentials</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-white/70 text-sm font-bold mb-2 block">
                Your API Key
              </label>
              <div className="flex gap-3">
                <div className="flex-1 bg-black/20 rounded-xl p-4 font-mono text-white border border-white/10">
                  {apiKey}
                </div>
                <button
                  onClick={handleCopyKey}
                  className="px-6 py-4 bg-[#2E7D32] hover:bg-[#43A047] rounded-xl text-white font-bold transition-colors flex items-center gap-2"
                >
                  {copiedKey ? <Check size={20} /> : <Copy size={20} />}
                  {copiedKey ? "Copied!" : "Copy"}
                </button>
              </div>
            </div>

            <button
              onClick={generateNewKey}
              className="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-xl text-white font-bold transition-colors"
            >
              Generate New Key
            </button>

            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 mt-4">
              <div className="flex items-start gap-3">
                <Lock size={20} className="text-yellow-400 mt-0.5" />
                <div>
                  <p className="text-yellow-100 font-bold mb-1">
                    Keep your API key secure
                  </p>
                  <p className="text-yellow-200/70 text-sm">
                    Never share your API key publicly or commit it to version
                    control.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Authentication Guide */}
        <section className={`${glassCardClass} p-6 rounded-3xl mb-8`}>
          <div className="flex items-center gap-3 mb-6">
            <Lock size={24} className="text-[#A5D6A7]" />
            <h2 className="text-2xl font-black text-white">Authentication</h2>
          </div>

          <div className="space-y-4">
            <p className="text-white/90">
              Include your API key in the request header:
            </p>
            <div className="bg-black/40 rounded-xl p-4 border border-white/10">
              <pre className="text-green-300 font-mono text-sm overflow-x-auto">
                {`Authorization: Bearer YOUR_API_KEY
Content-Type: application/json`}
              </pre>
            </div>

            <p className="text-white/90 mt-4">Example using cURL:</p>
            <div className="bg-black/40 rounded-xl p-4 border border-white/10">
              <pre className="text-green-300 font-mono text-sm overflow-x-auto">
                {`curl -X GET "https://api.example.com/api/water-status?district=pune&state=maharashtra" \\
  -H "Authorization: Bearer ${apiKey}" \\
  -H "Content-Type: application/json"`}
              </pre>
            </div>
          </div>
        </section>

        {/* API Endpoints */}
        <section className={`${glassCardClass} p-6 rounded-3xl mb-8`}>
          <div className="flex items-center gap-3 mb-6">
            <Book size={24} className="text-[#A5D6A7]" />
            <h2 className="text-2xl font-black text-white">API Endpoints</h2>
          </div>

          <div className="space-y-4">
            {apiEndpoints.map((endpoint) => (
              <div
                key={endpoint.id}
                className="bg-white/5 rounded-xl border border-white/10 overflow-hidden"
              >
                {/* Endpoint Header */}
                <button
                  onClick={() => toggleEndpoint(endpoint.id)}
                  className="w-full p-4 flex items-center justify-between hover:bg-white/5 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <span
                      className={`px-3 py-1 rounded-lg font-bold text-sm ${
                        endpoint.method === "GET"
                          ? "bg-blue-500/20 text-blue-300"
                          : "bg-green-500/20 text-green-300"
                      }`}
                    >
                      {endpoint.method}
                    </span>
                    <code className="text-white font-mono">
                      {endpoint.path}
                    </code>
                  </div>
                  {expandedEndpoint === endpoint.id ? (
                    <ChevronUp size={20} className="text-white/70" />
                  ) : (
                    <ChevronDown size={20} className="text-white/70" />
                  )}
                </button>

                {/* Endpoint Details */}
                {expandedEndpoint === endpoint.id && (
                  <div className="p-4 pt-0 space-y-4">
                    <p className="text-white/90">{endpoint.description}</p>

                    {/* Parameters */}
                    {endpoint.parameters.length > 0 && (
                      <div>
                        <h4 className="text-white font-bold mb-2">
                          Parameters
                        </h4>
                        <div className="space-y-2">
                          {endpoint.parameters.map((param) => (
                            <div
                              key={param.name}
                              className="bg-black/20 rounded-lg p-3 border border-white/10"
                            >
                              <div className="flex items-center gap-2 mb-1">
                                <code className="text-green-300 font-mono">
                                  {param.name}
                                </code>
                                <span className="text-xs text-white/50">
                                  {param.type}
                                </span>
                                {param.required && (
                                  <span className="text-xs bg-red-500/20 text-red-300 px-2 py-0.5 rounded">
                                    required
                                  </span>
                                )}
                              </div>
                              <p className="text-white/70 text-sm">
                                {param.description}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Response Example */}
                    <div>
                      <h4 className="text-white font-bold mb-2">
                        Response Example
                      </h4>
                      <div className="bg-black/40 rounded-lg p-4 border border-white/10">
                        <pre className="text-green-300 font-mono text-sm overflow-x-auto">
                          {JSON.stringify(endpoint.response, null, 2)}
                        </pre>
                      </div>
                    </div>

                    {/* Test Button */}
                    <button
                      onClick={() => handleTestEndpoint(endpoint)}
                      disabled={isLoading}
                      className="flex items-center gap-2 px-4 py-2 bg-[#2E7D32] hover:bg-[#43A047] disabled:bg-gray-500 rounded-lg text-white font-bold transition-colors"
                    >
                      <Play size={16} />
                      {isLoading ? "Testing..." : "Test Endpoint"}
                    </button>

                    {/* Test Response */}
                    {testResponse && (
                      <div className="mt-4">
                        <h4 className="text-white font-bold mb-2">
                          Test Response
                        </h4>
                        <div className="bg-black/40 rounded-lg p-4 border border-green-500/30">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-green-400 font-bold">
                              Status: {testResponse.status}
                            </span>
                          </div>
                          <pre className="text-green-300 font-mono text-sm overflow-x-auto">
                            {JSON.stringify(testResponse.data, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Rate Limits */}
        <section className={`${glassCardClass} p-6 rounded-3xl mb-8`}>
          <h2 className="text-2xl font-black text-white mb-4">Rate Limits</h2>
          <div className="space-y-3 text-white/90">
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
              <span>Requests per minute</span>
              <span className="font-bold text-green-300">60</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
              <span>Requests per hour</span>
              <span className="font-bold text-green-300">1,000</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
              <span>Requests per day</span>
              <span className="font-bold text-green-300">10,000</span>
            </div>
          </div>
        </section>

        {/* Support */}
        <section className={`${glassCardClass} p-6 rounded-3xl`}>
          <h2 className="text-2xl font-black text-white mb-4">Need Help?</h2>
          <p className="text-white/90 mb-4">
            If you have questions or need assistance with the API, please reach
            out to our support team.
          </p>
          <div className="flex gap-4">
            <a
              href="mailto:support@example.com"
              className="px-6 py-3 bg-[#2E7D32] hover:bg-[#43A047] rounded-xl text-white font-bold transition-colors"
            >
              Contact Support
            </a>
            <a
              href="#"
              className="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-xl text-white font-bold transition-colors"
            >
              View Full Documentation
            </a>
          </div>
        </section>
      </div>
    </div>
  );
};

export default ApiDocumentation;
