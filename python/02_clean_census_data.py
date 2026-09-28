
import pandas as pd

census_df = pd.read_csv("../data/raw/pune_ward_census_2011.csv", encoding="utf-8-sig")

# Drop any row where 'Census Ward Number' contains the word 'Total'
# (some source files embed a running subtotal row per ward - check for it)
before = len(census_df)
census_df = census_df[~census_df["Census Ward Number"].astype(str).str.contains("Total", case=False, na=False)]
after = len(census_df)
print(f"Dropped {before - after} 'Total' rows. Remaining rows: {after}")

# Aggregate to admin-ward level: group by 'Ward Name', sum numeric columns
numeric_cols = ["No of House Holds", "TOT_P", "TOT_M", "TOT_F", "P_06", "M_06", "F_06", "P_SC", "M_SC", "F_SC", "P_ST", "M_ST", "F_ST"]
ward_agg = census_df.groupby("Ward Name")[numeric_cols].sum().reset_index()

print("\nAggregated to", len(ward_agg), "admin wards")
print(ward_agg)

# Save cleaned output
ward_agg.to_csv("../data/cleaned/census_aggregated_by_ward.csv", index=False)
print("\nSaved to data/cleaned/census_aggregated_by_ward.csv")