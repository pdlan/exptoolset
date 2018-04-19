import sympy
import sympy.physics

length = sympy.symbols('length');
mass = sympy.symbols('mass')
time = sympy.symbols('time')
current = sympy.symbols('current')
temperature = sympy.symbols('temperature')
amount_of_substance = sympy.symbols('amount_of_substance')

basic_unit = {
    'm' : sympy.Rational(1, 1),
    'km' : sympy.Rational(1000, 1),
    'dm' : sympy.Rational(1, 10),
    'cm' : sympy.Rational(1, 100),
    'mm' : sympy.Rational(1, 1000),
    'um' : sympy.Rational(1, 1000000),
    'nm' : sympy.Rational(1, 1000000000),
    's' : sympy.Rational(1, 1),
    'min' : sympy.Rational(60, 1),
    'h' : sympy.Rational(3600, 1),
    'ms' : sympy.Rational(1, 1000),
    'us' : sympy.Rational(1, 1000000),
    'ns' : sympy.Rational(1, 1000000000),
    'kg' : sympy.Rational(1, 1),
    'g' : sympy.Rational(1, 1000),
    'mg' : sympy.Rational(1, 1000000),
    'ug' : sympy.Rational(1, 1000000000),
    'ng' : sympy.Rational(1, 1000000000000),
    'K' : sympy.Rational(1, 1),
    'A' : sympy.Rational(1, 1),
    'mA' : sympy.Rational(1, 1000),
    'uA' : sympy.Rational(1, 1000000),
    'mol' : sympy.Rational(1, 1),
    'mmol' : sympy.Rational(1, 1000),
    'umol' : sympy.Rational(1, 1000000)
}

class Unit:
    def __init__(self, L, M, T, I, S, N):
        self.L = L
        self.M = M
        self.T = T
        self.I = I
        self.S = S
        self.N = N
        strs = []
        strs_latex = []
        pairs = [(M[0], M[1]), (N[0], N[1]), (L[0], L[1]), (S[0], S[1]), (I[0], I[1]), (T[0], T[1])]
        pairs_posexp = []
        pairs_negexp = []
        for p in pairs:
            if p[1] >= 0:
                pairs_posexp.append(p)
            else:
                pairs_negexp.append(p)
        pairs_sorted = pairs_posexp + pairs_negexp
        for p in pairs_sorted:
            if p[1] != 0:
                strs.append('%s' % p[0])
                strs_latex.append('\\mathrm{%s}' % p[0])
                if p[1] != 1:
                    strs[-1] += '^%d' % p[1]
                    strs_latex[-1] += '^{%d}' % p[1]
        self.name = '·'.join(strs)
        self.latex = '\\cdot'.join(strs_latex)
        self.dim = length ** L[1]
        self.dim *= mass ** M[1]
        self.dim *= time ** T[1]
        self.dim *= current ** I[1]
        self.dim *= temperature ** S[1]
        self.dim *= amount_of_substance ** N[1]

    def convert_to_si(self, number):
        number *= basic_unit[self.L[0]] ** self.L[1]
        number *= basic_unit[self.M[0]] ** self.M[1]
        number *= basic_unit[self.T[0]] ** self.T[1]
        number *= basic_unit[self.I[0]] ** self.I[1]
        number *= basic_unit[self.S[0]] ** self.S[1]
        number *= basic_unit[self.N[0]] ** self.N[1]
        return number

    def convert_from_si(self, number):
        number /= basic_unit[self.L[0]] ** self.L[1]
        number /= basic_unit[self.M[0]] ** self.M[1]
        number /= basic_unit[self.T[0]] ** self.T[1]
        number /= basic_unit[self.I[0]] ** self.I[1]
        number /= basic_unit[self.S[0]] ** self.S[1]
        number /= basic_unit[self.N[0]] ** self.N[1]
        return number

    def standard_unit(self):
        return Unit(('m', self.L[1]), ('kg', self.M[1]), ('s', self.T[1]), ('K', self.S[1]), ('A', self.I[1]), ('mol', self.N[1]))

def parse_unit(unit_str):
    if unit_str == '':
        return Unit(('m', 0), ('kg', 0), ('s', 0), ('A', 0), ('K', 0), ('mol', 0))
    unit_str = unit_str.replace('N', 'kg*m*s^-2')
    unit_str = unit_str.replace('J', 'kg*m^2*s^-2')
    unit_str = unit_str.replace('V', 'kg*m^2*A^-1*s^-3')
    parts = unit_str.split('*')
    L = [None, 0]
    M = [None, 0]
    T = [None, 0]
    I = [None, 0]
    N = [None, 0]
    S = [None, 0]
    for p in parts:
        base_exp = p.split('^')
        if len(base_exp) == 1:
            base_exp.append(1)
        if base_exp[0] in ['m', 'km', 'cm', 'mm', 'um', 'nm']:
            if L[0] != None and base_exp[0] != L[0]:
                return None
            L[0] = base_exp[0]
            L[1] += int(base_exp[1])
        elif base_exp[0] in ['kg', 'g', 'mg', 'ug', 'ng']:
            if M[0] != None and base_exp[0] != M[0]:
                return None
            M[0] = base_exp[0]
            M[1] += int(base_exp[1])
        elif base_exp[0] in ['s', 'ms', 'us', 'ns', 'min', 'h']:
            if T[0] != None and base_exp[0] != T[0]:
                return None
            T[0] = base_exp[0]
            T[1] += int(base_exp[1])
        elif base_exp[0] in ['A', 'mA', 'uA']:
            if I[0] != None and base_exp[0] != I[0]:
                return None
            I[0] = base_exp[0]
            I[1] += int(base_exp[1])
        elif base_exp[0] in ['mol', 'mmol', 'umol']:
            if N[0] != None and base_exp[0] != N[0]:
                return None
            N[0] = base_exp[0]
            N[1] += int(base_exp[1])
        elif base_exp[0] in ['K']:
            if S[0] != None and base_exp[0] != S[0]:
                return None
            S[0] = base_exp[0]
            S[1] += int(base_exp[1])
        else:
            return None
    if L[0] == None:
        L[0] = 'm'
    if M[0] == None:
        M[0] = 'kg'
    if T[0] == None:
        T[0] = 's'
    if I[0] == None:
        I[0] = 'A'
    if N[0] == None:
        N[0] = 'mol'
    if S[0] == None:
        S[0] = 'K'
    return Unit(L, M, T, I, S, N)
