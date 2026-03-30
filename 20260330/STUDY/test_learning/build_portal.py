import os
import json
import glob

base_dir1 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\test_learning"
base_dir2 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\test_learning2"
base_dir3 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\test_learning3"
base_dir4 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\test_learning4"
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
    else:
        print(f"Roadmap not found: {roadmap_file}")
    
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
        else:
            print(f"Directory not found: {week_dir}")

print("Building Software QA & Testing Study Portal Data...")
load_data(base_dir1, "Testing_Foundations_Roadmap.md", "P1Roadmap", "Part 1: テスト基礎理論", "P1")
load_data(base_dir2, "Test_Design_Techniques_Roadmap.md", "P2Roadmap", "Part 2: テスト設計技法", "P2")
load_data(base_dir3, "Excel_Test_Documentation_Roadmap.md", "P3Roadmap", "Part 3: Excel仕様書の実務", "P3")
load_data(base_dir4, "Unit_Test_and_Automation_Roadmap.md", "P4Roadmap", "Part 4: 単体テストとモック", "P4")

js_content = f"const portalData = {json.dumps(portal_data, ensure_ascii=False)};"

with open(output_js, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"\n✅ Build Complete! Unified QA database saved to {output_js}")
