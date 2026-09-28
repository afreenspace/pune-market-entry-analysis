
import pandas as pd

df = pd.read_csv("../outputs/pune_market_entry_final.csv")

# Recompute normalized components (same as Step 6) so we can re-weight them
def normalize(series):
    return (series - series.min()) / (series.max() - series.min()) * 100

df["density_norm"] = normalize(df["density_2026_est_per_km2"])
df["income_norm"] = normalize(df["avg_property_rate_rs_sqft"])
df["competitor_norm"] = normalize(df["competitor_intensity_score"])

# --- Define weighting scenarios to test ---
scenarios = {
    "Base case (50/50)": (0.5, 0.5),
    "Density-heavy (70/30)": (0.7, 0.3),
    "Income-heavy (30/70)": (0.3, 0.7),
    "Density-only (100/0)": (1.0, 0.0),
    "Income-only (0/100)": (0.0, 1.0),
}

results = {}
for label, (w_density, w_income) in scenarios.items():
    demand = w_density * df["density_norm"] + w_income * df["income_norm"]
    opportunity = (demand - df["competitor_norm"]).round(1)
    ranked = df.assign(opportunity=opportunity).sort_values("opportunity", ascending=False)
    results[label] = ranked[["Ward Name", "opportunity"]].reset_index(drop=True)
    top3 = ranked["Ward Name"].head(3).tolist()
    print(f"\n{label}: weights density={w_density}, income={w_income}")
    print(f"  Top 3: {top3}")

# --- Build a comparison table: rank of each ward across all scenarios ---
comparison = pd.DataFrame({"Ward Name": df["Ward Name"]})
for label, ranked_df in results.items():
    rank_map = {name: i + 1 for i, name in enumerate(ranked_df["Ward Name"])}
    comparison[label] = comparison["Ward Name"].map(rank_map)

comparison["avg_rank"] = comparison.drop(columns="Ward Name").mean(axis=1).round(1)
comparison["rank_range"] = (
    comparison.drop(columns=["Ward Name", "avg_rank"]).max(axis=1)
    - comparison.drop(columns=["Ward Name", "avg_rank"]).min(axis=1)
)
comparison = comparison.sort_values("avg_rank")

print("\n=== RANK STABILITY ACROSS ALL 5 SCENARIOS ===")
print("(rank 1 = best opportunity in that scenario; rank_range = how much a ward's rank swings)")
print(comparison.to_string(index=False))

comparison.to_csv("../outputs/sensitivity_analysis.csv", index=False)
print("\nSaved to outputs/sensitivity_analysis.csv")