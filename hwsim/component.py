from collections import defaultdict


from trit import ZERO, POS, NEG


class Primitive:
    inputs = tuple()
    outputs = tuple()

    def __init__(self, inputs, outputs):
        self.inputs = tuple(inputs)
        self.outputs = tuple(outputs)

    def get_outputs(self, inputs):
        raise NotImplementedError()

    def evaluate(self, values=None):
        if values is None:
            values = tuple()

        inputs = defaultdict(lambda x: ZERO)
        if isinstance(values, (list, tuple)):
            inputs.update(zip(self.inputs, values))
        else:
            inputs.update(values)

        return self.get_outputs(inputs)


class Component(Primitive):
    def __init__(self, inputs: int = 2, outputs: int = 1, components=None,
                 connections=None):
        super().__init__(inputs, outputs)

        self.cache = {}
        self.components = {}
        self.connections = {}
        if components:
            for name, item in components.items():
                if isinstance(item, Primitive):
                    self.components[name] = item
                else:
                    self.components[name] = item()

        if connections:
            self.connections.update(connections)

    def get_value(self, inputs: dict, name: str):
        if name in self.inputs:
            return inputs[name]

        if name in self.connections:
            source = self.connections[name]
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


class Nand(Primitive):
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


# The Nand gate has get_outputs as a pure function, so use it as a singleton
NAND = Nand()


def not_gate():
    """The NOT gate performs logical negation of the input.

    It contains a single NAND. The input of the NOT gate is routed to both
    inputs of the NAND.

    (NOT a) == (a NAND a)
    """
    return Component(
            ('in',),
            ('out',),
            {'Nand': NAND},
            {
                    'out': 'Nand.out',
                    'Nand.a': 'in',
                    'Nand.b': 'in',
                    })
