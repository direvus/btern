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
    def __init__(self, inputs: tuple, outputs: tuple, components=None,
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


def and_gate():
    """The AND gate performs logical conjunction of the inputs.

    The output is true if and only if both inputs are true.

    (a AND b) == NOT (a NAND b)
    """
    return Component(
            ('a', 'b'),
            ('out',),
            {'Nand': NAND, 'Not': NOT},
            {
                    'out': 'Not.out',
                    'Not.in': 'Nand.out',
                    'Nand.a': 'a',
                    'Nand.b': 'b',
                    })


def or_gate():
    """The OR gate performs logical disjunction of the inputs.

    The output is true if either (or both) of the inputs are true.

    (a OR b) == NOT (a NOR b)
    """
    return Component(
            ('a', 'b'),
            ('out',),
            {'Nor': NOR, 'Not': NOT},
            {
                    'out': 'Not.out',
                    'Not.in': 'Nor.out',
                    'Nor.a': 'a',
                    'Nor.b': 'b',
                    })


def any_gate():
    """The ANY gate detects an overall bias of the inputs.

    The output is zero if the inputs are positive and negative, or both zero.
    Otherwise, the output is positive if there is any positive signal in the
    inputs, or negative if there is any negative signal.

    (a ANY b) == NOT (a NANY b)
    """
    return Component(
            ('a', 'b'),
            ('out',),
            {'NAny': NANY, 'Not': NOT},
            {
                    'out': 'Not.out',
                    'Not.in': 'NAny.out',
                    'NAny.a': 'a',
                    'NAny.b': 'b',
                    })


def xor_gate():
    """The XOR gate performs logical exclusive disjunction of the inputs.

    The output is true if either one of the inputs is true, but not both.

    It consists of four primitive gates: a NAND, a NOT and two NORS. Both
    inputs are separately passed to a NAND gate and a NOR gate, the result of
    the NAND is inverted, and those two results are passed to a NOR gate to
    produce the final output.

    (a XOR b) == (NOT (a NAND b)) NOR (a NOR b)
    """
    return Component(
            ('a', 'b'),
            ('out',),
            {'Nand': NAND, 'NorAB': NOR, 'Not': NOT, 'NorOut': NOR},
            {
                    'out': 'NorOut.out',
                    'NorOut.a': 'Not.out',
                    'NorOut.b': 'NorAB.out',
                    'Not.in': 'Nand.out',
                    'Nand.a': 'a',
                    'Nand.b': 'b',
                    'NorAB.a': 'a',
                    'NorAB.b': 'b',
                    })


def nxor_gate():
    """The NXOR gate performs negative exclusive disjunction of the inputs.

    The output is positive if the inputs are either both positive, or both
    negative.

    It consists of four primitive gates: two NANDs, a NOR and a NOT. Both
    inputs are separately passed to a NAND gate and a NOR gate, the result of
    the NOR is inverted, and those two results are passed to a NAND gate to
    produce the final output.

    (a NXOR b) == (NOT (a NOR b)) NAND (a NAND b)
    """
    return Component(
            ('a', 'b'),
            ('out',),
            {'NandAB': NAND, 'NandOut': NAND, 'Nor': NOR, 'Not': NOT},
            {
                    'out': 'NandOut.out',
                    'NandOut.a': 'Not.out',
                    'NandOut.b': 'NandAB.out',
                    'Not.in': 'Nor.out',
                    'Nor.a': 'a',
                    'Nor.b': 'b',
                    'NandAB.a': 'a',
                    'NandAB.b': 'b',
                    })


def isz_gate():
    """The ISZ gate tests whether the input is zero.

    The output is positive if the input value is zero, and negative otherwise.

    | in  | out |
    |=====|=====|
    |  -  |  -  |
    |  0  |  +  |
    |  +  |  -  |

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


def mux_gate():
    """The MUX gate is a 3-way multiplexer.

    It selects one of its three data inputs, based on the value of a fourth
    'selector' input, and produces the selected input signal on its output.

    The three data inputs are named 'a', 'b' and 'c', and the selector input is
    named 's'. The input value is selected as follows:

    |  s  | out |
    |=====|=====|
    |  -  |  a  |
    |  0  |  b  |
    |  +  |  c  |

    The complete truth table for all four inputs is:

    |   | c | - | - | - | 0 | 0 | 0 | + | + | + |
    |   | s | - | 0 | + | - | 0 | + | - | 0 | + |
    | a | b |   |   |   |   |   |   |   |   |   |
    |===|===|===|===|===|===|===|===|===|===|===|
    | - | - | - | - | - | - | - | 0 | - | - | + |
    | - | 0 | - | 0 | - | - | 0 | 0 | - | 0 | + |
    | - | + | - | + | - | - | + | 0 | - | + | + |
    | 0 | - | 0 | - | - | 0 | - | 0 | 0 | - | + |
    | 0 | 0 | 0 | 0 | - | 0 | 0 | 0 | 0 | 0 | + |
    | 0 | + | 0 | + | - | 0 | + | 0 | 0 | + | + |
    | + | - | + | - | - | + | - | 0 | + | - | + |
    | + | 0 | + | 0 | - | + | 0 | 0 | + | 0 | + |
    | + | + | + | + | - | + | + | 0 | + | + | + |
    """
    return Component(
            ('a', 'b', 'c', 's'),
            ('out',),
            {
                'NandABC': NAND,
                'NandAB': NAND,
                'NandA': NAND,
                'NandB': NAND,
                'NandC': NAND,
                'NotAB': NOT,
                'NNot': NNOT,
                'ISZ': isz_gate,
                'PNot1': PNOT,
                'PNot2': PNOT,
                },
            {
                'out': 'NandABC.out',
                'NandABC.a': 'NotAB.out',
                'NandABC.b': 'NandC.out',
                'NotAB.in': 'NandAB.out',
                'NandAB.a': 'NandA.out',
                'NandAB.b': 'NandB.out',
                'NandA.a': 'a',
                'NandA.b': 'NNot.out',
                'NNot.in': 's',
                'NandB.a': 'b',
                'NandB.b': 'ISZ.out',
                'ISZ.in': 's',
                'NandC.a': 'c',
                'NandC.b': 'PNot2.out',
                'PNot2.in': 'PNot1.out',
                'PNot1.in': 's',
                })

