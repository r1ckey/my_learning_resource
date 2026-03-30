import os
import json
import glob

# Parts 1-4 definitions
base_dir1 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Dataengineer_learning"
base_dir2 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Dataengineer_learning2"
base_dir3 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Dataengineer_learning3"
base_dir4 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Dataengineer_learning4"
# Parts 5-7 Deep Dive definitions
base_dir5 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Dataengineer_learning5"
base_dir6 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Dataengineer_learning6"
base_dir7 = r"c:\Users\jorda\Documents\ANTIGRAVITY\STUDY\Dataengineer_learning7"

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

print("Building FULL Data Engineer Study Portal Data...")
# Base parts
load_data(base_dir1, "DataEngineering_Core_Roadmap.md", "P1Roadmap", "Part 1: アーキテクチャ基礎", "P1")
load_data(base_dir2, "Data_Modeling_and_ETL_Roadmap.md", "P2Roadmap", "Part 2: モデリング・ETL", "P2")
load_data(base_dir3, "Advanced_Pipelines_and_Streaming_Roadmap.md", "P3Roadmap", "Part 3: パイプライン・ストリーミング", "P3")
load_data(base_dir4, "Data_Governance_and_Future_Roadmap.md", "P4Roadmap", "Part 4: ガバナンス・未来", "P4")

# Deep Dive parts
load_data(base_dir5, "Advanced_Spark_Optimization_Roadmap.md", "P5Roadmap", "Part 5: [Deep] Sparkアーキテクチャの死闘", "P5")
load_data(base_dir6, "Modern_Data_Pipelines_Roadmap.md", "P6Roadmap", "Part 6: [Deep] dbtとパイプラインの罠", "P6")
load_data(base_dir7, "Realtime_Streaming_Roadmap.md", "P7Roadmap", "Part 7: [Deep] リアルタイムとKafkaの心臓", "P7")

js_content = f"const portalData = {json.dumps(portal_data, ensure_ascii=False)};"

with open(output_js, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"\n✅ Build Complete! Unified database saved to {output_js}")
