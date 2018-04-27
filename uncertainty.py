import decimal
import math
import re
import sympy
import scipy.stats
import instrument
import unit

re_between_numbers = re.compile(r'<SUBSNUMBEREND[12]>\s*<SUBSNUMBERSTART[12]>')
re_number_bracket_frac = re.compile(r'<SUBSNUMBEREND[12]>\s*(\(|\[|\\{|\\frac)')
re_number_left_bracket_frac = re.compile(r'<SUBSNUMBEREND[12]>\s*\\left\s*(\(|\[|\\{|\\frac)')
re_sn_number_exponent = re.compile(r'<SUBSNUMBERSTART1>(.*?)<SUBSNUMBEREND1>\s*\^')
re_bracket_number = re.compile(r'(\)|\]|\})\s*<SUBSNUMBERSTART[12]>')

def measure_uncertainty(data, measure_instrument, p, unit):
    n = len(data)
    mean = 0
    for i in data:
        mean += i
    mean /= n
    stdev = 0
    for i in data:
        stdev += (i - mean) * (i - mean)
    stdev = sympy.sqrt(stdev / (n - 1))
    db = unit.convert_from_si(measure_instrument[0])
    C = measure_instrument[1]
    t = scipy.stats.t.interval(p, n - 1, 0, 1)[1]
    ua = t * stdev / sympy.sqrt(n)
    kp = scipy.stats.norm.interval(p, 0, 1)[1]
    ub = kp * db / C
    uncertainty = sympy.sqrt(ua * ua + ub * ub)
    return uncertainty, mean, stdev, t, db, kp, C

def round_after_point(number, digits):
    if digits < 0:
        s = '%d' % decimal.Decimal(str(sympy.N(number)))
        if len(s) > -digits:
            return s[:digits] + '0' * (-digits)
        else:
            return '0'
    fmt = '%%.%df' % digits
    return fmt % decimal.Decimal(str(sympy.N(number)))

def round_for_instrument(number, measure_instrument, unit, extra=0):
    digits = measure_instrument[3] + int(sympy.log(unit.convert_to_si(1), 10)) + extra
    return round_after_point(number, digits)

def latex_mu_procedure(name, data, unit, measure_instrument, p):
    uncertainty, mean, stdev, t, db, kp, C = measure_uncertainty(data, measure_instrument, p, unit)
    data = [round_for_instrument(i, measure_instrument, unit) for i in data]
    mean_str = round_for_instrument(mean, measure_instrument, unit)
    stdev_str = round_for_instrument(stdev, measure_instrument, unit, 1)
    res = '$$\\overline{%s}=\\frac{%s}{%d}%s=%s%s$$\n' % (name, '+'.join(data), len(data), unit.latex, mean_str, unit.latex)
    items = ['(%s-%s)^2' % (round_for_instrument(i, measure_instrument, unit), mean_str) for i in data]
    res += '$$\\sigma_{%s}=\\sqrt{\\frac{%s}{%d-1}}%s=%s%s$$\n' % (name, '+'.join(items), len(data), unit.latex, stdev_str, unit.latex)
    res += '$$U_{%s%s}=\\sqrt{\\left(t_{%s}\\frac{\\sigma_{%s}}{\\sqrt{n}}\\right)^2+\\left(k_p\\frac{\Delta_B}{C}\\right)^2}' % (remove_end_zero(p), name, remove_end_zero(p), name)
    if C == sympy.sqrt(3):
        C = '\\sqrt{3}'
    db = round_for_instrument(db, measure_instrument, unit)
    uncertainty_str = round_for_instrument(uncertainty, measure_instrument, unit, 1)
    res += '=\\sqrt{\\left(%.2f\\times\\frac{%s}{\\sqrt{%d}}\\right)^2+\\left(%.2f\\times\\frac{%s}{%s}\\right)^2}%s' % (t, stdev_str, len(data), kp, db, C, unit.latex)
    res += '=%s%s$$\n' % (uncertainty_str, unit.latex)
    return sympy.S(mean_str), sympy.S(uncertainty_str), res

def compose_uncertainty(expression, uncertainties):
    symbols = expression.free_symbols
    u_square = 0
    for s in symbols:
        name = s.name
        if name not in uncertainties:
            continue
        u = sympy.diff(expression, s)
        u_square += u * u * uncertainties[name] ** 2
    return sympy.sqrt(u_square)

def align_to_uncertainty(value, u, u_accuracy):
    if u == 0:
        return format(decimal.Decimal(str(sympy.N(value))), 'f')
    s_u = format(decimal.Decimal(str(sympy.N(u, u_accuracy))), 'f')
    point_pos = s_u.find('.')
    if point_pos == -1:
        value_integer = '%d' % decimal.Decimal(str(sympy.N(value)))
        zero_digits = 0
        for i in range(len(s_u)):
            if s_u[-(i + 1)] == '0':
                zero_digits += 1
            else:
                break
        return value_integer[0:len(value_integer) - zero_digits] + '0' * zero_digits
    digits = 0
    for i in range(point_pos + 1, len(s_u)):
        digits += 1
        if s_u[i] != '0':
            break
    digits += u_accuracy - 1
    return round_after_point(value, digits)

def eval_noexp(number, accuracy):
    return format(decimal.Decimal(str(sympy.N(number, accuracy))), 'f')

def remove_end_zero(number, noexp=False):
    s = ''
    if noexp:
        s = format(decimal.Decimal(str(sympy.N(number))), 'f')
    else:
        s = str(number)
        if s == 'pi' or s == 'E':
            s = str(sympy.N(s, 5))
    if s.find('.') == -1:
        return s
    parts = s.split('e')
    res = parts[0]
    while res[-1] == '0' and len(res) > 1:
        res = res[:-1]
    if res[-1] == '.':
        res = res[:-1]
    if len(parts) > 1:
        if parts[1][0] == '+':
            parts[1] = parts[1][1:]
        res += '\\times10^{%s}' % parts[1]
    return res

def sub_number(expression, variables):
    exp_subs = expression
    for k in variables:
        number = remove_end_zero(variables[k])
        if number.find('\\times') != -1:
            exp_subs = exp_subs.subs(k, sympy.symbols('<SUBSNUMBERSTART1>' + number + '<SUBSNUMBEREND1>'))
        else:
            exp_subs = exp_subs.subs(k, sympy.symbols('<SUBSNUMBERSTART2>' + number + '<SUBSNUMBEREND2>'))
    exp_subs = sympy.latex(exp_subs)
    exp_subs = re_between_numbers.sub(r'\\times', exp_subs)
    exp_subs = re_sn_number_exponent.sub(r'(<SUBSNUMBERSTART1>\1<SUBSNUMBEREND1>)^', exp_subs)
    exp_subs = re_number_bracket_frac.sub(r'\\times\1', exp_subs)
    exp_subs = re_number_left_bracket_frac.sub(r'\\times\\left\1', exp_subs)
    exp_subs = re_bracket_number.sub(r'\1\\times', exp_subs)
    exp_subs = exp_subs.replace('<SUBSNUMBERSTART1>', '').replace('<SUBSNUMBEREND1>', '')
    exp_subs = exp_subs.replace('<SUBSNUMBERSTART2>', '').replace('<SUBSNUMBEREND2>', '')
    exp_subs = exp_subs.replace('\\cdot', '\\times')
    return exp_subs

def latex_cu_procedure(name, expression, unit, uncertainties, values, p, u_accuracy=3, is_result=False):
    standard_unit = unit.standard_unit()
    symbols = expression.free_symbols
    u_symbols = {}
    pd_squares = []
    u_vars = {}
    for s in symbols:
        if s.name not in values:
            return None
        u_vars[s] = values[s.name]
        if s.name not in uncertainties:
            continue
        u_name = 'U_{%s%s}' % (remove_end_zero(p), s.name)
        pd_squares.append('\\left(\\frac{\\mathrm{\\partial}%s}{\\mathrm{\\partial}%s}%s\\right)^2' % (name, s.name, u_name))
        u_symbol = sympy.symbols(u_name, positive=True)
        u_symbols[s.name] = u_symbol
        u_vars[u_symbol] = uncertainties[s.name]
    u_exp = compose_uncertainty(expression, u_symbols)
    u_val = unit.convert_from_si(u_exp.subs(u_vars))
    exp_value = unit.convert_from_si(expression.subs(u_vars))
    exp_latex = sympy.latex(expression)
    u_exp_latex = sympy.latex(u_exp)
    u_exp_subs_latex = sub_number(u_exp, u_vars)
    exp_subs_latex = sub_number(expression, u_vars)
    exp_value_str = ''
    is_exp_sn = False;
    if is_result:
        is_startswith12 = False
        for c in eval_noexp(u_val, 1):
            if c != '0' and c != '.':
                if c == '1' or c == '2':
                    is_startswith12 = True
                break
        if not is_startswith12:
            u_accuracy = 1
    exp_value_aligned = align_to_uncertainty(exp_value, u_val, u_accuracy)
    ev_aligned_s = str(sympy.N(sympy.S(exp_value_aligned)))
    if 'e' in ev_aligned_s:
        is_exp_sn = True
        ev_aligned_parts = ev_aligned_s.split('e')
        if ev_aligned_parts[1][0] == '+':
            ev_aligned_parts[1] = ev_aligned_parts[1][1:]
        ev_aligned_parts[0] = remove_end_zero(sympy.S(ev_aligned_parts[0]))
        exp_value_str = ev_aligned_parts[0] + '\\times10^{%s}' % ev_aligned_parts[1]
    else:
        exp_value_str = exp_value_aligned
    res = '$$%s=%s=%s%s=%s%s$$\n' % (name, exp_latex, exp_subs_latex, standard_unit.latex, exp_value_str, unit.latex)
    if len(uncertainties) == 0:
        return exp_value, sympy.S('0'), res
    res += '$$\n\\begin{align}\n'
    res += 'U_{%s%s} & = \\sqrt{%s} \\\\\n& =' % (remove_end_zero(p), name, '+'.join(pd_squares))
    res += u_exp_latex + ' \\\\\n&=' + u_exp_subs_latex + standard_unit.latex
    u_val_parts = str(sympy.N(u_val, u_accuracy)).split('e')
    u_val_str = u_val_parts[0]
    if u_val_str[-1] == '.':
        u_val_str = u_val_str[:-1]
    if len(u_val_parts) > 1:
        if u_val_parts[1][0] == '+':
            u_val_parts[1] = u_val_parts[1][1:]
        u_val_str += '\\times 10^{%s}' % u_val_parts[1]
    res += ' \\\\\n& = %s%s, \\quad P=%s\n\\end{align}\n$$\n' % (u_val_str, unit.latex, remove_end_zero(p))
    if is_result:
        if is_exp_sn:
            n = ev_aligned_parts[0]
            exp = int(ev_aligned_parts[1])
            u_val_str = eval_noexp(u_val / (10 ** exp), u_accuracy)
            res += '$$\\mathrm{Result:}\\;%s=%s\\pm%s\\times10^{%d}%s' % (name, n, u_val_str, exp, unit.latex)
        else:
            u_val_str = eval_noexp(u_val, u_accuracy)
            res += '$$\\mathrm{Result:}\\;%s=%s\\pm%s%s' % (name, exp_value_str, u_val_str, unit.latex)
        res += ', \\quad P=%s$$' % remove_end_zero(p)
    return sympy.S(align_to_uncertainty(exp_value, u_val, u_accuracy)), sympy.S(sympy.N(u_val, u_accuracy)), res

def analyse_equations(equations):
    free_vars = []
    intermediate_vars = []
    invalid_equations = []
    symbols = {}
    for i, eq in enumerate(equations):
        if not isinstance(eq, sympy.Eq):
            invalid_equations.append(i)
            continue
        if len(eq.lhs.free_symbols) != 1:
            invalid_equations.append(i)
    if len(invalid_equations) > 0:
        return invalid_equations, None, None, None
    for i, eq in enumerate(equations):
        lhs = None
        for i in eq.lhs.free_symbols:
            lhs = i
        if lhs in free_vars:
            invalid_equations.append(i)
            return invalid_equations, None, None, None
        intermediate_vars.append(lhs)
        for symbol in eq.rhs.free_symbols:
            if not symbol in intermediate_vars and symbol not in free_vars:
                free_vars.append(symbol)
    for s in intermediate_vars:
        symbols[s.name] = s
    for s in free_vars:
        symbols[s.name] = s
    return None, free_vars, intermediate_vars, symbols

def check_unit(equations, units):
    dims = {}
    for k in units:
        dims[k] = units[k].dim
    for i, eq in enumerate(equations):
        lhs = list(eq.lhs.free_symbols)[0]
        r = eq.rhs.subs(dims) / dims[lhs]
        if not r.is_constant():
            return False, i
    return True, None

def round(number, accuracy):
    s = format(decimal.Decimal(str(sympy.N(number, accuracy))), 'f')
    return sympy.S(s)

def symbol_dict_to_name_dict(symbol_dict):
    name_dict = {}
    for k in symbol_dict:
        name_dict[k.name] = symbol_dict[k]
    return name_dict

def subs_math_constants(equations, values):
    constants = {
        'e' : ('E', sympy.E),
        '\\pi' : ('pi', sympy.pi)
    }
    equations_subs = equations[:]
    for i in range(len(equations)):
        for k in values:
            if k.name not in constants:
                continue
            if values[k] != constants[k.name][0]:
                continue
            equations_subs[i] = equations_subs[i].subs({k : constants[k.name][1]})
    return equations_subs

def full_procedure(equations_, measures, values, uncertainties, units, p):
    equations = subs_math_constants(equations_, uncertainties)
    full_values = values
    latex = ''
    intermediate_vars_values = {}
    values_si = {}
    uncertainties_si = {}
    for k in full_values:
        values_si[k.name] = units[k].convert_to_si(full_values[k])
    for k in uncertainties:
        uncertainties_si[k.name] = units[k].convert_to_si(uncertainties[k])
    for i, eq in enumerate(equations):
        lhs = list(eq.lhs.free_symbols)[0]
        for s in eq.rhs.free_symbols:
            if s in full_values:
                continue
            elif s in measures:
                v, u, pr = latex_mu_procedure(s.name, measures[s][0], units[s], measures[s][1], p)
                latex += pr
                full_values[s] = v
                uncertainties[s] = u
                values_si[s.name] = units[s].convert_to_si(v)
                uncertainties_si[s.name] = units[s].convert_to_si(u)
        is_result = i == len(equations) - 1
        u_accuracy = 3
        if is_result:
            u_accuracy = 2
        v, u, pr = latex_cu_procedure(lhs.name, eq.rhs, units[lhs], uncertainties_si, values_si, p, u_accuracy, is_result)
        latex += pr
        full_values[lhs] = v
        uncertainties[lhs] = u
        values_si[lhs.name] = units[lhs].convert_to_si(v)
        uncertainties_si[lhs.name] = units[lhs].convert_to_si(u)
    return latex