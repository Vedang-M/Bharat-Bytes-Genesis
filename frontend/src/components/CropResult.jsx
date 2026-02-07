import {
  Leaf,
  Droplet,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Loader2,
  ArrowLeft,
} from "lucide-react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getTranslations, getLanguage } from "../utils/languageUtils";
import { checkCropViability, getSmartSwap } from "../utils/apiUtils";
import { getSavedLocation } from "../utils/locationUtils";
import FertilizerAd from "./FertilizerAd";

const CropResult = ({ selectedCrop: propSelectedCrop }) => {
  const navigate = useNavigate();
  const [language, setLanguage] = useState("hi");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cropData, setCropData] = useState(null);
  const [alternatives, setAlternatives] = useState([]);

  useEffect(() => {
    const savedLanguage = getLanguage();
    if (savedLanguage) {
      setLanguage(savedLanguage);
    }
  }, []);

  const t = getTranslations(language);

  // Get selected crop from props or sessionStorage
  const getSelectedCrop = () => {
    if (propSelectedCrop) return propSelectedCrop;
    try {
      const stored = sessionStorage.getItem("selectedCrop");
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  };

  // Get cached water data from sessionStorage
  const getCachedWaterData = (currentLat, currentLon) => {
    try {
      const stored = sessionStorage.getItem('waterData');
      if (!stored) return null;
      const data = JSON.parse(stored);
      // Check if data is recent (within 10 minutes) and for same location
      const isRecent = Date.now() - data.timestamp < 10 * 60 * 1000;
      // Check if location matches (within ~100m)
      const latMatch = Math.abs(data.lat - currentLat) < 0.001;
      const lonMatch = Math.abs(data.lon - currentLon) < 0.001;
      return (isRecent && latMatch && lonMatch) ? data : null;
    } catch {
      return null;
    }
  };

  // Fetch crop viability on mount
  useEffect(() => {
    const fetchCropViability = async () => {
      const selectedCrop = getSelectedCrop();
      const location = getSavedLocation();
      
      if (!selectedCrop?.id) {
        setError("No crop selected");
        setIsLoading(false);
        return;
      }

      const lat = selectedCrop.latitude || location?.latitude;
      const lon = selectedCrop.longitude || location?.longitude;

      if (!lat || !lon) {
        setError("Location not available");
        setIsLoading(false);
        return;
      }

      // Get cached water data if available for consistent values
      const cachedWater = getCachedWaterData(lat, lon);
      const waterMm = cachedWater?.waterAvailability || null;

      setIsLoading(true);
      try {
        const data = await checkCropViability(selectedCrop.id, lat, lon, waterMm);
        
        setCropData({
          id: data.crop_id,
          name: language === "hi" ? data.crop_name_hi : data.crop_name,
          nameHi: data.crop_name_hi,
          nameEn: data.crop_name,
          image: selectedCrop.image || `/${data.crop_id}.webp`,
          waterNeed: selectedCrop.waterNeed || "medium",
          recommendation: data.recommendation,
          waterRequired: data.water_required_mm,
          availableWater: data.water_available_mm,
          waterRatio: data.water_ratio,
          waterDeficit: data.water_deficit_mm,
          message: data.message,
          messageEn: data.message_en,
          isViable: data.is_viable,
          yieldPrediction: data.is_viable 
            ? t.advice.defaultYield 
            : t.advice.yieldReduced,
          tips: data.is_viable 
            ? t.advice.defaultTips 
            : t.advice.waterSavingTips,
        });

        // If crop is not recommended, fetch alternatives
        if (data.recommendation === "not-recommended" && data.water_available_mm > 0) {
          try {
            const altData = await getSmartSwap(data.crop_id, data.water_available_mm, 3);
            setAlternatives(altData.recommendations || []);
          } catch (altErr) {
            console.error("Error fetching alternatives:", altErr);
          }
        }
      } catch (err) {
        console.error("Error fetching crop viability:", err);
        setError(err.message);
        
        // Use fallback data
        const fallbackCrop = getSelectedCrop();
        setCropData({
          id: fallbackCrop?.id || "wheat",
          name: fallbackCrop?.name || t.crops.cropNames.wheat,
          image: fallbackCrop?.image || "/wheat.webp",
          waterNeed: fallbackCrop?.waterNeed || "medium",
          recommendation: "caution",
          waterRequired: 450,
          availableWater: 400,
          yieldPrediction: t.advice.defaultYield,
          tips: t.advice.defaultTips,
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchCropViability();
  }, [language]);

  const recommendationConfig = {
    suitable: {
      color: "#2E7D32",
      gradient: "from-[#2E7D32] to-[#43A047]",
      icon: CheckCircle2,
      label: t.advice.recommendation.suitable,
      message: t.advice.messages.suitable,
    },
    caution: {
      color: "#F9A825",
      gradient: "from-[#F9A825] to-[#FBC02D]",
      icon: AlertCircle,
      label: t.advice.recommendation.caution,
      message: t.advice.messages.caution,
    },
    "not-recommended": {
      color: "#E53935",
      gradient: "from-[#E53935] to-[#EF5350]",
      icon: AlertCircle,
      label: t.advice.recommendation.notRecommended,
      message: t.advice.messages.notRecommended,
    },
  };

  const current = recommendationConfig[cropData?.recommendation] || recommendationConfig.caution;
  const Icon = current.icon;

  // --- REUSABLE GLASS STYLES (MATCHING PREVIOUS SCREENS) ---
  const glassCardClass =
    "bg-gradient-to-b from-white/20 to-white/5 backdrop-blur-xl border border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.1)]";
  const glassPillClass =
    "bg-gradient-to-b from-white/20 to-white/5 backdrop-blur-lg border border-white/10 shadow-sm";

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#FAFAF7] font-hindi relative flex flex-col items-center justify-center">
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
        <div className="relative z-10 flex flex-col items-center gap-4">
          <Loader2 size={48} className="text-white animate-spin" />
          <p className="text-white text-xl font-bold">
            {language === "hi" ? "फसल विश्लेषण हो रहा है..." : "Analyzing crop..."}
          </p>
        </div>
      </div>
    );
  }

  // If no crop data available
  if (!cropData) {
    return (
      <div className="min-h-screen bg-[#FAFAF7] font-hindi relative flex flex-col items-center justify-center">
        <p className="text-xl">{error || "No crop data available"}</p>
        <button 
          onClick={() => navigate("/crops")}
          className="mt-4 px-6 py-3 bg-green-600 text-white rounded-full"
        >
          {language === "hi" ? "फसल चुनें" : "Select Crop"}
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAF7] font-hindi relative flex flex-col">
      {/* Hero Background Images */}
      <img
        src="/Hero-image-desktop.webp"
        alt=""
        className="absolute inset-0 w-full h-full object-cover object-center hidden md:block"
      />
      <img
        src="/Hero-inmage-mobile.webp"
        alt=""
        className="absolute inset-0 w-full h-full object-cover object-center block md:hidden"
      />
      {/* Dark Overlay - Consistent opacity */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#422B06]/80 to-[#422B06]/50" />

      <div className="relative z-10 max-w-md lg:max-w-5xl mx-auto px-5 pt-4 pb-28 md:pb-8 md:pt-24 flex flex-col flex-1 w-full overflow-y-auto md:overflow-hidden md:h-full">
        {/* Header - Using glassPillClass */}
        <header
          className={`mb-6 ${glassPillClass} p-5 rounded-[2.5rem] flex-shrink-0`}
        >
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="bg-gradient-to-br from-[#2E7D32] to-[#43A047] p-3.5 rounded-2xl shadow-lg ring-2 ring-white/10">
                <Leaf size={32} className="text-white" />
              </div>
            </div>
            <div className="flex-1">
              <h1 className="text-2xl md:text-3xl font-black text-white drop-shadow-md">
                {t.advice.title}
              </h1>
              <p className="text-sm md:text-base font-bold text-white/80">
                {cropData.name} {t.advice.subtitle}
              </p>
            </div>
          </div>
        </header>

        {/* Main Content - Scrollable */}
        <div className="flex-1 overflow-y-auto pr-1 pb-4 custom-scrollbar space-y-6">
          {/* Crop Info Card */}
          <div className={`${glassCardClass} rounded-[2.5rem] p-6`}>
            <div className="flex items-center gap-6">
              <div className="relative">
                <img
                  src={cropData.image}
                  alt={cropData.name}
                  className="w-24 h-24 md:w-28 md:h-28 object-contain drop-shadow-2xl relative z-10"
                />
                {/* Subtle glow behind image */}
                <div className="absolute inset-0 bg-white/20 blur-2xl -z-10 rounded-full" />
              </div>

              <div className="flex-1">
                <h2 className="text-3xl font-black text-white drop-shadow-md mb-2">
                  {cropData.name}
                </h2>
                <div
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r ${current.gradient} shadow-lg ring-1 ring-white/20`}
                >
                  <Icon size={20} className="text-white" />
                  <span className="text-white font-black text-sm uppercase tracking-wide">
                    {current.label}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Recommendation Message */}
          <div className="relative group">
            <div className={`absolute inset-0 ${glassCardClass} rounded-3xl`} />
            <div
              className={`absolute left-0 top-6 bottom-6 w-1.5 rounded-r-lg bg-gradient-to-b ${current.gradient}`}
            />
            <div className="relative p-6 pl-8">
              <p className="text-white font-bold text-lg leading-relaxed drop-shadow-sm">
                {current.message}
              </p>
            </div>
          </div>

          {/* Water Analysis */}
          <div className={`${glassCardClass} rounded-3xl p-6`}>
            <h3 className="text-lg font-black text-white mb-4 flex items-center gap-2 opacity-90">
              <Droplet size={24} className="text-[#90CAF9] drop-shadow-sm" />
              {t.advice.waterAnalysis}
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {/* Inner glass cards for stats */}
              <div className="bg-white/10 border border-white/5 rounded-2xl p-4 backdrop-blur-sm shadow-inner">
                <p className="text-white/70 text-sm font-bold mb-1 uppercase tracking-wider">
                  {t.advice.waterRequired}
                </p>
                <p className="text-white text-2xl font-black drop-shadow-sm">
                  {cropData.waterRequired}{" "}
                  <span className="text-base font-bold text-white/60">mm</span>
                </p>
              </div>
              <div className="bg-white/10 border border-white/5 rounded-2xl p-4 backdrop-blur-sm shadow-inner">
                <p className="text-white/70 text-sm font-bold mb-1 uppercase tracking-wider">
                  {t.advice.waterAvailable}
                </p>
                <p
                  className={`text-2xl font-black drop-shadow-sm ${cropData.availableWater < cropData.waterRequired ? "text-[#FFCDD2]" : "text-white"}`}
                >
                  {cropData.availableWater}{" "}
                  <span className="text-base font-bold text-white/60">mm</span>
                </p>
              </div>
            </div>
          </div>

          {/* Yield Prediction */}
          <div className={`${glassCardClass} rounded-3xl p-6`}>
            <h3 className="text-lg font-black text-white mb-3 flex items-center gap-2 opacity-90">
              <TrendingUp size={24} className="text-[#FFF59D] drop-shadow-sm" />
              {t.advice.yieldPrediction}
            </h3>
            <p className="text-white font-bold text-xl drop-shadow-sm">
              {cropData.yieldPrediction}
            </p>
          </div>

          {/* Tips */}
          <div className={`${glassCardClass} rounded-3xl p-6`}>
            <h3 className="text-lg font-black text-white mb-5 opacity-90 uppercase tracking-wide text-sm">
              💡 {t.advice.tips}
            </h3>
            <ul className="space-y-4">
              {(cropData.tips || []).map((tip, index) => (
                <li key={index} className="flex items-start gap-4">
                  <div className="bg-white/10 border border-white/10 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 shadow-sm">
                    <span className="text-white text-sm font-black">
                      {index + 1}
                    </span>
                  </div>
                  <span className="text-white font-medium text-lg leading-snug pt-0.5">
                    {tip}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          {/* Fertilizer Ad - Government Approved */}
          <FertilizerAd 
            crop={cropData.id} 
            region={getSavedLocation()?.state || getSavedLocation()?.district}
            language={language}
          />
        </div>
      </div>
    </div>
  );
};

export default CropResult;
