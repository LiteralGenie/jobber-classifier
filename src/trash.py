import json

from config import paths

skills = [
    "python",
    "c++",
    "git",
    "vba",
    "node.js",
    "react",
    "angular",
    "java",
    "vuejs",
    "c",
    "ruby",
    "rust",
    "golang",
    "sql",
    "perl",
    "bash",
    "javascript",
    "typescript",
    "php",
    "html",
    "css",
]

with open(paths.DATA_DIR / "test" / "1.txt") as file:
    description = file.read()


# llm = models.LlamaCpp(
#     model="/home/anne/Downloads/mistral-7b-instruct-v0.2.Q8_0.gguf",
#     n_gpu_layers=1000,
#     n_ctx=4096,
# )
# result = extract(
#     llm,
#     description,
#     skills,
#     ["Does the position involve a support / on-call rotation?"],
# )


# result = requests.post(
#     "http://localhost:9593/parse",
#     json=[
#         dict(
#             description=description,
#             skills=skills,
#             duties=["Does the position involve a support / on-call rotation?"],
#         ),
#     ],
# ).json()

# print(json.dumps(result, indent=2))

print(
    json.dumps(
        dict(
            description=description,
            skills=skills,
            duties=["Does the position involve a support / on-call rotation?"],
        )
    )
)
