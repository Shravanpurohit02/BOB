from pathlib import Path

class Resolver:

    def find(self,workspace,name):

        for f in Path(workspace).rglob(name):
            return str(f)

        return None

resolver=Resolver()
