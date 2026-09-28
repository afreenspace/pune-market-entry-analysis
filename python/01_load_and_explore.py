
import pandas as pd
import json

# Load census CSV
census_df = pd.read_csv("../data/raw/pune_ward_census_2011.csv", encoding="utf-8-sig")
print("Shape:", census_df.shape)
print(census_df.head())
print(census_df.columns.tolist())

# Load geojson
with open("../data/raw/pune_admin_wards.geojson") as f:
    geo = json.load(f)

print("Number of ward polygons:", len(geo["features"]))
print("Sample ward name:", geo["features"][0]["properties"])

