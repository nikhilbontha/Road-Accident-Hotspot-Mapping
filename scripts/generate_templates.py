import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.services.import_service import generate_template_csv

def main():
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(templates_dir, exist_ok=True)
    template_path = os.path.join(templates_dir, "accident_data_template_v2.csv")
    csv_content = generate_template_csv()
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(csv_content)
    print(f"Generated official template at: {template_path}")

if __name__ == "__main__":
    main()
