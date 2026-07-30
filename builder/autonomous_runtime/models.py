from dataclasses import dataclass,field


@dataclass(slots=True)
class RuntimeContext:

    objective:str=""

    workspace:str=""

    pipeline:object=None

    attempts:int=0

    metadata:dict=field(default_factory=dict)


@dataclass(slots=True)
class RuntimeResult:

    success:bool=False

    completed:bool=False

    context:RuntimeContext|None=None

    history:list[str]=field(default_factory=list)
