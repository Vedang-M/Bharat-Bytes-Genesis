import { useState, useEffect } from "react";
import {
  Shield,
  Droplet,
  AlertTriangle,
  CheckCircle2,
  Send,
  Users,
  MapPin,
  RefreshCw,
} from "lucide-react";
import { Bar } from "react-chartjs-2";
import { toast } from "react-toastify";
import { broadcastNotification } from "../utils/notificationUtils";
import { useAuth } from "../context/AuthContext";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { getTranslations, getLanguage } from "../utils/languageUtils";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const SarpanchDashboard = () => {
  const { userProfile, getAuthToken } = useAuth();
  const [language, setLanguage] = useState("hi");
  const [notificationMsg, setNotificationMsg] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [villageData, setVillageData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const savedLanguage = getLanguage();
    if (savedLanguage) {
      setLanguage(savedLanguage);
    }
    fetchVillageData();
  }, []);

  const fetchVillageData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Get user's location for village aggregation
      const location = userProfile?.location || {};
      const state = location.state || "Uttar Pradesh";
      const district = location.district || "Prayagraj";

      // Fetch village aggregation data from backend
      const response = await fetch(
        `${API_URL}/api/village-stats?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}`,
      );

      if (response.ok) {
        const data = await response.json();
        setVillageData({
          villageName: language === "hi"
            ? `${district} जिला`
            : `${district} District`,
          status: data.water_status || "SAFE",
          totalDemand: data.total_demand_mm || 4200,
          totalAvailable: data.total_available_mm || 6800,
          utilizationPercentage: data.utilization_percentage || 62,
          farmers: data.total_farmers || 45,
          totalArea: data.total_area_ha || 120,
          predictionsToday: data.predictions_today || 0,
        });
      } else {
        // Fallback to demo data
        setVillageData({
          villageName: language === "hi" ? "रामपुर गाँव" : "Rampur Village",
          status: "SAFE",
          totalDemand: 4200,
          totalAvailable: 6800,
          utilizationPercentage: 62,
          farmers: 45,
          totalArea: 120,
          predictionsToday: 12,
        });
      }
    } catch (err) {
      console.error("Error fetching village data:", err);
      // Use demo data on error
      setVillageData({
        villageName: language === "hi" ? "रामपुर गाँव" : "Rampur Village",
        status: "SAFE",
        totalDemand: 4200,
        totalAvailable: 6800,
        utilizationPercentage: 62,
        farmers: 45,
        totalArea: 120,
        predictionsToday: 12,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleShareNotification = async () => {
    if (!notificationMsg.trim()) {
      toast.warning(
        language === "hi" ? "कृपया संदेश दर्ज करें" : "Please enter a message",
      );
      return;
    }

    setIsSending(true);

    try {
      // Send to backend
      const token = await getAuthToken();
      const location = userProfile?.location || {};

      const response = await fetch(`${API_URL}/api/notifications`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({
          message: notificationMsg,
          type: "info",
          state: location.state,
          district: location.district,
        }),
      });

      if (response.ok) {
        // Also broadcast locally
        broadcastNotification(notificationMsg, "info");
        toast.success(
          language === "hi" ? "सूचना साझा की गई!" : "Notification shared!",
        );
        setNotificationMsg("");
      } else {
        // Fallback to local broadcast
        broadcastNotification(notificationMsg, "info");
        toast.success(
          language === "hi" ? "सूचना साझा की गई!" : "Notification shared!",
        );
        setNotificationMsg("");
      }
    } catch (err) {
      console.error("Error sending notification:", err);
      // Still broadcast locally on error
      broadcastNotification(notificationMsg, "info");
      toast.success(
        language === "hi" ? "सूचना साझा की गई!" : "Notification shared!",
      );
      setNotificationMsg("");
    } finally {
      setIsSending(false);
    }
  };

  const t = getTranslations(language);

  const isCritical = villageData?.status === "CRITICAL";
  const statusConfig = isCritical
    ? {
      color: "#E53935",
      gradient: "from-[#E53935] to-[#EF5350]",
      icon: AlertTriangle,
      label: language === "hi" ? "संकटग्रस्त" : "CRITICAL",
      bgGlow: "bg-red-500/20",
    }
    : {
      color: "#2E7D32",
      gradient: "from-[#2E7D32] to-[#43A047]",
      icon: CheckCircle2,
      label: language === "hi" ? "सुरक्षित" : "SAFE",
      bgGlow: "bg-green-500/20",
    };

  const StatusIcon = statusConfig.icon;

  const glassCardClass =
    "bg-gradient-to-b from-white/20 to-white/5 backdrop-blur-xl border border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.1)]";
  const glassPillClass =
    "bg-gradient-to-b from-white/20 to-white/5 backdrop-blur-lg border border-white/10 shadow-sm";

  // Chart.js configuration
  const chartData = {
    labels: [
      language === "hi" ? "कुल माँग" : "Total Demand",
      language === "hi" ? "उपलब्ध पानी" : "Available Water",
    ],
    datasets: [
      {
        label: language === "hi" ? "पानी (mm)" : "Water (mm)",
        data: [villageData?.totalDemand || 0, villageData?.totalAvailable || 0],
        backgroundColor: [
          "rgba(249, 168, 37, 0.8)", // Orange for demand
          "rgba(46, 125, 50, 0.8)", // Green for available
        ],
        borderColor: ["rgba(249, 168, 37, 1)", "rgba(46, 125, 50, 1)"],
        borderWidth: 2,
        borderRadius: 12,
        barThickness: 60,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: (context) => `${context.parsed.y} mm`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: "rgba(255, 255, 255, 0.1)", drawBorder: false },
        ticks: {
          color: "rgba(255, 255, 255, 0.8)",
          callback: (v) => v + " mm",
        },
      },
      x: {
        grid: { display: false },
        ticks: { color: "rgba(255, 255, 255, 0.9)", font: { weight: "bold" } },
      },
    },
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#422B06] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-white border-t-transparent mx-auto mb-4"></div>
          <p className="text-white text-xl font-bold">
            {language === "hi" ? "डेटा लोड हो रहा है..." : "Loading data..."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAF7] font-hindi relative flex flex-col">
      <img
        src="/Hero-image-desktop.webp"
        alt=""
        className="absolute inset-0 w-full h-full object-cover hidden md:block"
      />
      <img
        src="/Hero-inmage-mobile.webp"
        alt=""
        className="absolute inset-0 w-full h-full object-cover block md:hidden"
      />
      <div className="absolute inset-0 bg-gradient-to-b from-[#422B06]/80 to-[#422B06]/50" />

      <div className="relative z-10 max-w-md lg:max-w-5xl mx-auto px-5 pt-4 pb-40 md:pb-10 md:pt-8 flex flex-col flex-1 w-full gap-6 overflow-y-auto md:overflow-hidden md:h-full">
        <header
          className={`${glassPillClass} p-5 rounded-[2.5rem] flex-shrink-0`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="bg-gradient-to-br from-[#2E7D32] to-[#43A047] p-3.5 rounded-2xl shadow-lg ring-2 ring-white/10">
                <Shield size={32} className="text-white" />
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-black text-white drop-shadow-md">
                  {language === "hi" ? "सरपंच डैशबोर्ड" : "Sarpanch Dashboard"}
                </h1>
                <p className="text-sm md:text-base font-bold text-white/80">
                  {villageData?.villageName}
                </p>
              </div>
            </div>
            <button
              onClick={fetchVillageData}
              className="p-3 rounded-xl bg-white/10 hover:bg-white/20 transition-all"
              title={language === "hi" ? "रिफ्रेश करें" : "Refresh"}
            >
              <RefreshCw size={24} className="text-white" />
            </button>
          </div>
        </header>

        <main className="flex flex-col gap-6 flex-1 w-full">
          {/* Health Status Card */}
          <div
            className={`${glassCardClass} rounded-[2.5rem] p-8 flex flex-col md:flex-row items-center justify-between relative overflow-hidden flex-shrink-0`}
          >
            <div
              className={`absolute inset-0 ${statusConfig.bgGlow} blur-3xl opacity-30`}
            />

            <div className="relative z-10 flex flex-col md:flex-row items-center gap-8 w-full">
              {/* Status Indicator */}
              <div className="flex flex-col items-center md:items-start gap-2 flex-shrink-0">
                <p className="text-sm font-bold text-white/70 uppercase tracking-wider">
                  {language === "hi" ? "गाँव की स्थिति" : "Village Status"}
                </p>
                <div
                  className={`inline-flex items-center gap-4 px-8 py-4 rounded-2xl bg-gradient-to-r ${statusConfig.gradient} shadow-2xl ring-2 ring-white/20`}
                >
                  <StatusIcon size={44} className="text-white" />
                  <span className="text-4xl md:text-5xl font-black text-white tracking-tight">
                    {statusConfig.label}
                  </span>
                </div>
              </div>

              {/* Key Metrics */}
              <div className="w-full flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white/10 border border-white/5 rounded-2xl p-4 backdrop-blur-sm">
                  <p className="text-white/70 text-xs font-bold mb-1 uppercase tracking-wider">
                    {language === "hi" ? "उपयोग" : "Utilization"}
                  </p>
                  <p className="text-white text-3xl font-black drop-shadow-sm">
                    {villageData?.utilizationPercentage}
                    <span className="text-lg font-bold text-white/60">%</span>
                  </p>
                </div>
                <div className="bg-white/10 border border-white/5 rounded-2xl p-4 backdrop-blur-sm">
                  <p className="text-white/70 text-xs font-bold mb-1 uppercase tracking-wider">
                    {language === "hi" ? "बचत" : "Surplus"}
                  </p>
                  <p className="text-white text-3xl font-black drop-shadow-sm">
                    {(villageData?.totalAvailable || 0) - (villageData?.totalDemand || 0)}
                    <span className="text-sm font-bold text-white/60 ml-1">
                      mm
                    </span>
                  </p>
                </div>
                <div className="bg-white/10 border border-white/5 rounded-2xl p-4 backdrop-blur-sm">
                  <div className="flex items-center gap-2 mb-1">
                    <Users size={14} className="text-white/70" />
                    <p className="text-white/70 text-xs font-bold uppercase tracking-wider">
                      {language === "hi" ? "किसान" : "Farmers"}
                    </p>
                  </div>
                  <p className="text-white text-3xl font-black drop-shadow-sm">
                    {villageData?.farmers}
                  </p>
                </div>
                <div className="bg-white/10 border border-white/5 rounded-2xl p-4 backdrop-blur-sm hidden md:block">
                  <div className="flex items-center gap-2 mb-1">
                    <MapPin size={14} className="text-white/70" />
                    <p className="text-white/70 text-xs font-bold uppercase tracking-wider">
                      {language === "hi" ? "क्षेत्र" : "Area"}
                    </p>
                  </div>
                  <p className="text-white text-3xl font-black drop-shadow-sm">
                    {villageData?.totalArea}
                    <span className="text-sm font-bold text-white/60 ml-1">ha</span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Section: Budget and Notifications */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 min-h-0">
            {/* Water Budget Chart Card */}
            <div
              className={`${glassCardClass} rounded-[2.5rem] p-8 flex flex-col h-full`}
            >
              <div className="flex items-center gap-2 mb-6">
                <Droplet size={24} className="text-[#90CAF9]" />
                <h2 className="text-xl font-black text-white">
                  {language === "hi" ? "पानी का बजट" : "Water Budget Overview"}
                </h2>
              </div>
              <div className="flex-1 min-h-[250px] relative">
                <Bar data={chartData} options={chartOptions} />
              </div>
              <div className="flex justify-center gap-6 mt-6 pt-6 border-t border-white/10 text-white/80 text-sm font-bold">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-[#F9A825]" />
                  <span>{language === "hi" ? "माँग" : "Demand"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-[#2E7D32]" />
                  <span>{language === "hi" ? "उपलब्ध" : "Available"}</span>
                </div>
              </div>
            </div>

            {/* Notification Center Card */}
            <div
              className={`${glassCardClass} rounded-[2.5rem] p-8 flex flex-col h-full`}
            >
              <div className="flex items-center gap-2 mb-4">
                <Send size={24} className="text-[#81C784]" />
                <h2 className="text-xl font-black text-white">
                  {language === "hi" ? "सूचना भेजें" : "Send Notification"}
                </h2>
              </div>
              <p className="text-white/60 text-sm mb-4">
                {language === "hi"
                  ? "गाँव के किसानों के लिए महत्वपूर्ण जानकारी साझा करें"
                  : "Share important updates with village farmers"}
              </p>
              <textarea
                value={notificationMsg}
                onChange={(e) => setNotificationMsg(e.target.value)}
                placeholder={
                  language === "hi"
                    ? "संदेश यहाँ लिखें..."
                    : "Type your message here..."
                }
                className="w-full bg-white/10 border border-white/20 rounded-2xl p-4 text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-[#43A047] h-40 resize-none mb-4"
              />
              <button
                onClick={handleShareNotification}
                disabled={isSending}
                className="w-full bg-gradient-to-r from-[#2E7D32] to-[#43A047] text-white font-black py-4 rounded-2xl shadow-lg hover:shadow-[#2E7D32]/40 transition-all active:scale-[0.98] flex items-center justify-center gap-2 mt-auto disabled:opacity-50"
              >
                {isSending ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                ) : (
                  <Send size={20} />
                )}
                {language === "hi" ? "सूचना साझा करें" : "Share Notification"}
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default SarpanchDashboard;
