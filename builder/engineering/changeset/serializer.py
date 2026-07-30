from dataclasses import asdict
import json


class Serializer:

    def dumps(self, obj):

        return json.dumps(
            asdict(obj),
            indent=2,
            ensure_ascii=False,
        )

    def dump(self, obj, path):

        path.write_text(
            self.dumps(obj),
            encoding="utf-8",
        )


serializer = Serializer()
