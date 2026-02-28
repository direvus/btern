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


class PNot(Primitive):
    """The PNOT gate produces the positively-biased inverse of its input.

    For positive or negative input, it works just like a normal NOT gate, but
    for zero input, it produces a positive output:

    | in | out |
    |====|=====|
    |  - |  +  |
    |  0 |  +  |
    |  + |  -  |
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

    | in | out |
    |====|=====|
    |  - |  +  |
    |  0 |  -  |
    |  + |  -  |
    """
    def __init__(self):
        super().__init__(('in',), ('out',))

    def get_outputs(self, inputs):
        inp = inputs['in']
        return (POS,) if inp == NEG else (NEG,)


# The primitive gates have get_outputs as a pure function, and have no mutable
# attributes, so prepare singletons for them.
NAND = Nand()
NNOT = NNot()
PNOT = PNot()


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


def and_gate():
    """The AND gate performs logical conjunction of the inputs.

    The output is true if and only if both inputs are true.

    It consists of two NAND gates. The first performs NAND on the two inputs,
    and the second performs NOT on the result.

    (a AND b) == NOT (a NAND b)
    """
    return Component(
            ('a', 'b'),
            ('out',),
            {'Nand': NAND, 'Not': not_gate},
            {
                    'out': 'Not.out',
                    'Not.in': 'Nand.out',
                    'Nand.a': 'a',
                    'Nand.b': 'b',
                    })


def or_gate():
    """The OR gate performs logical disjunction of the inputs.

    The output is true if either (or both) of the inputs are true.

    It consists of two NOT gates and one NAND gate (three NANDs total). The
    two NOT gates first negate each of the inputs, and the NAND gate takes the
    inverted inputs and produces the final result.

    (a OR b) == ((NOT a) NAND (NOT b))
    """
    return Component(
            ('a', 'b'),
            ('out',),
            {'Nand': NAND, 'NotA': not_gate, 'NotB': not_gate},
            {
                    'out': 'Nand.out',
                    'Nand.a': 'NotA.out',
                    'Nand.b': 'NotB.out',
                    'NotA.in': 'a',
                    'NotB.in': 'b',
                    })


def xor_gate():
    """The XOR gate performs logical exclusive disjunction of the inputs.

    The output is true if either one of the inputs is true, but not both.

    It consists of one OR, one NAND and one AND gate (six NANDs total). The two
    inputs are both separately passed to the OR gate and the NAND gate, and the
    AND gate finally combines the results of those two to produce the output.

    (a XOR b) == (a OR b) AND (a NAND b)
    """
    return Component(
            ('a', 'b'),
            ('out',),
            {'Nand': NAND, 'Or': or_gate, 'And': and_gate},
            {
                    'out': 'And.out',
                    'And.a': 'Or.out',
                    'And.b': 'Nand.out',
                    'Or.a': 'a',
                    'Or.b': 'b',
                    'Nand.a': 'a',
                    'Nand.b': 'b',
                    })


def isz_gate():
    """The ISZ gate tests whether the input is zero.

    The output is positive if the input value is zero, and negative otherwise.

    | in | out |
    |====|=====|
    |  - |  -  |
    |  0 |  +  |
    |  + |  -  |

    It consists of two NNOTs, one PNOT, and one AND gate, for a total of
    4 primitive gates.

    ISZ a == (PNOT a) AND (NOT NNOT a)
    """
    return Component(
            ('in',),
            ('out',),
            {
                'PNot': PNOT,
                'NNot': NNOT,
                'Not': NNOT,
                'And': and_gate,
            },
            {
                'out': 'And.out',
                'And.a': 'PNot.out',
                'And.b': 'Not.out',
                'PNot.in': 'in',
                'Not.in': 'NNot.out',
                'NNot.in': 'in',
                })
