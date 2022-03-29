from functools import partial

import andi


class Inject:
    pass


def _build(plan, instances_stock=None):
    instances_stock = instances_stock or {}
    instances = {}
    for fn_or_cls, kwargs_spec in plan:
        if fn_or_cls in instances_stock:
            instances[fn_or_cls] = instances_stock[fn_or_cls]
        else:
            instances[fn_or_cls] = fn_or_cls(**kwargs_spec.kwargs(instances))
    return instances


def inject_everything(_):
    # return True
    return issubclass(_, Inject)


def get_instance(cls, ext=None):
    plan = andi.plan(cls, is_injectable=inject_everything, externally_provided=ext)
    instances = _build(plan)
    return instances[cls]


def get_method(func, dependencies=None):
    externally_provided = {c.__class__ for c in dependencies}
    instances = {c.__class__: c for c in dependencies}

    plan = andi.plan(func, is_injectable=inject_everything, externally_provided=externally_provided)
    instances = _build(plan.dependencies, instances)
    return partial(func, **plan.final_kwargs(instances))

# class Demo(Inject):
#     def __init__(self):
#        pass
#
#
# def vroem(speed: int, d: Demo):
#     print(type(speed))
#     print("I'm in my moms", d)
#     print(f"Driving {speed} mph")
#
# _vroem = get_method(vroem)
# _vroem("100")
