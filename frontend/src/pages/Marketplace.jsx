import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
    Droplets,
    TrendingUp,
    MapPin,
    CheckCircle2,
    Loader2,
    ArrowLeft,
    Filter,
    DollarSign,
    Clock,
    ChevronDown,
} from "lucide-react";
import { getLanguage } from "../utils/languageUtils";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Marketplace - Water-filtered crop marketplace showing only water-safe crops
 */
const Marketplace = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [language, setLanguage] = useState("hi");
    const [crops, setCrops] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [seasonFilter, setSeasonFilter] = useState("kharif");
    const [showSeasonDropdown, setShowSeasonDropdown] = useState(false);

    // Get water data from location state or use default
    const availableWater = location.state?.water_level_mm || 500;

    // Load language preference
    useEffect(() => {
        const savedLanguage = getLanguage();
        if (savedLanguage) setLanguage(savedLanguage);
    }, []);

    // Fetch marketplace data
    useEffect(() => {
        const fetchMarketplace = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(
                    `${API_BASE}/api/marketplace?available=${availableWater}&season=${seasonFilter}`
                );
                if (!response.ok) throw new Error("Failed to fetch marketplace data");
                const data = await response.json();
                setCrops(data.crops || []);
            } catch (err) {
                console.error("Marketplace fetch error:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchMarketplace();
    }, [availableWater, seasonFilter]);

    // Labels
    const labels = {
        title: language === "hi" ? "💧 जल-सुरक्षित बाज़ार" : "💧 Water-Safe Marketplace",
        subtitle: language === "hi"
            ? `${availableWater}mm पानी बजट के लिए फसलें`
            : `Crops for your ${availableWater}mm water budget`,
        cropsFound: language === "hi" ? "जल-सुरक्षित फसलें" : "water-safe crops",
        waterNeeded: language === "hi" ? "पानी" : "Water",
        uses: language === "hi" ? "उपयोग" : "Uses",
        profit: language === "hi" ? "अनुमानित लाभ" : "Expected Profit",
        perAcre: language === "hi" ? "प्रति एकड़" : "per acre",
        efficiency: language === "hi" ? "दक्षता" : "Efficiency",
        marketInfo: language === "hi" ? "बाज़ार जानकारी" : "Market Info",
        mandi: language === "hi" ? "मंडी" : "Mandi",
        price: language === "hi" ? "मूल्य" : "Price",
        distance: language === "hi" ? "दूरी" : "Distance",
        demand: language === "hi" ? "मांग" : "Demand",
        growthDays: language === "hi" ? "उगाई अवधि" : "Growth",
        days: language === "hi" ? "दिन" : "days",
        waterSafe: language === "hi" ? "जल सुरक्षित" : "Water Safe",
        back: language === "hi" ? "वापस" : "Back",
        nocrops: language === "hi"
            ? "इस बजट के लिए कोई फसल नहीं"
            : "No crops available for this budget",
        season: language === "hi" ? "मौसम" : "Season",
        kharif: language === "hi" ? "खरीफ" : "Kharif",
        rabi: language === "hi" ? "रबी" : "Rabi",
        zaid: language === "hi" ? "ज़ायद" : "Zaid",
    };

    const seasons = [
        { id: "kharif", label: labels.kharif },
        { id: "rabi", label: labels.rabi },
        { id: "zaid", label: labels.zaid },
    ];

    // Get demand color
    const getDemandColor = (level) => {
        switch (level?.toLowerCase()) {
            case "high": return "text-green-400";
            case "moderate": return "text-yellow-400";
            case "low": return "text-red-400";
            default: return "text-gray-400";
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-amber-900 via-amber-800 to-amber-900 flex items-center justify-center">
                <div className="text-center">
                    <Loader2 size={48} className="animate-spin text-white mx-auto mb-4" />
                    <p className="text-white/70">
                        {language === "hi" ? "बाज़ार लोड हो रहा है..." : "Loading marketplace..."}
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-amber-900 via-amber-800 to-amber-900 pb-24 md:pt-20">
            {/* Header */}
            <div className="bg-gradient-to-r from-amber-800/50 to-amber-700/50 backdrop-blur-sm border-b border-white/10 sticky top-0 z-40 md:static">
                <div className="max-w-6xl mx-auto px-4 py-4">
                    <div className="flex items-center gap-4 mb-2">
                        <button
                            onClick={() => navigate(-1)}
                            className="p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
                        >
                            <ArrowLeft size={20} className="text-white" />
                        </button>
                        <h1 className="text-2xl md:text-3xl font-bold text-white">
                            {labels.title}
                        </h1>
                    </div>
                    <p className="text-white/70 ml-12">{labels.subtitle}</p>

                    {/* Stats & Filter Bar */}
                    <div className="flex flex-wrap items-center gap-3 mt-4 ml-12">
                        {/* Crop count badge */}
                        <div className="bg-green-600/80 text-white px-4 py-2 rounded-full text-sm font-bold flex items-center gap-2">
                            <CheckCircle2 size={16} />
                            {crops.length} {labels.cropsFound}
                        </div>

                        {/* Season Filter */}
                        <div className="relative">
                            <button
                                onClick={() => setShowSeasonDropdown(!showSeasonDropdown)}
                                className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-full text-sm font-medium flex items-center gap-2 transition-colors"
                            >
                                <Filter size={16} />
                                {labels.season}: {seasons.find(s => s.id === seasonFilter)?.label}
                                <ChevronDown size={16} className={`transition-transform ${showSeasonDropdown ? "rotate-180" : ""}`} />
                            </button>

                            {showSeasonDropdown && (
                                <div className="absolute top-full left-0 mt-2 bg-amber-800 border border-white/20 rounded-xl shadow-xl overflow-hidden z-50">
                                    {seasons.map(season => (
                                        <button
                                            key={season.id}
                                            onClick={() => {
                                                setSeasonFilter(season.id);
                                                setShowSeasonDropdown(false);
                                            }}
                                            className={`w-full px-4 py-2 text-left text-white hover:bg-white/10 transition-colors ${seasonFilter === season.id ? "bg-white/20" : ""
                                                }`}
                                        >
                                            {season.label}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Error State */}
            {error && (
                <div className="max-w-6xl mx-auto px-4 mt-6">
                    <div className="bg-red-500/20 border border-red-500/30 rounded-xl p-4 text-white">
                        <p className="font-semibold">Error loading marketplace</p>
                        <p className="text-sm text-white/70">{error}</p>
                    </div>
                </div>
            )}

            {/* Crop Grid */}
            <div className="max-w-6xl mx-auto px-4 py-6">
                {crops.length > 0 ? (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
                        {crops.map((crop, idx) => (
                            <div
                                key={crop.id || idx}
                                className="bg-white/10 backdrop-blur-sm rounded-2xl p-5 border border-white/10 hover:border-white/20 hover:bg-white/15 transition-all duration-300 group"
                            >
                                {/* Header */}
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h3 className="text-xl font-bold text-white group-hover:text-green-300 transition-colors">
                                            {language === "hi" ? crop.name_hi || crop.name : crop.name}
                                        </h3>
                                        <span className="inline-flex items-center gap-1 bg-green-600/80 text-white text-xs px-3 py-1 rounded-full mt-2">
                                            <CheckCircle2 size={12} />
                                            {labels.waterSafe}
                                        </span>
                                    </div>
                                    {/* Rank Badge */}
                                    <div className="bg-amber-600/80 text-white text-xs font-bold px-2 py-1 rounded-full">
                                        #{idx + 1}
                                    </div>
                                </div>

                                {/* Water Stats */}
                                <div className="grid grid-cols-3 gap-2 mb-4">
                                    <div className="bg-blue-900/30 rounded-xl p-3 text-center">
                                        <Droplets size={16} className="text-blue-400 mx-auto mb-1" />
                                        <div className="text-lg font-bold text-white">{crop.water_mm}mm</div>
                                        <div className="text-xs text-gray-400">{labels.waterNeeded}</div>
                                    </div>
                                    <div className="bg-blue-900/30 rounded-xl p-3 text-center">
                                        <TrendingUp size={16} className="text-cyan-400 mx-auto mb-1" />
                                        <div className="text-lg font-bold text-white">{crop.water_percentage}%</div>
                                        <div className="text-xs text-gray-400">{labels.uses}</div>
                                    </div>
                                    <div className="bg-blue-900/30 rounded-xl p-3 text-center">
                                        <Clock size={16} className="text-purple-400 mx-auto mb-1" />
                                        <div className="text-lg font-bold text-white">{crop.growth_days}</div>
                                        <div className="text-xs text-gray-400">{labels.days}</div>
                                    </div>
                                </div>

                                {/* Profit Section */}
                                <div className="bg-green-900/30 rounded-xl p-4 mb-4">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-gray-300 text-sm">{labels.profit}</span>
                                        <DollarSign size={18} className="text-green-400" />
                                    </div>
                                    <div className="text-2xl font-black text-green-400">
                                        ₹{crop.profit_per_acre?.toLocaleString() || "N/A"}
                                    </div>
                                    <div className="text-xs text-gray-400">{labels.perAcre}</div>
                                    <div className="mt-2 pt-2 border-t border-white/10 flex justify-between text-xs">
                                        <span className="text-gray-400">{labels.efficiency}</span>
                                        <span className="text-green-400 font-bold">₹{crop.profit_per_drop}/mm</span>
                                    </div>
                                </div>

                                {/* Buyer/Market Signal */}
                                {crop.buyer_signal && (
                                    <div className="bg-orange-900/30 rounded-xl p-4">
                                        <div className="flex items-center gap-2 text-orange-300 text-xs mb-3">
                                            <MapPin size={14} />
                                            {labels.marketInfo}
                                        </div>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-gray-400">{labels.mandi}</span>
                                                <span className="text-white font-medium truncate max-w-[150px]">
                                                    {crop.buyer_signal.mandi_name}
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-400">{labels.price}</span>
                                                <span className="text-white font-medium">
                                                    ₹{crop.buyer_signal.price_per_quintal}/q
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-400">{labels.distance}</span>
                                                <span className="text-white font-medium">
                                                    {crop.buyer_signal.distance_km}km
                                                </span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-400">{labels.demand}</span>
                                                <span className={`font-bold capitalize ${getDemandColor(crop.buyer_signal.demand_level)}`}>
                                                    {crop.buyer_signal.demand_level}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                ) : (
                    /* Empty State */
                    <div className="text-center py-16">
                        <div className="text-6xl mb-4">💧</div>
                        <p className="text-xl text-white font-medium">{labels.nocrops}</p>
                        <p className="text-white/60 mt-2">
                            {language === "hi"
                                ? "जल संरक्षण या रिचार्ज विधियों पर विचार करें"
                                : "Consider water conservation or recharge methods"}
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Marketplace;
