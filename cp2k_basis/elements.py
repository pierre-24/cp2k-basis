from typing import List, Iterable, Union
from marshmallow import fields, ValidationError


Z_TO_SYMB = {
    1: 'H',
    2: 'He',
    3: 'Li',
    4: 'Be',
    5: 'B',
    6: 'C',
    7: 'N',
    8: 'O',
    9: 'F',
    10: 'Ne',
    11: 'Na',
    12: 'Mg',
    13: 'Al',
    14: 'Si',
    15: 'P',
    16: 'S',
    17: 'Cl',
    18: 'Ar',
    19: 'K',
    20: 'Ca',
    21: 'Sc',
    22: 'Ti',
    23: 'V',
    24: 'Cr',
    25: 'Mn',
    26: 'Fe',
    27: 'Co',
    28: 'Ni',
    29: 'Cu',
    30: 'Zn',
    31: 'Ga',
    32: 'Ge',
    33: 'As',
    34: 'Se',
    35: 'Br',
    36: 'Kr',
    37: 'Rb',
    38: 'Sr',
    39: 'Y',
    40: 'Zr',
    41: 'Nb',
    42: 'Mo',
    43: 'Tc',
    44: 'Ru',
    45: 'Rh',
    46: 'Pd',
    47: 'Ag',
    48: 'Cd',
    49: 'In',
    50: 'Sn',
    51: 'Sb',
    52: 'Te',
    53: 'I',
    54: 'Xe',
    55: 'Cs',
    56: 'Ba',
    57: 'La',
    58: 'Ce',
    59: 'Pr',
    60: 'Nd',
    61: 'Pm',
    62: 'Sm',
    63: 'Eu',
    64: 'Gd',
    65: 'Tb',
    66: 'Dy',
    67: 'Ho',
    68: 'Er',
    69: 'Tm',
    70: 'Yb',
    71: 'Lu',
    72: 'Hf',
    73: 'Ta',
    74: 'W',
    75: 'Re',
    76: 'Os',
    77: 'Ir',
    78: 'Pt',
    79: 'Au',
    80: 'Hg',
    81: 'Tl',
    82: 'Pb',
    83: 'Bi',
    84: 'Po',
    85: 'At',
    86: 'Rn',
    87: 'Fr',
    88: 'Ra',
    89: 'Ac',
    90: 'Th',
    91: 'Pa',
    92: 'U',
    93: 'Np',
    94: 'Pu',
    95: 'Am',
    96: 'Cm',
    97: 'Bk',
    98: 'Cf',
    99: 'Es',
    100: 'Fm',
    101: 'Md',
    102: 'No',
    103: 'Lr'
}

SYMB_TO_Z = dict((b, a) for a, b in Z_TO_SYMB.items())

TPL = """Available for {0}:

{1:2}                                                 {2:2}
{3:2} {4:2}                               {5:2} {6:2} {7:2} {8:2} {9:2} {10:2}
{11:2} {12:2}                               {13:2} {14:2} {15:2} {16:2} {17:2} {18:2}
{19:2} {20:2} {21:2} {22:2} {23:2} {24:2} {25:2} {26:2} {27:2} {28:2} {29:2} {30:2} {31:2} {32:2} {33:2} {34:2} {35:2} {36:2} 
{37:2} {38:2} {39:2} {40:2} {41:2} {42:2} {43:2} {44:2} {45:2} {46:2} {47:2} {48:2} {49:2} {50:2} {51:2} {52:2} {53:2} {54:2} 
{55:2} {56:2} *  {72:2} {73:2} {74:2} {75:2} {76:2} {77:2} {78:2} {79:2} {80:2} {81:2} {82:2} {83:2} {84:2} {85:2} {86:2} 
{87:2} {88:2} **

  *  {57:2} {58:2} {59:2} {60:2} {61:2} {62:2} {63:2} {64:2} {65:2} {66:2} {67:2} {68:2} {69:2} {70:2} {71:2}
  ** {89:2} {90:2} {91:2} {92:2}"""  # noqa


def print_availability(name, atoms: List[str], not_avail: str = '..'):
    """Print atom that are in `atom` in their corresponding place in the periodic table, or `..`"""
    print(TPL.format(name, *[
        not_avail if Z_TO_SYMB[i] not in atoms else Z_TO_SYMB[i] for i in range(1, 93)
    ]))


class ElementSet:
    def __init__(self, elements: Iterable[int] = None):
        self.elements: frozenset = frozenset(elements) if elements else {}

    def _elementset_or_raise(self, o):
        if type(o) is ElementSet:
            return o
        elif type(o) is str:
            return ElementSet.create(o)
        else:
            raise TypeError('must be ElementSet')

    def __eq__(self, other: Union['ElementSet', str]) -> bool:
        other = self._elementset_or_raise(other)
        return self.elements == other.elements

    def __or__(self, other: Union['ElementSet', str]) -> 'ElementSet':
        other = self._elementset_or_raise(other)
        return ElementSet(self.elements | other.elements)

    def __and__(self, other: Union['ElementSet', str]) -> 'ElementSet':
        other = self._elementset_or_raise(other)
        return ElementSet(self.elements & other.elements)

    def __sub__(self, other: Union['ElementSet', str]) -> 'ElementSet':
        other = self._elementset_or_raise(other)
        return ElementSet(self.elements - other.elements)

    def __contains__(self, item: str):
        return ElementSet._Z(item) in self.elements

    def __le__(self, other: Union['ElementSet', str]):
        other = self._elementset_or_raise(other)
        return self.elements.issubset(other.elements)

    def __iter__(self) -> Iterable[str]:

        # NOTE: order not guaranteed
        for i in self.elements:
            yield Z_TO_SYMB[i]

    def iter_sorted(self) -> Iterable[str]:
        for i in sorted(self.elements):
            yield Z_TO_SYMB[i]

    def __repr__(self):
        return '<ElementSet({})>'.format(', '.join(Z_TO_SYMB[i] for i in self.elements))

    def __str__(self):
        return ','.join(Z_TO_SYMB[i] for i in self.elements)

    @staticmethod
    def _Z(w: str) -> int:
        try:
            Z = int(w)
        except ValueError:
            try:
                Z = SYMB_TO_Z[w]
            except KeyError:
                raise ValueError('`{}` is not a valid element'.format(w))

        if 1 <= Z <= 103:
            return Z
        else:
            raise ValueError('`{}` is not a valid Z value'.format(w))

    @classmethod
    def create(cls, inp: str):
        """Create an element set
        """
        elements = inp.split(',')
        resulting_set = set()

        for elmt in elements:
            if '-' in elmt:  # it is a range
                rng = elmt.split('-')
                if len(rng) != 2:
                    raise ValueError('range `{}` should be two elements')
                start, end = ElementSet._Z(rng[0]), ElementSet._Z(rng[1])
                if start > end:
                    start, end = end, start

                resulting_set |= set(range(start, end + 1))
            else:
                resulting_set.add(ElementSet._Z(elmt))

        return cls(resulting_set)


class ElementSetField(fields.Field):
    def _serialize(self, value: Union[ElementSet, None], *args, **kwargs):
        if value is None:
            return ''
        else:
            return str(value)

    def _deserialize(self, value: Union[str, None], *args, **kwargs):
        try:
            return ElementSet.create(value)
        except ValueError as e:
            raise ValidationError(str(e))


L_TO_SHELL = {
    0: 's',
    1: 'p',
    2: 'd',
    3: 'f',
    4: 'g',
    5: 'h'
}
