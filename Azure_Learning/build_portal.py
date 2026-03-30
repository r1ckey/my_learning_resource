import os
import json
import glob

base_dir1 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Azure_Learning"
base_dir2 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Azure_Learning2"
base_dir3 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Azure_Learning3"
output_js = os.path.join(base_dir1, "portal_data.js")

weeks = ["Week1", "Week2", "Week3", "Week4"]
portal_data = {}

def load_data(base_dir, roadmap_file, roadmap_key, roadmap_title, week_prefix):
    print(f"\n[Scanning {base_dir}]")
    if os.path.exists(os.path.join(base_dir, roadmap_file)):
        with open(os.path.join(base_dir, roadmap_file), 'r', encoding='utf-8') as f:
            portal_data[roadmap_key] = [{
                "id": f"{roadmap_key}_id",
                "title": roadmap_title,
                "content": f.read()
            }]
    
    for week in weeks:
        key = f"{week_prefix}{week}"
        week_dir = os.path.join(base_dir, week)
        portal_data[key] = []
        if os.path.exists(week_dir):
            files = glob.glob(os.path.join(week_dir, "*.md"))
            files.sort()
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    filename = os.path.basename(file_path)
                    portal_data[key].append({
                        "id": f"{key}_{filename}",
                        "title": filename.replace(".md", ""),
                        "content": f.read()
                    })

print("Building Azure Study Portal Data...")
# Load AZ-104 (Part 1 & 2 logically mapped to Weeks 1-4)
load_data(base_dir1, "Azure_AZ104_Roadmap.md", "P1Roadmap", "AZ-104 ロードマップ", "P1")
# Load DP-203 (Part 3 & 4 logically mapped to Weeks 1-4)
load_data(base_dir2, "Azure_DP203_Roadmap.md", "P2Roadmap", "DP-203 ロードマップ", "P2")
# Load Azure Databricks Architecture (Part 5 mapped to Weeks 1-4)
load_data(base_dir3, "Azure_Databricks_Architecture_Roadmap.md", "P3Roadmap", "Architecture ロードマップ", "P3")

js_content = f"const portalData = {json.dumps(portal_data, ensure_ascii=False)};"

with open(output_js, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"\n✅ Build Complete! Unified database saved to {output_js}")
