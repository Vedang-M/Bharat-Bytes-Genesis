/**
 * FertilizerAd Component
 * Displays government-approved fertilizer advertisements.
 * Shows contextually relevant ads based on crop, region, and season.
 */

import { useState, useEffect } from "react";
import { ExternalLink, CheckCircle, ShoppingBag } from "lucide-react";
import { getFertilizerAds } from "../utils/apiUtils";

/**
 * Determine current agricultural season based on month
 * Kharif: June-October, Rabi: November-March, Zaid: April-May
 */
const getCurrentSeason = () => {
  const month = new Date().getMonth() + 1; // 1-12
  if (month >= 6 && month <= 10) return "kharif";
  if (month >= 11 || month <= 3) return "rabi";
  return "zaid";
};

/**
 * Get state name from district or use fallback
 */
const normalizeRegion = (region) => {
  if (!region) return null;
  // Common state mappings from district names
  const stateFromDistrict = {
    "mumbai": "maharashtra",
    "pune": "maharashtra",
    "thane": "maharashtra",
    "nagpur": "maharashtra",
    "delhi": "delhi",
    "bengaluru": "karnataka",
    "bangalore": "karnataka",
    "chennai": "tamil nadu",
    "hyderabad": "telangana",
    "kolkata": "west bengal",
    "ahmedabad": "gujarat",
    "jaipur": "rajasthan",
    "lucknow": "uttar pradesh",
    "bhopal": "madhya pradesh",
    "patna": "bihar",
    "chandigarh": "punjab",
  };
  
  const lowerRegion = region.toLowerCase();
  return stateFromDistrict[lowerRegion] || lowerRegion;
};

const FertilizerAd = ({ crop, region, language = "hi" }) => {
  const [ad, setAd] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showRetailers, setShowRetailers] = useState(false);

  useEffect(() => {
    const fetchAd = async () => {
      if (!crop) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const season = getCurrentSeason();
        const normalizedRegion = normalizeRegion(region);
        
        const response = await getFertilizerAds(crop, normalizedRegion, season);
        
        // Show first ad from the response
        if (response?.ads?.length > 0) {
          setAd(response.ads[0]);
        }
      } catch (error) {
        console.error("Error fetching fertilizer ads:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAd();
  }, [crop, region]);

  // Don't render anything while loading or if no ad
  if (loading || !ad) return null;

  const translations = {
    hi: {
      adLabel: "विज्ञापन",
      govtApproved: "सरकार द्वारा अनुमोदित",
      viewRetailers: "खरीदें",
      price: "मूल्य",
      hideRetailers: "बंद करें",
    },
    en: {
      adLabel: "Ad",
      govtApproved: "Govt. Approved",
      viewRetailers: "Buy Now",
      price: "Price",
      hideRetailers: "Close",
    },
  };

  const t = translations[language] || translations.hi;

  return (
    <div className="bg-gradient-to-b from-white/15 to-white/5 backdrop-blur-xl border border-white/10 shadow-lg rounded-3xl p-5 mt-6">
      {/* Ad Label */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-bold bg-white/20 text-white/70 px-3 py-1 rounded-full uppercase tracking-wide">
          {t.adLabel}
        </span>
        <div className="flex items-center gap-1.5 text-green-400">
          <CheckCircle size={14} />
          <span className="text-xs font-bold">{t.govtApproved}</span>
        </div>
      </div>

      {/* Ad Content */}
      <div className="flex gap-4">
        {/* Product Image */}
        <div className="relative flex-shrink-0">
          <div className="w-24 h-24 md:w-28 md:h-28 rounded-2xl overflow-hidden bg-white/10 border border-white/10">
            <img
              src={ad.image_url}
              alt={ad.product_name}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.src = "/fertilizer-placeholder.webp";
                e.target.onerror = null;
              }}
            />
          </div>
        </div>

        {/* Product Info */}
        <div className="flex-1 min-w-0">
          <h4 className="text-white font-black text-lg leading-tight truncate">
            {ad.brand_name}
          </h4>
          <p className="text-white/80 font-bold text-sm truncate">
            {ad.product_name}
          </p>
          
          {/* Approval Number */}
          <p className="text-green-400/80 text-xs font-medium mt-1 truncate">
            {ad.approval_number}
          </p>
          
          {/* Price */}
          <div className="mt-2 flex items-baseline gap-1">
            <span className="text-white font-black text-xl">
              ₹{ad.price_per_unit.toLocaleString("en-IN")}
            </span>
            <span className="text-white/60 text-xs font-medium">
              / {ad.unit}
            </span>
          </div>
        </div>
      </div>

      {/* View Retailers Button */}
      <button
        onClick={() => setShowRetailers(!showRetailers)}
        className="w-full mt-4 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white font-bold py-3 px-4 rounded-2xl flex items-center justify-center gap-2 transition-all duration-200 shadow-lg hover:shadow-xl"
      >
        <ShoppingBag size={18} />
        <span>{showRetailers ? t.hideRetailers : t.viewRetailers}</span>
      </button>

      {/* Retailer Links - Expandable */}
      {showRetailers && ad.retailer_links?.length > 0 && (
        <div className="mt-4 space-y-2 animate-in slide-in-from-top-2 duration-200">
          {ad.retailer_links.map((link, index) => {
            // Extract domain name for display
            let displayName;
            try {
              const url = new URL(link);
              displayName = url.hostname.replace("www.", "");
            } catch {
              displayName = `Retailer ${index + 1}`;
            }

            return (
              <a
                key={index}
                href={link}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-between bg-white/10 hover:bg-white/20 border border-white/10 rounded-xl px-4 py-3 transition-colors group"
              >
                <span className="text-white font-medium text-sm truncate">
                  {displayName}
                </span>
                <ExternalLink
                  size={16}
                  className="text-white/60 group-hover:text-white transition-colors flex-shrink-0 ml-2"
                />
              </a>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default FertilizerAd;
