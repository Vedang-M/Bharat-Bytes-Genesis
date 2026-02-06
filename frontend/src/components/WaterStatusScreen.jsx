import {
  Droplet,
  MapPin,
  ChevronRight,
  Info,
  AlertTriangle,
  CheckCircle,
  MapPinned,
} from "lucide-react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getTranslations, getLanguage } from "../utils/languageUtils";
import {
  getSavedLocation,
  getUserLocation,
  formatLocation,
} from "../utils/locationUtils";

const WaterStatusScreen = () => {
  const navigate = useNavigate();
  const [currentLanguage, setCurrentLanguage] = useState("hi");
  const [userLocation, setUserLocation] = useState(getSavedLocation());
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);

  // Read language from localStorage on mount and when it changes
  useEffect(() => {
    const savedLanguage = getLanguage();
    if (savedLanguage) {
      setCurrentLanguage(savedLanguage);
    }
  }, []);

  const t = getTranslations(currentLanguage).waterStatus;

  // Handle location fetching
  const handleFetchLocation = async () => {
    setIsLoadingLocation(true);
    try {
      const locationData = await getUserLocation();
      setUserLocation(locationData);
    } catch (error) {
      alert(error.message || "Unable to get location. Please try again.");
    } finally {
      setIsLoadingLocation(false);
    }
  };

  // Get user's location from state
  const locationDisplay = userLocation
    ? {
        city: userLocation.city ?? userLocation.district ?? "—",
        state: userLocation.state ?? "—",
      }
    : {
        city: "—",
        state: "—",
      };

  const MAX_WATER_CAPACITY = 1000;
  const waterData = {
    location: locationDisplay,
    waterAvailability: 400,
    status: "limited",
  };

  const statusConfig = {
    safe: {
      color: "#2E7D32",
      gradient: "from-[#2E7D32] to-[#43A047]",
      icon: CheckCircle,
      label: t.status.safe,
      advisory: t.advisory.safe,
    },
    limited: {
      color: "#F9A825",
      gradient: "from-[#F9A825] to-[#FBC02D]",
      icon: Info,
      label: t.status.limited,
      advisory: t.advisory.limited,
    },
    critical: {
      color: "#E53935",
      gradient: "from-[#E53935] to-[#EF5350]",
      icon: AlertTriangle,
      label: t.status.critical,
      advisory: t.advisory.critical,
    },
  };

  const current = statusConfig[waterData.status];
  const Icon = current.icon;

  const size = 260;
  const strokeWidth = 24;
  const radius = (size - strokeWidth) / 2 - 5;
  const center = size / 2;
  const circumference = 2 * Math.PI * radius;
  const percentage = Math.min(
    Math.max((waterData.waterAvailability / MAX_WATER_CAPACITY) * 100, 5),
    100,
  );
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  // --- REUSABLE GLASS STYLES ---
  // This replicates the image: Gradient top-to-bottom, very subtle border, soft blur.
  const glassCardClass =
    "bg-gradient-to-b from-white/20 to-white/5 backdrop-blur-xl border border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.1)]";
  const glassPillClass =
    "bg-gradient-to-b from-white/20 to-white/5 backdrop-blur-lg border border-white/10 shadow-sm";

  return (
    <div className="h-screen bg-[#FAFAF7] font-hindi overflow-hidden relative flex flex-col">
      {/* Background Images */}
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
      {/* Dark Overlay - slightly adjusted to match the warmth of the reference */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#422B06]/80 to-[#422B06]/50" />

      <div className="relative z-10 max-w-md lg:max-w-5xl mx-auto px-5 pt-4 pb-32 md:pb-10 md:pt-24 flex flex-col flex-1 h-full w-full justify-between gap-6">
        {/* Header - Using glassPillClass to match other pages */}
        <header
          className={`flex justify-between items-center ${glassPillClass} p-5 rounded-[2.5rem] flex-shrink-0`}
        >
          <div className="flex flex-col justify-center flex-1">
            <span className="text-xs font-bold text-white/70 uppercase tracking-wider mb-0.5">
              {t.header}
            </span>
            <div className="flex items-center gap-1.5 flex-wrap">
              <MapPin size={18} className="text-[#A5D6A7]" />
              <h2 className="text-lg font-black text-white drop-shadow-sm leading-none pb-0.5">
                {waterData.location.city}, {waterData.location.state}
              </h2>
              <button
                onClick={handleFetchLocation}
                disabled={isLoadingLocation}
                className="
                  ml-2 flex items-center gap-1.5 px-3 py-1.5 rounded-full
                  bg-white/20 hover:bg-white/30 border border-white/30
                  text-xs font-bold text-white
                  transition-all active:scale-95
                  disabled:opacity-50 disabled:cursor-not-allowed
                "
              >
                <MapPinned size={14} />
                {isLoadingLocation ? t.fetchingLocation : t.fetchLocation}
                {isLoadingLocation && (
                  <span className="h-3 w-3 animate-spin rounded-full border-2 border-white border-t-transparent" />
                )}
              </button>
            </div>
          </div>
          <div
            className={`h-10 w-10 rounded-full flex items-center justify-center bg-gradient-to-br ${current.gradient} text-white shadow-lg ring-2 ring-white/10 flex-shrink-0`}
          >
            <Icon size={20} />
          </div>
        </header>

        {/* Main Grid */}
        <main className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 items-center min-h-0">
          {/* LEFT SECTION: Gauge Card */}
          <div className="relative flex flex-col items-center justify-center h-full">
            {/* Applied glassCardClass here and rounded-3xl to match reference "soft" corners */}
            <div
              className={`relative z-10 w-full ${glassCardClass} rounded-[2.5rem] p-8 flex flex-col items-center`}
            >
              <div
                className="relative flex items-center justify-center mb-6"
                style={{ width: size, height: size }}
              >
                <svg
                  width={size}
                  height={size}
                  className="transform -rotate-90 drop-shadow-lg"
                >
                  <circle
                    cx={center}
                    cy={center}
                    r={radius}
                    stroke="rgba(255,255,255,0.1)" // More subtle track
                    strokeWidth={strokeWidth}
                    fill="transparent"
                  />
                  <circle
                    cx={center}
                    cy={center}
                    r={radius}
                    stroke={current.color}
                    strokeWidth={strokeWidth}
                    fill="transparent"
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                    strokeLinecap="round"
                    className="transition-all duration-1000 ease-in-out"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center pt-2">
                  {/* Inner small glass bubble */}
                  <div className="bg-white/10 p-3 rounded-full shadow-inner mb-2 backdrop-blur-sm border border-white/5">
                    <Droplet
                      size={32}
                      fill="white"
                      className="text-white drop-shadow-md"
                    />
                  </div>
                  <span className="text-7xl font-black text-white drop-shadow-md tracking-tighter leading-none">
                    {waterData.waterAvailability}
                  </span>
                  <span className="text-sm font-bold text-white/60 uppercase tracking-widest mt-2">
                    {t.unit}
                  </span>
                </div>
              </div>

              <div
                className={`px-8 py-3 rounded-xl bg-gradient-to-r ${current.gradient} shadow-lg flex items-center gap-3 transform translate-y-2 ring-1 ring-white/20`}
              >
                <span className="text-white font-black text-lg tracking-wide uppercase">
                  {current.label}
                </span>
              </div>
            </div>

            {/* Ambient Glow */}
            <div
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[70%] h-[70%] rounded-full blur-[80px] -z-10 opacity-40"
              style={{ backgroundColor: current.color }}
            />
          </div>

          {/* RIGHT SECTION */}
          <div className="flex flex-col gap-6 justify-center h-full">
            {/* Advisory Box - Applied glassCardClass */}
            <div className="relative group">
              <div
                className={`absolute inset-0 ${glassCardClass} rounded-3xl`}
              />
              <div
                className={`absolute left-0 top-6 bottom-6 w-1.5 rounded-r-lg bg-gradient-to-b ${current.gradient}`}
              />
              <div className="relative p-6 pl-8">
                <h3 className="text-xs font-bold text-white/60 uppercase mb-2 flex items-center gap-2 tracking-wider">
                  <Info size={16} /> सलाहकार संदेश
                </h3>
                <p className="text-white font-bold text-lg leading-relaxed drop-shadow-sm">
                  {current.advisory}
                </p>
              </div>
            </div>

            {/* CTA Button */}
            <button
              onClick={() => navigate("/crops")}
              className="group bg-[#2E7D32] text-white rounded-[2rem] p-2 pl-8 pr-2 h-20 flex items-center justify-between shadow-xl shadow-[#2E7D32]/20 border border-[#2E7D32]/50 active:scale-[0.98] transition-all"
            >
              <span className="text-xl font-black tracking-wide">{t.cta}</span>
              <div className="bg-white/20 rounded-full h-16 w-16 flex items-center justify-center group-hover:bg-white/30 transition-colors border border-white/10">
                <ChevronRight size={32} strokeWidth={3} />
              </div>
            </button>
          </div>
        </main>
      </div>
    </div>
  );
};

export default WaterStatusScreen;
