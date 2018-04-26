import sympy

wood_ruler1 = (sympy.S('0.0010'), 3, '木尺', 4)
wood_ruler2 = (sympy.S('0.0015'), 3, '木尺', 4)
metal_ruler1 = (sympy.S('0.00010'), 3, '钢板尺', 4)
metal_ruler2 = (sympy.S('0.00015'), 3, '钢板尺', 4)
metal_ruler3 = (sympy.S('0.00020'), 3, '钢板尺', 4)
metal_tape1 = (sympy.S('0.0008'), 3, '钢卷尺', 4)
metal_tape2 = (sympy.S('0.0012'), 3, '钢卷尺', 4)
caliper1 = (sympy.S('0.00002'), sympy.sqrt(3), '游标卡尺', 5)
caliper2 = (sympy.S('0.00005'), sympy.sqrt(3), '游标卡尺', 5)
micrometer = (sympy.S('0.000004'), 3, '螺旋测微器', 6)
physical_balance1 = (sympy.S('0.0008'), 3, '物理天平', 4)
physical_balance2 = (sympy.S('0.0006'), 3, '物理天平', 4)
physical_balance3 = (sympy.S('0.0004'), 3, '物理天平', 4)
analytical_balance1 = (sympy.S('0.0000013'), 3, '分析天平', 7)
analytical_balance2 = (sympy.S('0.0000010'), 3, '分析天平', 7)
analytical_balance3 = (sympy.S('0.0000007'), 3, '分析天平', 7)
thermometer1 = (sympy.S('1'), 3, '普通温度计', 0)
thermometer2 = (sympy.S('0.2'), 3, '精密温度计', 1)
stopwatch = (sympy.S('0.2'), 3, '电子秒表', 1)

instruments = {
    'wood_ruler1' : wood_ruler1,
    'wood_ruler2' : wood_ruler2,
    'metal_ruler1' : metal_ruler1,
    'metal_ruler2' : metal_ruler2,
    'metal_ruler3' : metal_ruler3,
    'metal_tape1' : metal_tape1,
    'metal_tape2' : metal_tape2,
    'caliper1' : caliper1,
    'caliper2' : caliper2,
    'micrometer' : micrometer,
    'physical_balance1' : physical_balance1,
    'physical_balance2' : physical_balance2,
    'physical_balance3' : physical_balance3,
    'analytical_balance1' : analytical_balance1,
    'analytical_balance2' : analytical_balance2,
    'analytical_balance3' : analytical_balance3,
    'thermometer1' : thermometer1,
    'thermometer2' : thermometer2,
    'stopwatch' : stopwatch
}