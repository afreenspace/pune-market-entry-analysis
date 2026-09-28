
import pandas as pd

income_data = [
    ("Aundh", 13950, "sourced"),
    ("Ghole Road", 10500, "estimated"),
    ("Kothrud", 14400, "sourced"),
    ("Warje", 9600, "sourced"),
    ("Dholepatil Road", 13500, "estimated"),
    ("Sangamwadi (Yerawada)", 10900, "sourced"),
    ("Nagar Road", 10000, "estimated"),
    ("Kasbavish-Rambaug", 8500, "estimated"),
    ("Tilak Road", 9500, "estimated"),
    ("Sahakarnagar", 9000, "estimated"),
    ("Bibvewadi", 10850, "sourced"),
    ("Bhavani Peth", 8800, "sourced"),
    ("Hadapsar", 11500, "sourced"),
    ("Dhankawadi", 7200, "estimated"),
    ("Yewalewadi", 6500, "estimated"),
]

income_df = pd.DataFrame(income_data, columns=["Ward Name", "avg_property_rate_rs_sqft", "data_source"])

print(income_df.sort_values("avg_property_rate_rs_sqft", ascending=False))

income_df.to_csv("../data/cleaned/income_proxy.csv", index=False)
print("\nSaved to data/cleaned/income_proxy.csv")
print(f"\n{(income_df['data_source']=='sourced').sum()} wards sourced directly, "
      f"{(income_df['data_source']=='estimated').sum()} estimated from comparable areas.")