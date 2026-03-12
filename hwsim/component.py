import re
from collections import defaultdict


from trit import ZERO, POS, NEG


BUS_RE = re.compile(r'^(\w+)\[(\d+)]$')


class Primitive:
    """Primitive is the base class for all components.

    The Primitive class can be subclassed directly to create basic logic gates
    with individual input and output trits, where the output is defined in
    software.

    Direct subclasses of Primitive must not contain any mutable attributes, and
    would typically be used with a singleton pattern.

    For more complex behaviour, or linking multiple Primitive components
    together, use the Component class.
    """
    buses: dict | None = None
    inputs: tuple = tuple()
    outputs: tuple = tuple()

    def __init__(self, inputs, outputs):
        self.inputs = tuple(inputs)
        self.outputs = tuple(outputs)

    def get_outputs(self, inputs):
        raise NotImplementedError()

    def evaluate(self, values=None):
        if values is None:
            values = tuple()

        inputs = defaultdict(lambda x: ZERO)
        if isinstance(values, (list, tuple, str)):
            inputs.update(zip(self.inputs, values))
        else:
            inputs.update(values)

        return self.get_outputs(inputs)


class Component(Primitive):
    def __init__(self, inputs: tuple, outputs: tuple, components=None,
                 connections=None):
        self.buses = {}
        input_items = []
        output_items = []
        for name in inputs:
            m = BUS_RE.match(name)
            if m:
                name = m.group(1)
                size = int(m.group(2))
                input_items.extend([f'{name}[{i}]' for i in range(size)])
                self.buses[name] = size
            else:
                input_items.append(name)

        for name in outputs:
            m = BUS_RE.match(name)
            if m:
                name = m.group(1)
                size = int(m.group(2))
                output_items.extend([f'{name}[{i}]' for i in range(size)])
                self.buses[name] = size
            else:
                output_items.append(name)

        super().__init__(input_items, output_items)

        self.cache = {}
        self.components = {}
        self.connections = {}
        if components:
            # Each member of 'components' should be either an instance that
            # inherits Primitive, or a callable that returns the same.
            for name, item in components.items():
                comp = item
                if not isinstance(item, Primitive):
                    comp = item()
                self.components[name] = comp
                if comp.buses:
                    for bus, size in comp.buses.items():
                        self.buses[f'{name}.{bus}'] = size

        if connections:
            for dest, source in connections.items():
                self.add_connection(dest, source)

    def add_connection(self, dest: str, source: str):
        if dest not in self.buses:
            self.connections[dest] = source
            return

        size = self.buses[dest]
        if source in self.buses:
            if self.buses[source] != size:
                raise ValueError(
                    f"Connection {dest} <- {source} is not "
                    "valid, both endpoints are buses but have "
                    "different sizes")
            for i in range(size):
                self.connections[f'{dest}[{i}]'] = f'{source}[{i}]'
        else:
            for i in range(size):
                self.connections[f'{dest}[{i}]'] = source

    def get_value(self, inputs: dict, name: str):
        if name in self.inputs:
            return inputs[name]

        if name in self.connections:
            source = self.connections[name]
            # Literal trit values are treated as a constant source
            if source in (ZERO, POS, NEG):
                return source

            if source in self.inputs:
                return inputs[source]

            if source in self.cache:
                return self.cache[source]

            sub, _ = source.split('.')
            self.evaluate_subcomponent(inputs, sub)
            return self.cache[source]

    def evaluate_subcomponent(self, inputs, name: str):
        comp = self.components[name]
        subinputs = {}
        for n in comp.inputs:
            subinputs[n] = self.get_value(inputs, f'{name}.{n}')
        outs = comp.get_outputs(subinputs)
        self.cache.update({
            f'{name}.{n}': outs[i] for i, n in enumerate(comp.outputs)})

    def get_outputs(self, inputs):
        return tuple(self.get_value(inputs, x) for x in self.outputs)


class NAnd(Primitive):
    """The NAND gate produces the inverse conjunction of its inputs.

    The NAND operation is equivalent to performing an AND operation, and then
    inverting its result:

    |   | - | 0 | + |
    |===|===|===|===|
    | - | + | + | + |
    | 0 | + | 0 | 0 |
    | + | + | 0 | - |
    """
    def __init__(self):
        super().__init__(('a', 'b'), ('out',))

    def get_outputs(self, inputs):
        """Return the logical NAND of 'a' and 'b'.

        The result is positive if either input is negative, negative if both
        inputs are positive, and otherwise zero.
        """
        a = inputs['a']
        b = inputs['b']
        if a == NEG or b == NEG:
            return (POS,)
        elif a == POS and b == POS:
            return (NEG,)
        else:
            return (ZERO,)


class Not(Primitive):
    """The NOT gate produces the inverse of its input.

    For positive or negative input, it produces the opposite value. For zero
    input, it produces zero.

    | in  | out |
    |=====|=====|
    |  -  |  +  |
    |  0  |  0  |
    |  +  |  -  |
    """
    def __init__(self):
        super().__init__(('in',), ('out',))

    def get_outputs(self, inputs):
        inp = inputs['in']
        if inp == ZERO:
            return (ZERO,)
        return (NEG,) if inp == POS else (POS,)


class PNot(Primitive):
    """The PNOT gate produces the positively-biased inverse of its input.

    For positive or negative input, it works just like a normal NOT gate, but
    for zero input, it produces a positive output:

    | in  | out |
    |=====|=====|
    |  -  |  +  |
    |  0  |  +  |
    |  +  |  -  |
    """
    def __init__(self):
        super().__init__(('in',), ('out',))

    def get_outputs(self, inputs):
        inp = inputs['in']
        return (NEG,) if inp == POS else (POS,)


class NNot(Primitive):
    """The NNOT gate produces the negatively-biased inverse of its input.

    For positive or negative input, it works just like a normal NOT gate, but
    for zero input, it produces a negative output:

    | in  | out |
    |=====|=====|
    |  -  |  +  |
    |  0  |  -  |
    |  +  |  -  |
    """
    def __init__(self):
        super().__init__(('in',), ('out',))

    def get_outputs(self, inputs):
        inp = inputs['in']
        return (POS,) if inp == NEG else (NEG,)


class NOr(Primitive):
    """The NOR gate produces the inverse disjunction of its inputs.

    Where either (or both) inputs are positive, it produces a negative. Where
    both inputs are negative, it produces a positive. In any other case, it
    produces zero.

    |   | - | 0 | + |
    |===|===|===|===|
    | - | + | 0 | - |
    | 0 | 0 | 0 | - |
    | + | - | - | - |
    """
    def __init__(self):
        super().__init__(('a', 'b',), ('out',))

    def get_outputs(self, inputs):
        a = inputs['a']
        b = inputs['b']
        if a == POS or b == POS:
            return (NEG,)
        if a == NEG and b == NEG:
            return (POS,)
        return (ZERO,)


class NAny(Primitive):
    """The NANY gate produces the inverse ANY of its inputs.

    For cases where either input is zero, it produces the NOT of its other
    input. Where one input is positive and the other negative, it produces
    zero. Otherwise, when both inputs are the same, it produces the inverse of
    that value.

    |   | - | 0 | + |
    |===|===|===|===|
    | - | + | + | 0 |
    | 0 | + | 0 | - |
    | + | 0 | - | - |
    """
    def __init__(self):
        super().__init__(('a', 'b',), ('out',))

    def get_outputs(self, inputs):
        a = inputs['a']
        b = inputs['b']
        if a == NEG:
            return (ZERO,) if b == POS else (POS,)
        if a == POS:
            return (ZERO,) if b == NEG else (NEG,)
        if b == ZERO:
            return (ZERO,)
        return (POS,) if b == NEG else (NEG,)


class NCons(Primitive):
    """The NCONS gate produces the inverse consensus of its inputs.

    For cases where both inputs have the same value, it produces the inverse of
    that value. In all other cases, it produces zero.

    |   | - | 0 | + |
    |===|===|===|===|
    | - | + | 0 | 0 |
    | 0 | 0 | 0 | 0 |
    | + | 0 | 0 | - |
    """
    def __init__(self):
        super().__init__(('a', 'b',), ('out',))

    def get_outputs(self, inputs):
        a = inputs['a']
        b = inputs['b']
        if a == b and a != ZERO:
            return (NEG,) if a == POS else (POS,)
        return (ZERO,)


# The primitive gates have get_outputs as a pure function, and have no mutable
# attributes, so prepare singletons for them.
NOT = Not()
NNOT = NNot()
PNOT = PNot()
NAND = NAnd()
NOR = NOr()
NANY = NAny()
NCONS = NCons()
