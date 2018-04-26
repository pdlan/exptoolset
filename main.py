import json
import sympy
from flask import Flask, request
import uncertainty
import unit
import instrument
from latex2sympy.process_latex import process_sympy

app = Flask(__name__, static_url_path='/static')

@app.route('/analyse_equations', methods=['POST'])
def analyse_equations_handler():
    equations_str = []
    try:
        equations_str = request.get_json(force=True)['equations']
    except:
        return json.dumps({'status':'badrequest'}), 400
    equations = []
    invalid_equations = []
    for i, eqs in enumerate(equations_str):
        try:
            eq = process_sympy(eqs)
            equations.append(eq)
        except:
            invalid_equations.append(i)
    if len(invalid_equations) > 0:
        res = {
            'status' : 'failparseequation',
            'invalid_equations' : invalid_equations
        }
        return json.dumps(res), 400
    invalid_equations, free_vars, intermediate_vars, _ = uncertainty.analyse_equations(equations)
    if invalid_equations:
        res = {
            'status' : 'invalidequation',
            'invalid_equations' : invalid_equations
        }
        return json.dumps(res), 400
    free_vars_name = [s.name for s in free_vars]
    intermediate_vars_name = [s.name for s in intermediate_vars]
    dimensions, constraints = unit.analyse_dimension(equations, free_vars, intermediate_vars)
    dimensions_name = {}
    for k in dimensions:
        dimensions_name[k.name] = dimensions[k]
    res = {
        'status' : 'ok',
        'free_variables' : free_vars_name,
        'intermediate_variables' : intermediate_vars_name,
        'dimensions' : dimensions_name,
        'dimension_constraints' : constraints
    }
    return json.dumps(res)

def get_instrument(instrument_str):
    if isinstance(instrument_str, str) and instrument_str in instrument.instruments:
        return instrument.instruments[instrument_str]
    try:
        parts = instrument_str[0].split('.')
        digits = 0
        if len(parts) > 1:
            digits = len(parts[1])
        return (sympy.S(instrument_str[0]), sympy.S(instrument_str[1]), 'CustomInstrument', digits)
    except:
        return None

@app.route('/measure_uncertainty', methods=['POST'])
def measure_uncertainty_handler():
    try:
        args = request.get_json(force=True)
        name = args['name']
        data = args['data']
        data = [sympy.S(i) for i in data]
        instrument_req = args['instrument']
        unit_str = args['unit']
        p = float(args['p'])
    except:
        return json.dumps({'status':'badrequest'}), 400
    unit_ = unit.parse_unit(unit_str)
    if unit_ == None:
        return json.dumps({'status':'invalidunit'}), 400
    measure_instrument = get_instrument(instrument_req)
    if measure_instrument == None:
        return json.dumps({'status':'invalidinstrument'}), 400
    try:
        _, _, latex = uncertainty.latex_mu_procedure(name, data, unit_, measure_instrument, p)
    except:
        return json.dumps({'status':'invalidnumber'}), 400
    return json.dumps({'status':'ok','latex':latex})

@app.route('/full_procedure', methods=['POST'])
def full_procedure_handler():
    try:
        args = request.get_json(force=True)
        equations_str = args['equations']
        units_str = args['units']
        measures_str = args['measures']
        values_str = args['values']
        uncertainties_str = args['uncertainties']
        check_unit = args['check_unit']
        p = float(args['p'])
    except:
        return json.dumps({'status':'badrequest'}), 400
    for k in units_str:
        units_str[k] = unit.parse_unit(units_str[k])
        if units_str[k] == None:
            return json.dumps({'status':'invalidunit', 'unit':k}), 400
    equations = []
    for eqs in equations_str:
        try:
            eq = process_sympy(eqs)
            equations.append(eq)
        except:
            return json.dumps({'status':'failedparseequation'}), 400
    invalid_equations, free_vars, intermediate_vars, symbols = uncertainty.analyse_equations(equations)
    if invalid_equations:
        return json.dumps({'status':'invalidequation'}), 400
    for k in symbols:
        if k not in units_str:
            return json.dumps({'status':'badrequest'}), 400
        if symbols[k] in free_vars and k not in measures_str and k not in values_str:
            return json.dumps({'status':'badrequest'}), 400
    units = {}
    measures = {}
    values = {}
    uncertainties = {}
    try:
        for k in units_str:
            units[symbols[k]] = units_str[k]
        for k in measures_str:
            data = [sympy.S(i) for i in measures_str[k][0]]
            measure_instrument = get_instrument(measures_str[k][1])
            if measure_instrument == None:
                return json.dumps({'status':'invalidinstrument', 'var':k}), 400
            measures[symbols[k]] = (data, measure_instrument)
        for k in values_str:
            values[symbols[k]] = sympy.S(values_str[k])
        for k in uncertainties_str:
            uncertainties[symbols[k]] = sympy.S(uncertainties_str[k])
        if check_unit == 'true':
            valid, symbol = uncertainty.check_unit(equations, units)
            if not valid:
                return json.dumps({'status':'inconsistentunit', 'lhs':symbol}), 400
        latex = uncertainty.full_procedure(equations, measures, values, uncertainties, units, p)
        return json.dumps({'status':'ok', 'latex':latex})
    except Exception as e:
        print(e)
        return json.dumps({'status':'badrequest'}), 400

@app.route('/')
def index_handler():
    return app.send_static_file('index.html')

@app.route('/uncertainty.html')
def uncertainty_html_handler():
    return app.send_static_file('uncertainty.html')

@app.route('/procedure.html')
def procedure_html_handler():
    return app.send_static_file('procedure.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, threaded=True)