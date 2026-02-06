import { Sprout, CheckCircle2 } from "lucide-react";
import { useState, useEffect } from "react";
import { getTranslations, getLanguage } from "../utils/languageUtils";

const CropSelect = () => {
  const [selectedId, setSelectedId] = useState(null);
  const [language, setLanguage] = useState("hi");

  useEffect(() => {
    const savedLanguage = getLanguage();
    if (savedLanguage) {
      setLanguage(savedLanguage);
    }
  }, []);

  const t = getTranslations(language);

  const crops = [
    {
      id: "sugarcane",
      name: t.crops.cropNames.sugarcane,
      image: "/sugarcane.webp",
      waterNeed: "high",
    },
    {
      id: "paddy",
      name: t.crops.cropNames.paddy,
      image: "/rice.webp",
      waterNeed: "high",
    },
    {
      id: "wheat",
      name: t.crops.cropNames.wheat,
      image: "/wheat.webp",
      waterNeed: "medium",
    },
    {
      id: "mustard",
      name: t.crops.cropNames.mustard,
      image: "/mustard.webp",
      waterNeed: "low",
    },
    {
      id: "chickpea",
      name: t.crops.cropNames.chickpea,
      image: "/chickpea.webp",
      waterNeed: "low",
    },
    {
      id: "cotton",
      name: t.crops.cropNames.cotton,
      image: "/cotton.webp",
      waterNeed: "medium",
    },
  ];

  const handleSelect = (crop) => {
    setSelectedId(crop.id);
    console.log("Selected crop:", crop);
    // Optionally navigate to advice page or store selection
  };

  // --- REUSABLE GLASS STYLES (MATCHING PREVIOUS SCREEN) ---
  // Gradient top-to-bottom, very subtle border, soft blur.
  const glassCardClass =
    "bg-gradient-to-b from-white/20 to-white/5 backdrop-blur-xl border border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.1)]";
  const glassPillClass =
    "bg-gradient-to-b from-white/20 to-white/5 backdrop-blur-lg border border-white/10 shadow-sm";

  return (
    <div className="h-screen bg-[#FAFAF7] font-hindi overflow-hidden relative flex flex-col">
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
      {/* Dark Overlay - Matched to previous screen opacity (80->50) */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#422B06]/80 to-[#422B06]/50" />

      <div className="relative z-10 max-w-md lg:max-w-5xl mx-auto px-5 pt-4 pb-28 md:pb-8 md:pt-24 flex flex-col flex-1 h-full w-full overflow-hidden">
        {/* Enhanced Header - Using glassPillClass */}
        <header
          className={`mb-6 ${glassPillClass} p-5 rounded-[2.5rem] flex-shrink-0`}
        >
          <div className="flex items-center gap-4">
            <div className="bg-gradient-to-br from-[#2E7D32] to-[#43A047] p-3.5 rounded-2xl shadow-lg ring-2 ring-white/10">
              <Sprout size={32} className="text-white" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-black text-white drop-shadow-md">
                {t.crops.title}
              </h1>
              <p className="text-sm md:text-base font-bold text-white/80">
                {t.crops.subtitle}
              </p>
            </div>
          </div>
        </header>

        {/* Crop Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 flex-1 content-start overflow-y-auto pr-1 pb-4 custom-scrollbar">
          {crops.map((crop) => {
            const isSelected = selectedId === crop.id;

            return (
              <button
                key={crop.id}
                onClick={() => handleSelect(crop)}
                className={`
                  relative group overflow-hidden
                  backdrop-blur-xl rounded-[2.5rem] 
                  transition-all duration-300
                  p-6 flex flex-col items-center justify-center gap-3
                  active:scale-95
                  ${
                    isSelected
                      ? "bg-gradient-to-b from-white/30 to-white/10 border-2 border-[#43A047] shadow-[0_0_30px_rgba(67,160,71,0.3)] scale-[1.02]"
                      : "bg-gradient-to-b from-white/20 to-white/5 border border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.1)] hover:from-white/25 hover:to-white/10"
                  }
                `}
              >
                {/* Selection Ribbon/Checkmark */}
                {isSelected && (
                  <div className="absolute top-4 right-4 text-[#43A047] animate-in zoom-in duration-300 drop-shadow-md">
                    <CheckCircle2
                      size={28}
                      fill="white"
                      className="stroke-[#2E7D32]"
                    />
                  </div>
                )}

                {/* Crop Image with dynamic shadow */}
                <div className="relative pointer-events-none">
                  <img
                    src={crop.image}
                    alt={crop.name}
                    className={`w-20 h-20 md:w-28 md:h-28 object-contain drop-shadow-2xl transition-transform duration-500 
                      ${isSelected ? "scale-110" : "group-hover:scale-105"}`}
                  />
                  {isSelected && (
                    <div className="absolute inset-0 bg-[#43A047]/20 blur-2xl -z-10 rounded-full" />
                  )}
                </div>

                <div className="text-xl md:text-2xl font-black text-white drop-shadow-md mt-2">
                  {crop.name}
                </div>

                {/* Water Need Tag */}
                <div
                  className={`
                    text-xs md:text-sm font-black px-4 py-1.5 rounded-full shadow-lg border border-white/10 backdrop-blur-sm
                    ${crop.waterNeed === "high" ? "bg-blue-600/80 text-white" : ""}
                    ${crop.waterNeed === "medium" ? "bg-orange-500/80 text-white" : ""}
                    ${crop.waterNeed === "low" ? "bg-green-600/80 text-white" : ""}
                  `}
                >
                  {crop.waterNeed === "high" ? t.crops.waterNeed.high : ""}
                  {crop.waterNeed === "medium" ? t.crops.waterNeed.medium : ""}
                  {crop.waterNeed === "low" ? t.crops.waterNeed.low : ""}
                </div>

                {/* Selection Glow Effect */}
                {isSelected && (
                  <div className="absolute inset-0 bg-gradient-to-t from-[#2E7D32]/10 to-transparent pointer-events-none" />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default CropSelect;
