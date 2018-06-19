[![Build Status](https://travis-ci.org/direvus/btern.png?branch=master)](https://travis-ci.org/direvus/btern)
[![codecov](https://codecov.io/gh/direvus/btern/branch/master/graph/badge.svg)](https://codecov.io/gh/direvus/btern)


Balanced Ternary
================

This library implements computations over values expressed in Balanced Ternary
form.

Balanced Ternary is a numeral system with three symbols, equating to the
decimal values -1, 0 and +1.  We use the characters -, 0 and + to represents these
values respectively.  Each digit in ternary is called a 'trit' (**tr**inary
dig**it**).

When performing logical operations with balanced ternary values, we use the
Kleene ternary propositional logic system, where - represents False, +
represents True, and 0 represents an indeterminate value, which is either True
or False.

Modules
-------

  * **trit** provides basic operations on individual trits (Trit) and sequences
    of trits (Trits).  All of the other modules in the package are built on
    this foundation.
  * **integer** provides for operations which interpret sequences of trits as
    integer values.  The natural numeric interpretation for balanced ternary
    values is a signed integer (Int), and the module also provides an unsigned
    interpretation (UInt).
  * **character** provides for interpreting sequences of trits as character
    strings, including a simple Unicode Transformation Format (UTF6t).
  * **binary** provides a fairly compact binary encoding for sequences of
    trits.
  * **processor** provides for simulating a balanced ternary computer.  It
    includes a class for fixed-width sequences of trits (Register), a class for
    a machine code instruction (Instruction), an abstract class for building
    computer simulators (Processor), and a simple working implementation of a
    Processor (T3).

Background
----------

This library was written by Brendan Jurd, for purely educational and
entertainment purposes.  It has no intended practical value, but was basically
a speculative problem-solving exercise.

License
-------

This library is released under the BSD 2-clause license, a copy of which can be
found at the root of the source repository.
