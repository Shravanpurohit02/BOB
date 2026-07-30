from builder.ast import engine


FEATURES = {
    "builder": (
        "builder",
        "orchestrator",
        "context",
        "autonomous",
        "deployment",
        "validation",
        "testing",
        "engineering",
    ),
    "research": (
        "research",
        "legal",
        "citation",
        "precedent",
        "judgment",
    ),
    "drafting": (
        "drafting",
        "template",
        "clause",
        "affidavit",
        "petition",
        "agreement",
    ),
    "rag": (
        "rag",
        "embedding",
        "vector",
        "retriever",
        "reranker",
        "chunk",
        "semantic",
    ),
    "court": (
        "court",
        "ecourts",
        "cause",
        "hearing",
    ),
    "document": (
        "document",
        "ocr",
        "parser",
        "upload",
        "pdf",
        "docx",
    ),
    "auth": (
        "auth",
        "security",
        "session",
        "token",
        "password",
        "user",
    ),
    "billing": (
        "invoice",
        "payment",
        "ledger",
        "finance",
    ),
    "ai": (
        "ai",
        "provider",
        "chat",
        "conversation",
        "reasoning",
        "llm",
    ),
}


class ModuleContext:

    def _score(self, module, keywords):
        text = " ".join(
            [
                module.path,
                *module.classes,
                *module.functions,
                *module.imports,
            ]
        ).lower()

        return sum(text.count(word) for word in keywords)

    def build(self, workspace, objective=None):

        modules = engine.build(workspace)["modules"]

        if not objective:
            return modules

        objective = objective.lower()

        keywords = []

        for _, words in FEATURES.items():
            if any(word in objective for word in words):
                keywords.extend(words)

        if not keywords:
            return modules

        ranked = sorted(
            modules,
            key=lambda m: self._score(m, keywords),
            reverse=True,
        )

        ranked = [m for m in ranked if self._score(m, keywords) > 0]

        return ranked[:50] if ranked else modules


context = ModuleContext()
