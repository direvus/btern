#!/usr/bin/env python3
from itertools import product

from trit import NEG, ZERO, POS


BINARY_TARGETS = {
        'XOR': (NEG, ZERO, POS, ZERO, ZERO, ZERO, POS, ZERO, NEG),
        'NXOR': (POS, ZERO, NEG, ZERO, ZERO, ZERO, NEG, ZERO, POS),
        'sum': (POS, NEG, ZERO, NEG, ZERO, POS, ZERO, POS, NEG),
        'carry': (NEG, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO, POS),
        }
UNARY_TARGETS = {
        'CLU': (ZERO, POS, NEG),
        'inc_carry': (ZERO, ZERO, POS),
        }


def buffer(v):
    return v


def _not(v):
    if v == ZERO:
        return v
    return NEG if v == POS else POS


def pnot(v):
    return NEG if v == POS else POS


def nnot(v):
    return POS if v == NEG else NEG


def nand(a, b):
    if a == NEG or b == NEG:
        return POS
    if a == POS and b == POS:
        return NEG
    return ZERO


def nor(a, b):
    if a == POS or b == POS:
        return NEG
    if a == NEG and b == NEG:
        return POS
    return ZERO


def nany(a, b):
    if a == NEG:
        return ZERO if b == POS else POS
    if a == POS:
        return ZERO if b == NEG else NEG
    if b == ZERO:
        return ZERO
    return POS if b == NEG else NEG


def ncons(a, b):
    if a == b and a != ZERO:
        return NEG if a == POS else POS
    return ZERO


def nxor(a, b):
    if a == ZERO or b == ZERO:
        return ZERO
    return POS if a == b else NEG


INPUTS = tuple((a, b) for a in (NEG, ZERO, POS) for b in (NEG, ZERO, POS))
UNARY = (buffer, _not, pnot, nnot)
BINARY = (nand, nor, nany, ncons, nxor)

COST = {
        'buffer': 0,
        '_not': 1,
        'pnot': 1,
        'nnot': 1,
        'nand': 1,
        'nor': 1,
        'nany': 1,
        'ncons': 1,
        'nxor': 4,
        }


def test_gates_uubu(pre_a, pre_b, com, post, inputs, expected):
    def f(a, b):
        return post(com(pre_a(a), pre_b(b)))

    for i, a in enumerate(inputs):
        res = f(*a)
        if res != expected[i]:
            return False
    return True


def test_gates_bbbu(pre1, pre2, com, post, inputs, expected):
    def f(a, b):
        return post(com(pre1(a, b), pre2(a, b)))

    for i, a in enumerate(inputs):
        res = f(*a)
        if res != expected[i]:
            return False
    return True


def test_gates_10(pre1a, pre1b, pre2a, pre2b, com1, com2, post1, post2, com3,
                  post3, inputs, expected):
    def f(a, b):
        return post3(
                com3(
                    post1(com1(pre1a(a), pre1b(b))),
                    post2(com2(pre2a(a), pre2b(b)))))

    for i, a in enumerate(inputs):
        res = f(*a)
        if res != expected[i]:
            return False
    return True


def find_binary_gates(name, expected):
    print(f"Finding gates for {name}:")

    found = False
    for pre_a, pre_b, com, post in product(UNARY, UNARY, BINARY, UNARY):
        if test_gates_uubu(pre_a, pre_b, com, post, INPUTS, expected):
            print("  Match found for "
                  f"{post.__name__}({com.__name__}({pre_a.__name__}(a), "
                  f"{pre_b.__name__}(b)))")
            found = True
    if found:
        return

    for a, b, c, d in product(BINARY, BINARY, BINARY, UNARY):
        if test_gates_bbbu(a, b, c, d, INPUTS, expected):
            print("  Match found for "
                  f"{d.__name__}({c.__name__}({a.__name__}(a, b), "
                  f"{b.__name__}(a, b)))")
            found = True
    if found:
        return

    best = float('Infinity')
    for funcs in product(UNARY, UNARY, UNARY, UNARY, BINARY, BINARY, UNARY,
                         UNARY, BINARY, UNARY):
        if test_gates_10(*funcs, INPUTS, expected):
            found = True
            score = sum([COST[x.__name__] for x in funcs])
            if score <= best:
                print(f"  Match {score} found with "
                      f"{[x.__name__ for x in funcs]}")
                best = score
    if not found:
        print(f"No matches found for {name}")


def find_unary_gates(name, expected):
    print(f"Finding gates for {name}:")

    inputs = ((NEG, NEG), (ZERO, ZERO), (POS, POS))
    best = float('Infinity')
    for funcs in product(UNARY, UNARY, BINARY, UNARY):
        score = sum([COST[x.__name__] for x in funcs])
        if test_gates_uubu(*funcs, inputs, expected):
            if score <= best:
                print(f"  Match {score} found with "
                      f"{[x.__name__ for x in funcs]}")
                best = score

    for funcs in product(UNARY, UNARY, UNARY, UNARY, BINARY, BINARY, UNARY,
                         UNARY, BINARY, UNARY):
        if test_gates_10(*funcs, inputs, expected):
            found = True
            score = sum([COST[x.__name__] for x in funcs])
            if score <= best:
                print(f"  Match {score} found with "
                      f"{[x.__name__ for x in funcs]}")
                best = score
    if not found:
        print(f"No matches found for {name}")


if __name__ == '__main__':
    for name, expected in BINARY_TARGETS.items():
        find_binary_gates(name, expected)

    for name, expected in UNARY_TARGETS.items():
        find_unary_gates(name, expected)
