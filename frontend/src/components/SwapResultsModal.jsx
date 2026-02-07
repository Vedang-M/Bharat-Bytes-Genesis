import { X, Droplets, TrendingUp, MapPin, AlertTriangle, CheckCircle2, Leaf, DollarSign } from "lucide-react";

/**
 * SwapResultsModal - Displays crop viability assessment and swap recommendations
 * Shows current crop risk level and up to 3 alternative crops ranked by profit-per-drop
 */
const SwapResultsModal = ({ results, onClose, language = "en" }) => {
    if (!results) return null;

    // Get risk level color
    const getRiskColor = (risk) => {
        switch (risk) {
            case "SAFE":
                return "bg-green-600";
            case "MODERATE":
                return "bg-yellow-600";
            case "RISKY":
                return "bg-orange-600";
            case "CRITICAL":
                return "bg-red-600";
            default:
                return "bg-gray-600";
        }
    };

    // Get risk level icon
    const getRiskIcon = (risk) => {
        switch (risk) {
            case "SAFE":
                return <CheckCircle2 size={20} />;
            case "MODERATE":
                return <AlertTriangle size={20} />;
            case "RISKY":
            case "CRITICAL":
                return <AlertTriangle size={20} />;
            default:
                return null;
        }
    };

    // Get demand level styling
    const getDemandStyle = (level) => {
        switch (level?.toLowerCase()) {
            case "high":
                return "text-green-400 font-semibold";
            case "moderate":
                return "text-yellow-400";
            case "low":
                return "text-red-400";
            default:
                return "text-gray-400";
        }
    };

    // Labels based on language
    const labels = {
        currentCropAssessment: language === "hi" ? "वर्तमान फसल मूल्यांकन" : "Current Crop Assessment",
        waterDeficit: language === "hi" ? "पानी की कमी" : "Water Deficit",
        waterSurplus: language === "hi" ? "पानी का अधिशेष" : "Water Surplus",
        betterAlternatives: language === "hi" ? "बेहतर विकल्प" : "Better Alternatives",
        waterNeeded: language === "hi" ? "पानी की जरूरत" : "Water Needed",
        usesWater: language === "hi" ? "पानी उपयोग" : "Uses",
        ofAvailable: language === "hi" ? "उपलब्ध का" : "of available",
        marketInfo: language === "hi" ? "बाजार की जानकारी" : "Market Info",
        mandi: language === "hi" ? "मंडी" : "Mandi",
        price: language === "hi" ? "मूल्य" : "Price",
        distance: language === "hi" ? "दूरी" : "Distance",
        demand: language === "hi" ? "मांग" : "Demand",
        perAcre: language === "hi" ? "प्रति एकड़" : "per acre",
        profitPerDrop: language === "hi" ? "प्रति बूंद लाभ" : "Profit-per-drop",
        waterSafe: language === "hi" ? "पानी सुरक्षित" : "Water Safe",
        close: language === "hi" ? "बंद करें" : "Close",
        viabilityScore: language === "hi" ? "व्यवहार्यता स्कोर" : "Viability Score",
        waterSaving: language === "hi" ? "पानी की बचत" : "Water Saving",
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in duration-200">
            <div className="bg-gradient-to-br from-amber-900 via-amber-800 to-amber-900 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-white/10">

                {/* Modal Header */}
                <div className="sticky top-0 bg-gradient-to-r from-amber-900 to-amber-800 p-5 border-b border-white/10 flex items-center justify-between rounded-t-2xl">
                    <h2 className="text-xl md:text-2xl font-bold text-white flex items-center gap-2">
                        <Leaf className="text-green-400" size={24} />
                        {labels.currentCropAssessment}
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-full hover:bg-white/10 transition-colors"
                    >
                        <X size={24} className="text-white/70 hover:text-white" />
                    </button>
                </div>

                <div className="p-5 md:p-6 space-y-6">
                    {/* Current Crop Assessment */}
                    <div className="bg-white/10 backdrop-blur rounded-xl p-5">
                        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
                            <div>
                                <h3 className="text-2xl font-bold text-white capitalize">
                                    {results.current_crop}
                                </h3>
                                <p className="text-white/60 text-sm">
                                    {language === "hi" ? "पानी की आवश्यकता" : "Water Required"}: {results.current_crop_water_mm || "N/A"}mm
                                </p>
                            </div>

                            {/* Risk Badge */}
                            <div className={`${getRiskColor(results.risk_level)} px-4 py-2 rounded-full flex items-center gap-2 text-white font-bold shadow-lg`}>
                                {getRiskIcon(results.risk_level)}
                                {results.risk_level}
                            </div>
                        </div>

                        {/* Explanation */}
                        <p className="text-white/90 mb-4 leading-relaxed">{results.explanation}</p>

                        {/* Water Gap Alert */}
                        {results.water_gap_mm < 0 ? (
                            <div className="bg-red-900/40 border border-red-500/50 rounded-xl p-4 flex items-start gap-3">
                                <AlertTriangle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
                                <div>
                                    <strong className="text-red-300">{labels.waterDeficit}:</strong>
                                    <span className="text-white ml-2">
                                        {Math.abs(results.water_gap_mm)}mm {language === "hi" ? "कम" : "short"}
                                    </span>
                                </div>
                            </div>
                        ) : (
                            <div className="bg-green-900/40 border border-green-500/50 rounded-xl p-4 flex items-start gap-3">
                                <CheckCircle2 className="text-green-400 flex-shrink-0 mt-0.5" size={20} />
                                <div>
                                    <strong className="text-green-300">{labels.waterSurplus}:</strong>
                                    <span className="text-white ml-2">
                                        +{results.water_gap_mm}mm {language === "hi" ? "अतिरिक्त" : "available"}
                                    </span>
                                </div>
                            </div>
                        )}

                        {/* Viability Score */}
                        {results.viability_score !== undefined && (
                            <div className="mt-4 flex items-center gap-4">
                                <span className="text-white/60 text-sm">{labels.viabilityScore}:</span>
                                <div className="flex-1 bg-white/10 rounded-full h-3 overflow-hidden">
                                    <div
                                        className={`h-full transition-all duration-500 ${results.viability_score >= 70 ? "bg-green-500" :
                                                results.viability_score >= 40 ? "bg-yellow-500" : "bg-red-500"
                                            }`}
                                        style={{ width: `${results.viability_score}%` }}
                                    />
                                </div>
                                <span className="text-white font-bold text-lg">{results.viability_score}/100</span>
                            </div>
                        )}
                    </div>

                    {/* Alternatives Section */}
                    {results.alternatives && results.alternatives.length > 0 && (
                        <div>
                            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                                <TrendingUp className="text-green-400" size={22} />
                                {labels.betterAlternatives}
                            </h3>

                            <div className="space-y-4">
                                {results.alternatives.map((alt, idx) => (
                                    <div
                                        key={idx}
                                        className="bg-white/10 backdrop-blur rounded-xl p-5 hover:bg-white/15 transition-colors border border-white/5"
                                    >
                                        {/* Crop Header */}
                                        <div className="flex justify-between items-start mb-4">
                                            <div>
                                                <h4 className="text-lg font-bold text-white">{alt.crop_name}</h4>
                                                <span className="inline-flex items-center gap-1 bg-green-600/80 text-white text-xs px-3 py-1 rounded-full mt-1">
                                                    <CheckCircle2 size={12} />
                                                    {labels.waterSafe}
                                                </span>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-2xl font-black text-green-400">
                                                    ₹{alt.profit_estimate_per_acre?.toLocaleString() || "N/A"}
                                                </div>
                                                <div className="text-xs text-gray-300">{labels.perAcre}</div>
                                            </div>
                                        </div>

                                        {/* Water Info Grid */}
                                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
                                            <div className="bg-white/5 rounded-lg p-3">
                                                <div className="flex items-center gap-1 text-blue-400 text-xs mb-1">
                                                    <Droplets size={14} />
                                                    {labels.waterNeeded}
                                                </div>
                                                <div className="font-bold text-white">{alt.water_requirement_mm}mm</div>
                                            </div>
                                            <div className="bg-white/5 rounded-lg p-3">
                                                <div className="text-gray-400 text-xs mb-1">{labels.usesWater}</div>
                                                <div className="font-bold text-white">
                                                    {alt.water_percentage?.toFixed(0) || "N/A"}% {labels.ofAvailable}
                                                </div>
                                            </div>
                                            {alt.water_saving_percent > 0 && (
                                                <div className="bg-green-900/30 rounded-lg p-3">
                                                    <div className="text-green-400 text-xs mb-1">{labels.waterSaving}</div>
                                                    <div className="font-bold text-green-300">{alt.water_saving_percent}%</div>
                                                </div>
                                            )}
                                        </div>

                                        {/* Buyer/Market Signal */}
                                        {alt.buyer_signal && (
                                            <div className="bg-blue-900/30 rounded-xl p-4 mb-4">
                                                <div className="flex items-center gap-1 text-blue-300 text-xs mb-3">
                                                    <MapPin size={14} />
                                                    {labels.marketInfo}
                                                </div>
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                                                    <div>
                                                        <span className="text-gray-400 text-xs">{labels.mandi}</span>
                                                        <div className="text-white font-medium truncate">
                                                            {alt.buyer_signal.mandi_name || "Local Mandi"}
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-400 text-xs">{labels.price}</span>
                                                        <div className="text-white font-medium">
                                                            ₹{alt.buyer_signal.price_per_quintal || alt.buyer_signal.price || "N/A"}/q
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-400 text-xs">{labels.distance}</span>
                                                        <div className="text-white font-medium">
                                                            {alt.buyer_signal.distance_km || "N/A"}km
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-400 text-xs">{labels.demand}</span>
                                                        <div className={getDemandStyle(alt.buyer_signal.demand_level)}>
                                                            {alt.buyer_signal.demand_level || "moderate"}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* Reasoning */}
                                        <div className="text-sm text-gray-300 italic border-l-4 border-green-500/50 pl-4 py-1">
                                            {alt.reasoning}
                                        </div>

                                        {/* Efficiency Metric */}
                                        <div className="mt-4 flex items-center gap-2 text-xs text-gray-400">
                                            <DollarSign size={14} className="text-green-400" />
                                            {labels.profitPerDrop}:
                                            <span className="text-green-400 font-bold">
                                                ₹{alt.profit_per_drop?.toFixed(2) || "N/A"}/mm
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* No Alternatives Message */}
                    {(!results.alternatives || results.alternatives.length === 0) && results.is_water_safe && (
                        <div className="bg-green-900/30 border border-green-500/30 rounded-xl p-5 text-center">
                            <CheckCircle2 size={48} className="text-green-400 mx-auto mb-3" />
                            <p className="text-white font-medium">
                                {language === "hi"
                                    ? "आपकी फसल पानी के लिए सुरक्षित है! कोई स्वैप की आवश्यकता नहीं।"
                                    : "Your crop is water-safe! No swap needed."}
                            </p>
                        </div>
                    )}
                </div>

                {/* Modal Footer */}
                <div className="sticky bottom-0 bg-gradient-to-r from-amber-900 to-amber-800 p-5 border-t border-white/10">
                    <button
                        onClick={onClose}
                        className="w-full bg-gradient-to-r from-gray-700 to-gray-600 hover:from-gray-600 hover:to-gray-500 py-3 rounded-xl font-bold text-white transition-all duration-300 active:scale-[0.98] shadow-lg"
                    >
                        {labels.close}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SwapResultsModal;
