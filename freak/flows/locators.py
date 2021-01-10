from ast import FunctionDef, parse
from collections import defaultdict
from inspect import isfunction

from freak.types import Flow, Step

"""
    Inherit this class to implement new locator for your custom flow decorator.
"""


class Locator:
    def __init__(self, module: object, file_path: str, decorator: str):
        self.loaded_module = module
        self.file_path = file_path
        self.decorator = decorator

    def locate(self) -> Flow:
        file_path = self.file_path
        decorator = self.decorator

        with open(file=file_path, mode="rt") as file:
            tree = parse(source=file.read(), filename=file_path)
            predecessor = defaultdict(list)
            successor = {}
            for part in tree.body:
                if not (isinstance(part, FunctionDef) and part.decorator_list):
                    continue

                for deco in part.decorator_list:
                    if deco.func.id != decorator:  # type: ignore
                        continue

                    deco_kws = {
                        kw.arg: kw.value.value
                        for kw in deco.keywords  # type: ignore
                        if kw.arg in ("order", "uid", "parent_uid")
                    }

                    parent_uid = deco_kws.get("parent_uid", "")
                    uid = deco_kws.get("uid")
                    if (
                        not uid
                        or (parent_uid == "")
                        or not deco_kws.get("order")
                    ):
                        raise Exception("InvalidFlowDefintiionError")

                    predecessor[parent_uid].append(uid)

                    func = self.loaded_module.__dict__[part.name]
                    if not isfunction(object=func):
                        continue

                    successor[uid] = Step(
                        uid=uid,
                        parent_uid=parent_uid,
                        order=deco_kws["order"],
                        name=part.name,
                        function=func,
                    )

        return Flow(predecessor=predecessor, successor=successor)
