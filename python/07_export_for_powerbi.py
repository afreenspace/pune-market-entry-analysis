
import json
import pandas as pd

# Reload final scored data to get the name mapping
df = pd.read_csv("../outputs/pune_market_entry_final.csv")

# geo_name -> Ward Name lookup (reverse of what we used in Step 3)
geo_to_ward = dict(zip(df["geo_name"], df["Ward Name"]))

with open("../data/raw/pune_admin_wards.geojson") as f:
    geo = json.load(f)

matched, unmatched = 0, []
for feat in geo["features"]:
    old_name = feat["properties"]["name"]
    if old_name in geo_to_ward:
        # Add a new property Power BI will join on - keep the old one too for reference
        feat["properties"]["Ward Name"] = geo_to_ward[old_name]
        matched += 1
    else:
        unmatched.append(old_name)

print(f"Matched {matched}/{len(geo['features'])} ward polygons.")
if unmatched:
    print("WARNING - unmatched polygons (won't map correctly):", unmatched)

with open("../outputs/pune_wards_powerbi.geojson", "w") as f:
    json.dump(geo, f)

print("Saved outputs/pune_wards_powerbi.geojson")
print("\nFiles ready for Power BI in outputs/:")
print("  1. pune_market_entry_final.csv   (data table)")
print("  2. pune_wards_powerbi.geojson    (map boundaries, joinable on 'Ward Name')")