import sys
from pathlib import Path

# Add src/ to PATH
sys.path.append(str(Path(__file__).parent.parent))

import json

import tomli
from guidance import models

from config import paths
from extract import extract

with open(paths.CONFIG_DIR / "config.toml", "rb") as file:
    config = tomli.load(file)

example_usage = """
Example usage: 
    python3 run_extract.py "$JSON_DATA"

    where $JSON_DATA is a json string with the following structure:
    {{
        "description": "...",
        "skills": [
            "python",
            "..."
        ],
        "duties": [
            "Does the job involve ___?",
            "..."
        ]
    }}
""".strip()

# Validate number of args
if len(sys.argv) == 1:
    print(
        f"""
Expected at least 1 argument.

{example_usage}
""".strip()
    )
    sys.exit()

# Validate json data
requests = []
for idx, text in enumerate(sys.argv[1:]):
    try:
        requests.append(json.loads(text))
    except:
        print(
            f"""
Error: Invalid JSON data at index {idx}

{text}

{example_usage}
""".strip(),
            file=sys.stderr,
        )
        sys.exit()

# Run llm
llm = models.LlamaCpp(
    model=config["model_file"],
    n_gpu_layers=9999 if config["use_gpu"] else -1,
    n_ctx=4096,
)

result = []
for req in requests:
    data = extract(
        llm,
        description=req["description"],
        skills=req["skills"],
        duties=req["duties"],
    )
    result.append(data)
print(result)
