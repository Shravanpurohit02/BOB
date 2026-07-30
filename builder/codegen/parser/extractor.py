from builder.codegen.artifacts import (
    GeneratedArtifact,
    GeneratedDirectory,
    GeneratedFile,
)
from builder.codegen.parser.json import parser as json_parser
from builder.codegen.parser.markdown import parser as markdown_parser


class Extractor:

    SCHEMA = "vidhi-builder/v1"

    def artifacts(self, response):

        try:
            obj = json_parser.parse(response)
        except Exception:
            return []

        if obj.get("schema") != self.SCHEMA:
            return []

        artifact = GeneratedArtifact()

        for directory in obj.get("directories", []):
            artifact.directories.append(
                GeneratedDirectory(
                    path=directory["path"],
                )
            )

        for file in obj.get("files", []):
            artifact.files.append(
                GeneratedFile(
                    path=file["path"],
                    action=file.get("action", "modify"),
                    language=file.get("language", "python"),
                    content=file["content"],
                )
            )

        return [artifact]

    def code(self, response):

        try:
            obj = json_parser.parse(response)

            if obj.get("schema") == self.SCHEMA:
                return ""
        except Exception:
            pass

        return markdown_parser.extract(response)


extractor = Extractor()
