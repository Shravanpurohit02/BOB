from builder.codegen.parser import cleaner, extractor

NAME = "Autonomous Code Generation"
CATEGORY = "Autonomous"
DESCRIPTION = "Validates code extraction and cleaning pipeline."


def run() -> bool:

    try:
        markdown = """```python
def hello():
    return "world"
```"""

        code = cleaner.clean(extractor.code(markdown))

        artifact = """{
  "schema":"vidhi-builder/v1",
  "directories":[
    {
      "path":"demo"
    }
  ],
  "files":[
    {
      "path":"demo/main.py",
      "content":"print(1)"
    }
  ]
}"""

        artifacts = extractor.artifacts(
            artifact,
        )

        return (
            code.startswith("def hello")
            and len(artifacts) == 1
            and len(artifacts[0].directories) == 1
            and len(artifacts[0].files) == 1
            and artifacts[0].files[0].path == "demo/main.py"
        )

    except Exception:
        return False
