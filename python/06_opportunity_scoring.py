
import pandas as pd

density = pd.read_csv("../data/cleaned/population_density_2026.csv")
income = pd.read_csv("../data/cleaned/income_proxy.csv")
competitor = pd.read_csv("../data/cleaned/competitor_index.csv")

# Merge all three on 'Ward Name'
df = density.merge(income, on="Ward Name").merge(competitor, on="Ward Name")

def normalize(series):
    return (series - series.min()) / (series.max() - series.min()) * 100

df["density_norm"] = normalize(df["density_2026_est_per_km2"])
df["income_norm"] = normalize(df["avg_property_rate_rs_sqft"])
df["competitor_norm"] = normalize(df["competitor_intensity_score"])

# WEIGHTS - documented assumption: density and income equally drive demand
df["demand_index"] = (0.5 * df["density_norm"] + 0.5 * df["income_norm"]).round(1)
df["saturation_index"] = df["competitor_norm"].round(1)
df["opportunity_score"] = (df["demand_index"] - df["saturation_index"]).round(1)

df = df.sort_values("opportunity_score", ascending=False)

print(df[["Ward Name", "demand_index", "saturation_index", "opportunity_score"]].to_string(index=False))

print("\n--- TOP 3 RECOMMENDED ENTRY WARDS ---")
for _, r in df.head(3).iterrows():
    print(f"  {r['Ward Name']}: opportunity {r['opportunity_score']}, "
          f"pop {r['population_2026_est']:,}, "
          f"density {r['density_2026_est_per_km2']:,.0f}/km2, "
          f"rate Rs{r['avg_property_rate_rs_sqft']}/sqft, "
          f"competitor {r['competitor_intensity_score']}/25")

print("\n--- BOTTOM 3 (AVOID) ---")
for _, r in df.tail(3).iterrows():
    print(f"  {r['Ward Name']}: opportunity {r['opportunity_score']}")

# Save final combined dataset - this is what feeds Power BI
# Save final combined dataset - this is what feeds Power BI
final_cols = ["Ward Name", "geo_name", "population_2026_est", "area_km2",
              "density_2026_est_per_km2", "avg_property_rate_rs_sqft",
              "competitor_intensity_score", "rationale", "demand_index", "saturation_index",
              "opportunity_score", "centroid_lat", "centroid_lon"]
df[final_cols].to_csv("../outputs/pune_market_entry_final.csv", index=False)
print("\nSaved to outputs/pune_market_entry_final.csv - this feeds Power BI")