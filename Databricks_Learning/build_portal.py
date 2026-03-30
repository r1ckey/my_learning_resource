import os
import json
import glob

base_dir1 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Databricks_Learning"
base_dir2 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Databricks_Learning2"
base_dir3 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Databricks_Learning3"
base_dir4 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Databricks_Learning4"
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
        print(f"- Found {roadmap_file}")
    
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
            print(f"- Found {len(files)} files in {key}")

print("Building Unified Study Portal Data (Parts 1 to 4)...")

load_data(base_dir1, "Databricks_1Month_Roadmap.md", "Roadmap", "1ヶ月ロードマップ", "")
load_data(base_dir2, "Databricks_Certification_Roadmap.md", "CertRoadmap", "資格対策ロードマップ", "Cert")
load_data(base_dir3, "Databricks_Professional_Roadmap.md", "AdvRoadmap", "Advanced DEロードマップ", "Adv")
load_data(base_dir4, "Databricks_GenAI_Roadmap.md", "GenAIRoadmap", "GenAIロードマップ", "GenAI")

js_content = f"const portalData = {json.dumps(portal_data, ensure_ascii=False)};"

with open(output_js, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"\n✅ Build Complete! Unified database saved to {output_js}")
