import json
import random
import os

path = r"d:\Projects\PharmaSynapse\backend\app\data\mock_iqvia.json"

if not os.path.exists(path):
    print(f"File not found: {path}")
    exit(1)

with open(path, "r") as f:
    data = json.load(f)

metformin = data.get("metformin")
if not metformin:
    print("Metformin entry not found")
    exit(1)

regions = metformin.get("regions", {})

# List of dummy regions to ensure we have ~30 data points
countries = [
    "Japan", "China", "Germany", "France", "UK", "Italy", "Spain", "Canada", "Brazil", "Australia",
    "India", "South Korea", "Russia", "Mexico", "Turkey", "Saudi Arabia", "Switzerland", "Argentina",
    "Sweden", "Poland", "Belgium", "Thailand", "Austria", "Iran", "Norway", "UAE", "Egypt", "South Africa",
    "Malaysia", "Netherlands", "Vietnam", "Singapore", "Indonesia", "Pakistan", "Bangladesh", "Nigeria",
    "Philippines", "Colombia", "Chile", "Romania", "Czech Republic", "Portugal", "Greece", "Hungary"
]

for country in countries:
    # Ensure they are unique keys (some might overlap with existing, e.g. EU5 logic, but for mock chart it's fine)
    if country not in regions:
        regions[country] = {
            "market_size_usd_mn": round(random.uniform(50, 600), 1),
            "cagr_5y_percent": round(random.uniform(1.0, 9.0), 1),
            "volume_trend": random.choice(["stable", "growing", "declining"]),
            "competitors": [
                {"company": f"Local {country} Pharma", "share_percent": round(random.uniform(15, 35))},
                {"company": f"Global Generics {country}", "share_percent": round(random.uniform(5, 20))}
            ]
        }

data["metformin"]["regions"] = regions

with open(path, "w") as f:
    json.dump(data, f, indent=2)

print(f"Updated mock data. Total regions: {len(regions)}")
