from __future__ import annotations
import re
from collections.abc import Callable, Iterable

from trit import ZERO, POS, NEG
from hwsim.util import Trit, Trits


BUS_RE = re.compile(r'^(\w+)\[(\d+)]$')
BUS_SLICE_RE = re.compile(r'^([\w.]+)\[(\d+)\.\.(\d+)]$')


class Primitive:
    """Primitive is the abstract base class for all components.

    The Primitive class can be subclassed directly to create basic logic gates
    with individual input and output trits, where the output is defined in
    Python code, rather than in simulated circuitry.

    For more complex behaviour, or linking multiple components together, use
    the Component class.
    """
    buses: dict | None = None
    inputs: tuple[str] = tuple()
    outputs: tuple[str] = tuple()
    parent: Component | None = None
    name: str = ''

    def __init__(self, inputs: Iterable[str], outputs: Iterable[str]):
        self.inputs = tuple(inputs)
        self.outputs = tuple(outputs)
        self.cache = {}

    def set_name(self, name: str) -> None:
        self.name = name

    def set_parent(self, parent: Component) -> None:
        self.parent = parent

    def set_inputs(self, inputs: Trits) -> None:
        """Set this component's inputs and remove all other cache entries."""
        self.cache = dict(zip(self.inputs, inputs))

    def get_input(self, name: str) -> Trit:
        if name in self.cache:
            return self.cache[name]

        if self.parent is None:
            raise ValueError(
                    f"{self.name} needs input '{name}', but no parent is set.")
        value = self.parent.get_value(f'{self.name}.{name}')
        self.cache[name] = value
        return value

    def get_outputs(self, inputs: Trits | None = None) -> Trits:
        """Return the outputs for this component, given its inputs.

        This is the method that direct inheriting classes need to override to
        define their logic.
        """
        raise NotImplementedError()

    def get_output(self, name: str) -> Trit:
        """Return a single output for this component.

        The default behaviour for a Primitive component is to request all
        inputs up front, calculate all outputs and return the named one, but
        inheriting classes are free to override these methods to get different
        behaviour.
        """
        inputs = tuple(self.get_input(x) for x in self.inputs)
        self.set_inputs(inputs)
        index = self.outputs.index(name)
        return self.get_outputs(inputs)[index]

    def update(self) -> bool:
        """Update the component in response to a clock pulse.

        Return True if the component's state has changed as a result of the
        tick, and False if it has remained exactly the same.

        The default behaviour is to do nothing and return False.
        """
        return False

    def clear_cache(self) -> None:
        self.cache = {}


ComponentCompatible = Primitive | Callable


class Component(Primitive):
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
            # In either case, we will attach a parent reference to each
            # instance that we add as a subcomponent.
            for name, item in components.items():
                comp = item
                if not isinstance(comp, Primitive):
                    # Not already an instance, try invoking it as a callable
                    comp = item()
                assert isinstance(comp, Primitive)
                comp.set_name(name)
                comp.set_parent(self)
                self.components[name] = comp
                if comp.buses:
                    for bus, size in comp.buses.items():
                        self.buses[f'{name}.{bus}'] = size

        if connections:
            for dest, source in connections.items():
                self.add_connection(dest, source)

    def expand_bus(self, name: str) -> Iterable[str]:
        """Expand a name that could be a bus or bus slice.

        If the name matches a bus on this component, it is expanded to a
        listing of each of the connections in the bus; name[0], name[1],
        name[2], ..., name[size-1].

        If the name uses a slice notation in the form name[x..y] then it
        expands to just the connections between x and y, inclusive.

        If the name is not a bus nor a slice, then it just returns itself as an
        iterable of one item.
        """
        m = BUS_SLICE_RE.match(name)
        if m:
            # Dest uses slice notation [x..y]
            bus = m.group(1)
            start = int(m.group(2))
            end = int(m.group(3))
            if start > end:
                raise ValueError(
                        f"Invalid bus slice {name}: "
                        "start of range is after the end")
            return tuple(f'{bus}[{i}]' for i in range(start, end + 1))

        if name in self.buses:
            size = self.buses[name]
            return tuple(f'{name}[{i}]' for i in range(size))

        return (name,)

    def add_connection(self, dest: str, source: str) -> None:
        dest_items = self.expand_bus(dest)
        dest_size = len(dest_items)
        if dest_size == 1:
            # Simple case with no buses involved, this is just a single trit
            # connection.
            self.connections[dest] = source
            return

        source_items = self.expand_bus(source)
        source_size = len(source_items)
        if source_size == 1:
            # Source is a single trit, and dest is multiple, so fan out the
            # single source to all wires on the destination.
            for item in dest_items:
                self.connections[item] = source_items[0]
            return

        # If we've arrived here, then there is a bus (or slice) on both sides
        # of the connection, so they had better be the same size.
        if dest_size != source_size:
            raise ValueError(
                f"Invalid connection {dest} <- {source}: "
                "both endpoints are buses but have different sizes")

        self.connections.update(dict(zip(dest_items, source_items)))

    def get_value(self, name: str) -> Trit:
        # Literal trit values are treated as a constant source
        if name in (ZERO, POS, NEG):
            return name

        if name in self.cache:
            return self.cache[name]

        if name in self.inputs:
            value = self.get_input(name)
            self.cache[name] = value
            return value

        if name in self.connections:
            source = self.connections[name]
            if source in self.cache:
                return self.cache[source]

            try:
                if '.' in source:
                    value = self.get_subcomponent_output(*source.split('.'))
                    self.cache[name] = value
                    return value
                return self.get_value(source)
            except ValueError as e:
                raise ValueError(
                        f"Failed to get value for {name} <- {source}: {e}")

        raise ValueError(f"'{name}' does not exist in this component")

    def invalidate_cache(self, name: str) -> None:
        """Remove all cache entries for a subcomponent."""
        prefix = f'{name}.'
        self.cache = {
                k: v for k, v in self.cache.items()
                if k != name and not k.startswith(prefix)}

    def clear_cache(self) -> None:
        """Clear the cache of this component and all its descendants."""
        self.cache = {}
        for comp in self.components.values():
            comp.clear_cache()

    def update_local(self) -> bool:
        return False

    def update_subcomponents(self) -> set[str]:
        """Recursively update all subcomponents.

        Return the names of the subcomponents that indicated changes, as a set.
        """
        changed = set()
        for name, comp in self.components.items():
            if comp.update():
                changed.add(name)
        return changed

    def update(self) -> bool:
        changed = False
        if self.update_local():
            changed = True
        if self.update_subcomponents():
            changed = True
        return changed

    def tick(self) -> bool:
        changed = self.update()
        # Remove everything from the cache except for the inputs to this
        # component, and completely clear the caches of all subcomponents.
        self.cache = {
                k: v for k, v in self.cache.items()
                if k in self.inputs}
        for comp in self.components.values():
            comp.clear_cache()
        return changed

    def get_subcomponent_output(self, component: str, name: str) -> Trit:
        comp = self.components[component]
        return comp.get_output(name)

    def get_outputs(self, inputs: Trits | None = None) -> Trits:
        """Get the output values for this component, given its inputs."""
        if inputs is not None:
            self.set_inputs(inputs)
        return tuple(self.get_value(name) for name in self.outputs)

    def get_output(self, name: str) -> Trit:
        return self.get_value(name)


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
