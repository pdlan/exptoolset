import uncertainty
#import instrument
import unit
import sympy
import latex2sympy.process_latex

#equations = [latex2sympy.process_latex.process_sympy('V=\\frac{4}{3}\\pi r^3'), latex2sympy.process_latex.process_sympy('\\rou=\\frac{m}{V}')]
#exp = latex2sympy.process_latex.process_sympy('e^x')
#s = None
#for i in exp.free_symbols:
#    s = i
#print(exp.subs({s : 2}))
#print(equations)
#print(uncertainty.analyse_equations(equations))
#print(uncertainty.latex_cu_procedure('w', latex2sympy.process_latex.process_sympy('xy'), 'm', {'x' : 0.1, 'y' : 0.1}, {'x' : 1, 'y' : 1}, 0.95)[1])
#s = uncertainty.compose_uncertainty(latex2sympy.process_latex.process_sympy('\\sqrt{x}'), {'x' : sympy.symbols('u_x', positive=True), 'y' : sympy.symbols('u_y', positive=True)})
#print(s)
#mean, un, latex = uncertainty.latex_mu_procedure('m', [sympy.S(i) for i in ['52.953', '52.959', '52.961', '52.950', '52.955', '52.950', '52.949', '52.954', '52.955']], unit.Unit(('g', 1), ('m', 0), ('A', 0), ('s', 0)), instrument.analytical_balance3, 0.95)
#print(latex)

equations = ['V=\\frac{4}{3}\\pi r^3', '\\rou=\\frac{m}{V}', 'u=e^{\\rou}', 'v=\sin r']
equations = [latex2sympy.process_latex.process_sympy(i) for i in equations]
_, free_vars, intermediate_vars, symbols = uncertainty.analyse_equations(equations)
print(unit.analyse_dimension(equations, free_vars, intermediate_vars))