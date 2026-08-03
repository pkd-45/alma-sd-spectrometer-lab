from pathlib import Path

from alma_lab.pipeline import run_demo_pipeline

result = run_demo_pipeline(Path("products/example"), workers=1)
print(result.qa)
