/**
 * Nutrient brand reference data with products and recommended feed charts.
 * Values are approximate ml/gallon based on published manufacturer charts.
 * Users should always verify against their specific product labels.
 */

export interface NutrientProduct {
  id: string;
  name: string;
  type: "base" | "supplement";
}

export interface FeedChartPhase {
  phase: string;
  stage: string; // maps to grow stage enum
  weekRange: string;
  products: { productId: string; ml_per_gallon: number }[];
  notes?: string;
}

export interface NutrientBrand {
  id: string;
  name: string;
  line: string;
  description: string;
  products: NutrientProduct[];
  feedChart: FeedChartPhase[];
}

/**
 * Standalone additives that work alongside any nutrient brand.
 * These are not full feed lines — they're dosed independently.
 */
export interface StandaloneAdditive {
  id: string;
  name: string;
  brand: string;
  description: string;
  ml_per_gallon: number;
  when: string;
  growTypes: string[];
}

export const STANDALONE_ADDITIVES: StandaloneAdditive[] = [
  {
    id: "botanicare-hydroguard",
    name: "Hydroguard",
    brand: "Botanicare",
    description:
      "Beneficial bacteria (Bacillus amyloliquefaciens) that colonizes roots and outcompetes harmful pathogens like pythium. Essential for DWC when water temps exceed 68°F.",
    ml_per_gallon: 2,
    when: "Every reservoir change and top-off. Safe from seedling through harvest (not a nutrient — does not need to be flushed).",
    growTypes: ["dwc", "rdwc", "nft", "ebb_flow", "aeroponics", "kratky"],
  },
];

export const NUTRIENT_BRANDS: NutrientBrand[] = [
  {
    id: "gh-flora",
    name: "General Hydroponics",
    line: "Flora Series",
    description: "The original 3-part nutrient system. Industry standard for hydro and soilless grows.",
    products: [
      { id: "gh-micro", name: "FloraMicro", type: "base" },
      { id: "gh-gro", name: "FloraGro", type: "base" },
      { id: "gh-bloom", name: "FloraBloom", type: "base" },
      { id: "gh-calimagic", name: "CaliMagic", type: "supplement" },
      { id: "gh-koolbloom", name: "Liquid KoolBloom", type: "supplement" },
      { id: "gh-florakleen", name: "FloraKleen", type: "supplement" },
    ],
    feedChart: [
      {
        phase: "Seedling",
        stage: "seedling",
        weekRange: "1–2",
        products: [
          { productId: "gh-micro", ml_per_gallon: 1.25 },
          { productId: "gh-gro", ml_per_gallon: 1.25 },
          { productId: "gh-bloom", ml_per_gallon: 1.25 },
        ],
        notes: "¼ strength. pH 5.5–6.0.",
      },
      {
        phase: "Early Veg",
        stage: "vegetative",
        weekRange: "3–4",
        products: [
          { productId: "gh-micro", ml_per_gallon: 2.5 },
          { productId: "gh-gro", ml_per_gallon: 2.5 },
          { productId: "gh-bloom", ml_per_gallon: 1.25 },
          { productId: "gh-calimagic", ml_per_gallon: 2.5 },
        ],
        notes: "½ strength. Ramp up if plants look hungry.",
      },
      {
        phase: "Mid Veg",
        stage: "vegetative",
        weekRange: "5–6",
        products: [
          { productId: "gh-micro", ml_per_gallon: 3.75 },
          { productId: "gh-gro", ml_per_gallon: 3.75 },
          { productId: "gh-bloom", ml_per_gallon: 1.25 },
          { productId: "gh-calimagic", ml_per_gallon: 2.5 },
        ],
        notes: "¾ strength.",
      },
      {
        phase: "Late Veg",
        stage: "vegetative",
        weekRange: "7",
        products: [
          { productId: "gh-micro", ml_per_gallon: 5 },
          { productId: "gh-gro", ml_per_gallon: 5 },
          { productId: "gh-bloom", ml_per_gallon: 1.25 },
          { productId: "gh-calimagic", ml_per_gallon: 5 },
        ],
        notes: "Full strength veg.",
      },
      {
        phase: "Transition",
        stage: "flowering",
        weekRange: "8",
        products: [
          { productId: "gh-micro", ml_per_gallon: 5 },
          { productId: "gh-gro", ml_per_gallon: 2.5 },
          { productId: "gh-bloom", ml_per_gallon: 2.5 },
          { productId: "gh-calimagic", ml_per_gallon: 5 },
        ],
        notes: "Flip to 12/12. Begin reducing Gro.",
      },
      {
        phase: "Early Flower",
        stage: "flowering",
        weekRange: "9–10",
        products: [
          { productId: "gh-micro", ml_per_gallon: 5 },
          { productId: "gh-gro", ml_per_gallon: 1.25 },
          { productId: "gh-bloom", ml_per_gallon: 5 },
          { productId: "gh-calimagic", ml_per_gallon: 5 },
          { productId: "gh-koolbloom", ml_per_gallon: 1.25 },
        ],
      },
      {
        phase: "Mid Flower",
        stage: "flowering",
        weekRange: "11–12",
        products: [
          { productId: "gh-micro", ml_per_gallon: 5 },
          { productId: "gh-gro", ml_per_gallon: 0 },
          { productId: "gh-bloom", ml_per_gallon: 6.25 },
          { productId: "gh-calimagic", ml_per_gallon: 5 },
          { productId: "gh-koolbloom", ml_per_gallon: 2.5 },
        ],
        notes: "Drop FloraGro entirely.",
      },
      {
        phase: "Late Flower / Ripen",
        stage: "ripening",
        weekRange: "13–14",
        products: [
          { productId: "gh-micro", ml_per_gallon: 2.5 },
          { productId: "gh-bloom", ml_per_gallon: 5 },
          { productId: "gh-koolbloom", ml_per_gallon: 1.25 },
        ],
        notes: "Reduce feeding. Watch trichomes.",
      },
      {
        phase: "Flush",
        stage: "ripening",
        weekRange: "15",
        products: [
          { productId: "gh-florakleen", ml_per_gallon: 5 },
        ],
        notes: "Plain water + FloraKleen for 7–10 days before harvest.",
      },
    ],
  },
  {
    id: "foxfarm-trio",
    name: "Fox Farm",
    line: "Liquid Nutrient Trio",
    description: "Popular 3-bottle system. Great for soil and hydro. Aggressive bloom boosters.",
    products: [
      { id: "ff-growbig", name: "Grow Big", type: "base" },
      { id: "ff-bigbloom", name: "Big Bloom", type: "base" },
      { id: "ff-tigerbloom", name: "Tiger Bloom", type: "base" },
      { id: "ff-sledgehammer", name: "Sledgehammer", type: "supplement" },
      { id: "ff-bushwacker", name: "Bush Doctor Cal-Mag (Bush Wacker)", type: "supplement" },
      { id: "ff-opensesame", name: "Open Sesame", type: "supplement" },
      { id: "ff-beastie", name: "Beastie Bloomz", type: "supplement" },
      { id: "ff-chaching", name: "Cha Ching", type: "supplement" },
    ],
    feedChart: [
      {
        phase: "Seedling",
        stage: "seedling",
        weekRange: "1–2",
        products: [
          { productId: "ff-bigbloom", ml_per_gallon: 7.5 },
        ],
        notes: "Big Bloom only — gentle and organic-based. pH 6.3–6.8 for soil.",
      },
      {
        phase: "Early Veg",
        stage: "vegetative",
        weekRange: "3–4",
        products: [
          { productId: "ff-growbig", ml_per_gallon: 5 },
          { productId: "ff-bigbloom", ml_per_gallon: 15 },
          { productId: "ff-bushwacker", ml_per_gallon: 5 },
        ],
        notes: "Introduce Grow Big at half strength. Cal-Mag throughout veg & flower.",
      },
      {
        phase: "Mid Veg",
        stage: "vegetative",
        weekRange: "5–6",
        products: [
          { productId: "ff-growbig", ml_per_gallon: 10 },
          { productId: "ff-bigbloom", ml_per_gallon: 15 },
          { productId: "ff-bushwacker", ml_per_gallon: 5 },
        ],
      },
      {
        phase: "Late Veg",
        stage: "vegetative",
        weekRange: "7",
        products: [
          { productId: "ff-growbig", ml_per_gallon: 15 },
          { productId: "ff-bigbloom", ml_per_gallon: 15 },
          { productId: "ff-bushwacker", ml_per_gallon: 5 },
        ],
        notes: "Full strength Grow Big.",
      },
      {
        phase: "Transition",
        stage: "flowering",
        weekRange: "8",
        products: [
          { productId: "ff-growbig", ml_per_gallon: 5 },
          { productId: "ff-bigbloom", ml_per_gallon: 15 },
          { productId: "ff-tigerbloom", ml_per_gallon: 5 },
          { productId: "ff-bushwacker", ml_per_gallon: 5 },
          { productId: "ff-opensesame", ml_per_gallon: 2.5 },
        ],
        notes: "Begin Tiger Bloom. Open Sesame triggers flowering.",
      },
      {
        phase: "Early Flower",
        stage: "flowering",
        weekRange: "9–10",
        products: [
          { productId: "ff-bigbloom", ml_per_gallon: 30 },
          { productId: "ff-tigerbloom", ml_per_gallon: 10 },
          { productId: "ff-bushwacker", ml_per_gallon: 5 },
          { productId: "ff-beastie", ml_per_gallon: 2.5 },
        ],
        notes: "Drop Grow Big. Beastie Bloomz for bud density.",
      },
      {
        phase: "Peak Flower",
        stage: "flowering",
        weekRange: "11–12",
        products: [
          { productId: "ff-bigbloom", ml_per_gallon: 45 },
          { productId: "ff-tigerbloom", ml_per_gallon: 15 },
          { productId: "ff-bushwacker", ml_per_gallon: 5 },
          { productId: "ff-beastie", ml_per_gallon: 2.5 },
        ],
        notes: "Max bloom feeding.",
      },
      {
        phase: "Late Flower / Ripen",
        stage: "ripening",
        weekRange: "13–14",
        products: [
          { productId: "ff-bigbloom", ml_per_gallon: 30 },
          { productId: "ff-tigerbloom", ml_per_gallon: 10 },
          { productId: "ff-chaching", ml_per_gallon: 2.5 },
        ],
        notes: "Cha Ching for final push on resin production.",
      },
      {
        phase: "Flush",
        stage: "ripening",
        weekRange: "15",
        products: [
          { productId: "ff-sledgehammer", ml_per_gallon: 10 },
        ],
        notes: "Sledgehammer flush, then plain water 7–10 days.",
      },
    ],
  },
  {
    id: "an-ph-perfect",
    name: "Advanced Nutrients",
    line: "pH Perfect Sensi",
    description: "Auto-adjusting pH technology. 2-part base with powerful bloom supplements.",
    products: [
      { id: "an-sensi-grow-a", name: "Sensi Grow A", type: "base" },
      { id: "an-sensi-grow-b", name: "Sensi Grow B", type: "base" },
      { id: "an-sensi-bloom-a", name: "Sensi Bloom A", type: "base" },
      { id: "an-sensi-bloom-b", name: "Sensi Bloom B", type: "base" },
      { id: "an-b52", name: "B-52", type: "supplement" },
      { id: "an-bigbud", name: "Big Bud", type: "supplement" },
      { id: "an-overdrive", name: "Overdrive", type: "supplement" },
      { id: "an-flawless", name: "Flawless Finish", type: "supplement" },
    ],
    feedChart: [
      {
        phase: "Seedling",
        stage: "seedling",
        weekRange: "1–2",
        products: [
          { productId: "an-sensi-grow-a", ml_per_gallon: 3.8 },
          { productId: "an-sensi-grow-b", ml_per_gallon: 3.8 },
          { productId: "an-b52", ml_per_gallon: 3.8 },
        ],
        notes: "¼ strength. pH Perfect auto-adjusts — no manual pH needed.",
      },
      {
        phase: "Early Veg",
        stage: "vegetative",
        weekRange: "3–4",
        products: [
          { productId: "an-sensi-grow-a", ml_per_gallon: 7.5 },
          { productId: "an-sensi-grow-b", ml_per_gallon: 7.5 },
          { productId: "an-b52", ml_per_gallon: 3.8 },
        ],
        notes: "½ strength.",
      },
      {
        phase: "Late Veg",
        stage: "vegetative",
        weekRange: "5–7",
        products: [
          { productId: "an-sensi-grow-a", ml_per_gallon: 15 },
          { productId: "an-sensi-grow-b", ml_per_gallon: 15 },
          { productId: "an-b52", ml_per_gallon: 7.5 },
        ],
        notes: "Full veg strength.",
      },
      {
        phase: "Transition",
        stage: "flowering",
        weekRange: "8",
        products: [
          { productId: "an-sensi-bloom-a", ml_per_gallon: 7.5 },
          { productId: "an-sensi-bloom-b", ml_per_gallon: 7.5 },
          { productId: "an-b52", ml_per_gallon: 7.5 },
        ],
        notes: "Switch from Grow to Bloom base at ½ strength.",
      },
      {
        phase: "Early Flower",
        stage: "flowering",
        weekRange: "9–10",
        products: [
          { productId: "an-sensi-bloom-a", ml_per_gallon: 15 },
          { productId: "an-sensi-bloom-b", ml_per_gallon: 15 },
          { productId: "an-b52", ml_per_gallon: 7.5 },
          { productId: "an-bigbud", ml_per_gallon: 7.5 },
        ],
        notes: "Big Bud for flower size and weight.",
      },
      {
        phase: "Peak Flower",
        stage: "flowering",
        weekRange: "11–12",
        products: [
          { productId: "an-sensi-bloom-a", ml_per_gallon: 15 },
          { productId: "an-sensi-bloom-b", ml_per_gallon: 15 },
          { productId: "an-bigbud", ml_per_gallon: 7.5 },
        ],
      },
      {
        phase: "Late Flower / Ripen",
        stage: "ripening",
        weekRange: "13–14",
        products: [
          { productId: "an-sensi-bloom-a", ml_per_gallon: 15 },
          { productId: "an-sensi-bloom-b", ml_per_gallon: 15 },
          { productId: "an-overdrive", ml_per_gallon: 7.5 },
        ],
        notes: "Overdrive for final-stage boost.",
      },
      {
        phase: "Flush",
        stage: "ripening",
        weekRange: "15",
        products: [
          { productId: "an-flawless", ml_per_gallon: 7.5 },
        ],
        notes: "Flawless Finish for 7 days, then plain water.",
      },
    ],
  },
  {
    id: "athena-blended",
    name: "Athena",
    line: "Blended Line",
    description: "Commercial-grade 2-part system designed for consistency and scale. Simple mixing.",
    products: [
      { id: "ath-grow-a", name: "Grow A", type: "base" },
      { id: "ath-grow-b", name: "Grow B", type: "base" },
      { id: "ath-bloom-a", name: "Bloom A", type: "base" },
      { id: "ath-bloom-b", name: "Bloom B", type: "base" },
      { id: "ath-cleanse", name: "Cleanse", type: "supplement" },
      { id: "ath-fade", name: "Fade", type: "supplement" },
    ],
    feedChart: [
      {
        phase: "Seedling / Clone",
        stage: "seedling",
        weekRange: "1–2",
        products: [
          { productId: "ath-grow-a", ml_per_gallon: 3 },
          { productId: "ath-grow-b", ml_per_gallon: 3 },
          { productId: "ath-cleanse", ml_per_gallon: 1.5 },
        ],
        notes: "Low EC ~0.5. Keep humidity high for clones.",
      },
      {
        phase: "Early Veg",
        stage: "vegetative",
        weekRange: "3–4",
        products: [
          { productId: "ath-grow-a", ml_per_gallon: 5 },
          { productId: "ath-grow-b", ml_per_gallon: 5 },
          { productId: "ath-cleanse", ml_per_gallon: 1.5 },
        ],
      },
      {
        phase: "Late Veg",
        stage: "vegetative",
        weekRange: "5–7",
        products: [
          { productId: "ath-grow-a", ml_per_gallon: 7.5 },
          { productId: "ath-grow-b", ml_per_gallon: 7.5 },
          { productId: "ath-cleanse", ml_per_gallon: 3 },
        ],
        notes: "Target EC ~1.6–2.0.",
      },
      {
        phase: "Transition",
        stage: "flowering",
        weekRange: "8",
        products: [
          { productId: "ath-bloom-a", ml_per_gallon: 5 },
          { productId: "ath-bloom-b", ml_per_gallon: 5 },
          { productId: "ath-cleanse", ml_per_gallon: 1.5 },
        ],
        notes: "Switch to Bloom base.",
      },
      {
        phase: "Early Flower",
        stage: "flowering",
        weekRange: "9–10",
        products: [
          { productId: "ath-bloom-a", ml_per_gallon: 7.5 },
          { productId: "ath-bloom-b", ml_per_gallon: 7.5 },
          { productId: "ath-cleanse", ml_per_gallon: 3 },
        ],
        notes: "Target EC ~2.2–2.6.",
      },
      {
        phase: "Peak Flower",
        stage: "flowering",
        weekRange: "11–12",
        products: [
          { productId: "ath-bloom-a", ml_per_gallon: 9 },
          { productId: "ath-bloom-b", ml_per_gallon: 9 },
          { productId: "ath-cleanse", ml_per_gallon: 3 },
        ],
        notes: "Target EC ~2.6–3.0. Max feeding.",
      },
      {
        phase: "Late Flower / Ripen",
        stage: "ripening",
        weekRange: "13–14",
        products: [
          { productId: "ath-bloom-a", ml_per_gallon: 6 },
          { productId: "ath-bloom-b", ml_per_gallon: 6 },
          { productId: "ath-fade", ml_per_gallon: 5 },
        ],
        notes: "Fade draws out remaining nutrients in tissue.",
      },
      {
        phase: "Flush",
        stage: "ripening",
        weekRange: "15",
        products: [
          { productId: "ath-cleanse", ml_per_gallon: 5 },
        ],
        notes: "Cleanse only for 7–10 days, then plain water.",
      },
    ],
  },
];
