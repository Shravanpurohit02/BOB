class Pipeline:

    STAGES = [
        "workspace",
        "reflection",
        "dependency",
        "planning",
        "generation",
        "validation",
        "patch",
        "testing",
        "deployment",
    ]

    def stages(self):
        return list(self.STAGES)

pipeline = Pipeline()
