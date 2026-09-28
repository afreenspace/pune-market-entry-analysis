
import pandas as pd
import json
import math

# --- Load cleaned census data ---
census = pd.read_csv("../data/cleaned/census_aggregated_by_ward.csv")

# --- Load geojson ---
with open("../data/raw/pune_admin_wards.geojson") as f:
    geo = json.load(f)

# --- Name mapping: census "Ward Name" -> geojson "name" ---
# (verified manually - spellings differ between the two source files)
NAME_MAP = {
    "Aundh": "Admin Ward 01 Aundh",
    "Ghole Road": "Admin Ward 02 Ghole Road",
    "Kothrud": "Admin Ward 03 Kothrud Karveroad",
    "Warje": "Admin Ward 04 Warje Karvenagar",
    "Dholepatil Road": "Admin Ward 05 Dhole Patil Rd",
    "Sangamwadi (Yerawada)": "Admin Ward 06 Yerawda - Sangamwadi",
    "Nagar Road": "Admin Ward 07 Nagar Road",
    "Kasbavish-Rambaug": "Admin Ward 08 KasbaVishrambaugwada",
    "Tilak Road": "Admin Ward 09 Tilak Road",
    "Sahakarnagar": "Admin Ward 10 Sahakarnagar",
    "Bibvewadi": "Admin Ward 11 Bibwewadi",
    "Bhavani Peth": "Admin Ward 12 Bhavani Peth",
    "Hadapsar": "Admin Ward 13 Hadapsar",
    "Dhankawadi": "Admin Ward 14 Dhankawadi",
    "Yewalewadi": "Admin Ward 15 Kondhwa Wanavdi",
}
census["geo_name"] = census["Ward Name"].map(NAME_MAP)

# sanity check - make sure every row got matched
unmatched = census[census["geo_name"].isna()]
if len(unmatched) > 0:
    print("WARNING - unmatched wards:\n", unmatched["Ward Name"].tolist())
else:
    print("All 15 census wards matched to geojson names successfully.")

# --- Compute polygon area in km2 (shoelace formula on locally-projected meters) ---
def polygon_area_km2(coords, ref_lat):
    R = 6371000.0  # Earth radius in meters
    lat_rad = math.radians(ref_lat)
    m_per_deg_lat = (math.pi / 180) * R
    m_per_deg_lon = (math.pi / 180) * R * math.cos(lat_rad)
    pts = [(lon * m_per_deg_lon, lat * m_per_deg_lat) for lon, lat in coords]
    area = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2 / 1_000_000  # m2 -> km2

ward_area = {}
ward_centroid = {}
for feat in geo["features"]:
    name = feat["properties"]["name"]
    ring = feat["geometry"]["coordinates"][0]
    lats = [c[1] for c in ring]
    ref_lat = sum(lats) / len(lats)
    ward_area[name] = polygon_area_km2(ring, ref_lat)
    ward_centroid[name] = (
        sum(c[1] for c in ring) / len(ring),  # lat
        sum(c[0] for c in ring) / len(ring),  # lon
    )

census["area_km2"] = census["geo_name"].map(ward_area)
census["centroid_lat"] = census["geo_name"].map(lambda n: ward_centroid[n][0])
census["centroid_lon"] = census["geo_name"].map(lambda n: ward_centroid[n][1])

# --- Density (2011) and 2026 projection ---
GROWTH_RATE = 0.02  # 2%/yr, documented assumption based on Pune metro trend
YEARS = 2026 - 2011

census["density_2011_per_km2"] = (census["TOT_P"] / census["area_km2"]).round(1)
census["population_2026_est"] = (census["TOT_P"] * (1 + GROWTH_RATE) ** YEARS).round().astype(int)
census["density_2026_est_per_km2"] = (census["population_2026_est"] / census["area_km2"]).round(1)
census["avg_household_size"] = (census["TOT_P"] / census["No of House Holds"]).round(2)

census = census.sort_values("density_2026_est_per_km2", ascending=False)

print("\n--- Top 5 densest wards (2026 est.) ---")
print(census[["Ward Name", "population_2026_est", "area_km2", "density_2026_est_per_km2"]].head())

print("\n--- Bottom 5 (least dense) ---")
print(census[["Ward Name", "population_2026_est", "area_km2", "density_2026_est_per_km2"]].tail())

census.to_csv("../data/cleaned/population_density_2026.csv", index=False)
print("\nSaved to data/cleaned/population_density_2026.csv")