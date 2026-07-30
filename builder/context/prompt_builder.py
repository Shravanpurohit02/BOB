class PromptBuilder:

    MAX_MODULES = 30

    def build(
        self,
        objective,
        project,
        modules,
        files=None,
    ):

        if files is None:
            files = []

        module_lines = [
            f"- {m.path}"
            for m in modules[:self.MAX_MODULES]
        ]

        parts = [
            "You are Vidhi Builder.",
            "",
            "Repository Context",
            "==================",
            "",
            "Project Summary:",
            str(project),
            "",
            f"Relevant Modules: {len(modules)}",
            "",
            "Primary Modules",
            "===============",
            *module_lines,
        ]

        for file in files:
            parts.extend([
                "",
                "Relevant File",
                "=============",
                f"Path: {file['path']}",
                f"Lines: {file['lines']}",
                "",
                "Source",
                "======",
                file["source"],
            ])

        parts.extend([
            "",
            "Engineering Objective",
            "=====================",
            objective,
            "",
            "Requirements",
            "============",
            "- Modify existing files whenever possible.",
            "- Preserve unaffected code.",
            "- Do not invent filenames.",
            "- Update imports when required.",
            "- Return Builder Output Specification JSON only.",
        ])

        return "\n".join(parts)


builder = PromptBuilder()
