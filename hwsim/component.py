import re
from collections.abc import Callable, Iterable
from typing import Literal


from trit import ZERO, POS, NEG

Trit = Literal[NEG, ZERO, POS]
Trits = Iterable[Trit]


BUS_RE = re.compile(r'^(\w+)\[(\d+)]$')
BUS_SLICE_RE = re.compile(r'^([\w.]+)\[(\d+)\.\.(\d+)]$')


class Primitive:
    """Primitive is the abstract base class for all components.

    The Primitive class can be subclassed directly to create basic logic gates
    with individual input and output trits, where the output is defined in
    software.

    Direct subclasses of Primitive must not contain any mutable attributes, and
    would typically be used with a singleton pattern.

    For more complex behaviour, or linking multiple components together, use
    the Component class.
    """
    buses: dict | None = None
    inputs: tuple[str] = tuple()
    outputs: tuple[str] = tuple()
    deferred: bool = False

    def __init__(self, inputs: Iterable[str], outputs: Iterable[str]):
        self.inputs = tuple(inputs)
        self.outputs = tuple(outputs)

    def get_outputs(self, inputs: Trits) -> Trits:
        raise NotImplementedError()

    def tick(self) -> bool:
        """Update the component in response to a clock pulse.

        Return True if the component's state has changed as a result of the
        tick, and False if it has remained exactly the same.
        """
        return False


ComponentCompatible = Primitive | Callable


class Component(Primitive):
    deferred: bool = False

    def __init__(
            self,
            inputs: Iterable[str],
            outputs: Iterable[str],
            components: dict[str, ComponentCompatible] | None = None,
            connections: dict[str, str] | None = None):
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
            # Each value of 'components' should be either an instance that
            # inherits Primitive, or a callable that returns such an instance.
            for name, item in components.items():
                comp = item
                if not isinstance(comp, Primitive):
                    # Not already an instance, try invoking it as a callable
                    comp = item()
                assert isinstance(comp, Primitive)
                self.components[name] = comp
                if comp.buses:
                    for bus, size in comp.buses.items():
                        self.buses[f'{name}.{bus}'] = size

        if connections:
            for dest, source in connections.items():
                self.add_connection(dest, source)

    def add_connection(self, dest: str, source: str) -> None:
        m = BUS_SLICE_RE.match(dest)
        if m:
            # Dest uses slice notation [x..y]
            dest_name = m.group(1)
            dest_start = int(m.group(2))
            dest_end = int(m.group(3))
            if dest_start > dest_end:
                raise ValueError(
                        f"Invalid bus slice {dest}: "
                        "start of range is after the end")
            dest_size = dest_end - dest_start + 1
        elif dest in self.buses:
            # Dest refers to a whole bus
            dest_name = dest
            dest_start = 0
            dest_size = self.buses[dest]
        else:
            # Simple case with no buses involved, this is just a single trit
            # connection.
            self.connections[dest] = source
            return

        m = BUS_SLICE_RE.match(source)
        if m:
            # Source uses slice notation [x..y]
            source_name = m.group(1)
            source_start = int(m.group(2))
            source_end = int(m.group(3))
            if source_start > source_end:
                raise ValueError(
                        f"Invalid bus slice {source}: "
                        "start of range is after the end")
            source_size = source_end - source_start + 1
        elif source in self.buses:
            # Source refers to a whole bus
            source_name = source
            source_start = 0
            source_size = self.buses[source]
        else:
            # Source is a single trit, and dest is a bus, so fan out the single
            # source to all wires on the destination.
            for i in range(dest_size):
                self.connections[f'{dest_name}[{i}]'] = source
            return

        # If we've arrived here, then there is a bus (or slice) on both sides
        # of the connection
        if dest_size != source_size:
            raise ValueError(
                f"Invalid connection {dest} <- {source}: "
                "both endpoints are buses but have different sizes")

        i = dest_start
        j = source_start
        for _ in range(dest_size):
            self.connections[f'{dest_name}[{i}]'] = f'{source_name}[{j}]'
            i += 1
            j += 1

    def get_value(self, name: str) -> Trit:
        # Literal trit values are treated as a constant source
        if name in (ZERO, POS, NEG):
            return name

        if name in self.cache:
            return self.cache[name]

        if name in self.connections:
            source = self.connections[name]
            if source in self.cache:
                return self.cache[source]

            try:
                if '.' in source:
                    comp, _ = source.split('.')
                    self.evaluate_subcomponent(comp)
                    value = self.cache[source]
                    self.cache[name] = value
                    return value
                return self.get_value(source)
            except ValueError as e:
                raise ValueError(
                        f"Failed to get value for {name} <- {source}: {e}")

        raise ValueError(f"'{name}' does not exist in this component")

    def invalidate_cache(self, name: str) -> None:
        prefix = f'{name}.'
        self.cache = {
                k: v for k, v in self.cache.items()
                if k != name and not k.startswith(prefix)}

    def update(self) -> bool:
        return False

    def update_subcomponents(self) -> bool:
        changed = False
        for name, comp in self.components.items():
            if comp.deferred:
                # We previously deferred setting the inputs for this
                # subcomponent, so set them now.
                inputs = tuple(
                        self.get_value(f'{name}.{x}') for x in comp.inputs)
                comp.set_inputs(inputs)
            if comp.tick():
                changed = True
        if changed:
            for name in self.components.keys():
                self.invalidate_cache(name)
        return changed

    def tick(self) -> bool:
        changed = False
        if self.update():
            changed = True
        if self.update_subcomponents():
            changed = True
        self.cache = {
                k: v for k, v in self.cache.items()
                if k not in self.outputs}
        return changed

    def evaluate_subcomponent(self, name: str) -> Trits:
        comp = self.components[name]
        if comp.deferred:
            inputs = None
        else:
            inputs = tuple(self.get_value(f'{name}.{x}') for x in comp.inputs)
        outputs = comp.get_outputs(inputs)
        self.cache.update({
            f'{name}.{comp.outputs[i]}': x for i, x in enumerate(outputs)})
        return outputs

    def set_inputs(self, inputs: Trits) -> None:
        changed = False
        cache = {}
        for i, name in enumerate(self.inputs):
            if inputs[i] != self.cache.get(name):
                changed = True
            cache[name] = inputs[i]
        if changed:
            self.cache = cache

    def get_outputs(self, inputs: Trits | None = None) -> Trits:
        """Get the output values for this component.

        Normal (non-deferred) components need all of their inputs defined in
        order to calculate their outputs.

        Deferred components (e.g., memory registers) can provide their outputs
        without any inputs, but they will respond to their inputs during a
        clock tick.
        """
        if inputs is not None:
            self.set_inputs(inputs)
        return tuple(self.get_value(name) for name in self.outputs)


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

    def get_outputs(self, inputs: Trits) -> Trits:
        """Return the logical NAND of 'a' and 'b'.

        The result is positive if either input is negative, negative if both
        inputs are positive, and otherwise zero.
        """
        a, b = inputs
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

    def get_outputs(self, inputs: Trits) -> Trits:
        (inp,) = inputs
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

    def get_outputs(self, inputs: Trits) -> Trits:
        (inp,) = inputs
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

    def get_outputs(self, inputs: Trits) -> Trits:
        (inp,) = inputs
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

    def get_outputs(self, inputs: Trits) -> Trits:
        a, b = inputs
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

    def get_outputs(self, inputs: Trits) -> Trits:
        a, b = inputs
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

    def get_outputs(self, inputs: Trits) -> Trits:
        a, b = inputs
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
