var equations;
var free_vars = [];
var intermediate_vars = [];
var form_variable_state = {};
var intermediate_var_units = {};
var free_var_id;
var intermediate_var_id; 

var UnitsForInstrument = {
    'wood_ruler1' : ['cm', 'm', 'mm'],
    'wood_ruler2' : ['cm', 'm', 'mm'],
    'wood_ruler3' : ['cm', 'm', 'mm'],
    'metal_ruler1' : ['cm', 'm', 'mm'],
    'metal_ruler2' : ['cm', 'm', 'mm'],
    'metal_ruler3' : ['cm', 'm', 'mm'],
    'metal_tape1' : ['cm', 'm', 'mm'],
    'metal_tape2' : ['cm', 'm', 'mm'],
    'caliper1' : ['mm', 'cm', 'm'],
    'caliper2' : ['mm', 'cm', 'm'],
    'micrometer' : ['mm', 'cm', 'm'],
    'physical_balance1' : ['g', 'mg', 'kg'],
    'physical_balance2' : ['g', 'mg', 'kg'],
    'physical_balance3' : ['g', 'mg', 'kg'],
    'analytical_balance1' : ['g', 'mg', 'kg'],
    'analytical_balance2' : ['g', 'mg', 'kg'],
    'analytical_balance3' : ['g', 'mg', 'kg'],
};

function on_change_instrument() {
    var instrument = $('#instrument').val();
    if (instrument === 'custom') {
        $('#measure-custom').show();
        $('#measure-unit-group').hide();
    } else {
        $('#measure-custom').hide();
        units = UnitsForInstrument[instrument];
        var html = '';
        for (var i = 0; i < units.length; ++i) {
            html += '<option value="' + units[i] + '">' + units[i] + '</option>';
        }
        $('#measure-unit').html(html);
        $('#measure-unit-group').show();
    }
    form_variable_state[free_var_id]['instrument'] = instrument;
    form_variable_state[free_var_id]['measure_unit'] = $('#measure-unit').val();
}

function on_change_type() {
    var type = $('#variable-type').val();
    if (type === 'measure') {
        $('#measure').show();
        $('#constant').hide();
        $('#uncertainty').hide();
        on_change_instrument();
        $('#instrument').change(on_change_instrument);
    } else if (type === 'constant' || type === 'know-uncertainty') {
        $('#constant').show();
        $('#measure').hide();
        if (type === 'know-uncertainty') {
            $('#uncertainty').show();
        } else {
            $('#uncertainty').hide();
        }
        if (free_vars[free_var_id] === 'e') {
            if ($('#value').val() === '') {
                $('#value').attr('placeholder', '留空为自然对数的底数');
            }
        } else if (free_vars[free_var_id] === '\\pi') {
            if ($('#value').val() === '') {
                $('#value').attr('placeholder', '留空为圆周率');
            }
        } else {
            $('#value').attr('placeholder', '');
        }
    }
    form_variable_state[free_var_id]['variable_type'] = type;
}

function on_click_freevar(e) {
    e.preventDefault();
    $('.free-var-item').removeClass('active');
    $('.intermediate-var-item').removeClass('active');
    $(this).addClass('active');
    free_var_id = $(this).attr('data-freevarid');
    $('#form-free-variable').show();
    $('#form-intermediate-variable').hide();
    $('#variable-type').change(on_change_type);
    $('#deltab').change(function () {form_variable_state[free_var_id]['deltab'] = $('#deltab').val();});
    $('#C').change(function () {form_variable_state[free_var_id]['C'] = $('#C').val();});
    $('#measure-unit').change(function () {form_variable_state[free_var_id]['measure-unit'] = $('#measure-unit').val();});
    $('#data').keyup(function () {form_variable_state[free_var_id]['data'] = $('#data').val();});
    $('#data').change(function () {form_variable_state[free_var_id]['data'] = $('#data').val();});
    $('#constant-unit').keyup(function () {form_variable_state[free_var_id]['constant_unit'] = $('#constant-unit').val();});
    $('#constant-unit').change(function () {form_variable_state[free_var_id]['constant_unit'] = $('#constant-unit').val();});
    $('#value').keyup(function () {form_variable_state[free_var_id]['value'] = $('#value').val();});
    $('#value').change(function () {form_variable_state[free_var_id]['value'] = $('#value').val();});
    $('#uncertainty-value').keyup(function () {form_variable_state[free_var_id]['uncertainty_value'] = $('#uncertainty-value').val();});
    $('#uncertainty-value').change(function () {form_variable_state[free_var_id]['uncertainty_value'] = $('#uncertainty-value').val();});
    var state = form_variable_state[free_var_id];
    $('#variable-type').val(state['variable_type']);
    $('#instrument').val(state['instrument']);
    $('#deltab').val(state['deltab']);
    $('#C').val(state['C']);
    $('#measure-unit').val(state['measure_unit']);
    $('#data').val(state['data']);
    $('#constant-unit').val(state['constant_unit']);
    $('#value').val(state['value']);
    on_change_type();
}

function on_click_intermediatevar(e) {
    e.preventDefault();
    $('.free-var-item').removeClass('active');
    $('.intermediate-var-item').removeClass('active');
    $(this).addClass('active');
    intermediate_var_id = $(this).attr('data-intermediatevarid');
    $('#form-intermediate-variable').show();
    $('#form-free-variable').hide();
    $('#intermediate-unit').keyup(function () {intermediate_var_units[intermediate_var_id] = $('#intermediate-unit').val();});
    $('#intermediate-unit').change(function () {intermediate_var_units[intermediate_var_id] = $('#intermediate-unit').val();});
    $('#intermediate-unit').val(intermediate_var_units[intermediate_var_id]);
}

function convert_varname(varname) {
    return varname.replace('alpha', 'α')
    .replace('\\beta', 'β')
    .replace('\\gamma', 'γ').replace('\\Gamma', 'Γ')
    .replace('\\delta', 'δ').replace('\\Delta', 'Δ')
    .replace('\\epsilon', 'ε').replace('\\varepsilon', 'ε')
    .replace('\\zeta', 'ζ')
    .replace('\\eta', 'η')
    .replace('\\theta', 'θ').replace('\\Theta', 'Θ').replace('\\vartheta', 'θ')
    .replace('\\iota', 'ι')
    .replace('\\kappa', 'κ').replace('\\varkappa', 'κ')
    .replace('\\lambda', 'λ').replace('\\Lambda', 'Λ')
    .replace('\\mu', 'μ')
    .replace('\\nu', 'ν')
    .replace('\\xi', 'ξ').replace('\\Xi', 'Ξ')
    .replace('\\pi', 'π').replace('\\Pi', 'Π')
    .replace('\\rho', 'ρ').replace('\\varrho', 'ρ')
    .replace('\\sigma', 'σ').replace('\\Sigma', 'Σ').replace('\\varsigma', 'σ')
    .replace('\\tau', 'τ')
    .replace('\\upsilon', 'υ')
    .replace('\\phi', 'φ').replace('\\Phi', 'Φ').replace('\\varphi', 'φ')
    .replace('\\chi', 'χ')
    .replace('\\psi', 'ψ').replace('\\Psi', 'Ψ')
    .replace('\\omega', 'ω').replace('\\Omega', 'Ω');
}

function generate() {
    var values = {};
    var measures = {};
    var uncertainties = {};
    var units = {};
    for (var i = 0; i < free_vars.length; ++i) {
        var name = free_vars[i];
        var state = form_variable_state[i];
        if (state['variable_type'] === 'measure') {
            var data = state['data'].split(',');
            for (var j = 0; j < data.length; ++j) {
                data[j] = $.trim(data[j]);
            }
            var instrument;
            if (state['instrument'] === 'custom') {
                units[name] = '';
                instrument = [state['deltab'], state['C']];
            } else {
                instrument = state['instrument'];
                units[name] = state['measure_unit'];
            }
            measures[name] = [data, instrument];
        } else {
            var value = state['value'];
            var unit = state['constant_unit'];
            if (value === '') {
                if (name === '\\pi') {
                    value = 'pi';
                    unit = '';
                } else if (name === 'e') {
                    value = 'E';
                    unit = '';
                }
            }
            values[name] = value;
            units[name] = unit;
            if (state['variable_type'] === 'know-uncertainty') {
                uncertainties[name] = state['uncertainty_value'];
            }
        }
    }
    for (var i = 0; i < intermediate_vars.length; ++i) {
        units[intermediate_vars[i]] = intermediate_var_units[i];
    }
    var p = $('#p').val();
    var check_unit = 'false';
    if ($('#check-unit').prop('checked')) {
        check_unit = 'true';
    }
    var post_data = {
        'equations' : equations,
        'units' : units,
        'measures' : measures,
        'values' : values,
        'uncertainties' : uncertainties,
        'p' : p,
        'check_unit' : check_unit
    };
    $.ajax({
        url : '/full_procedure',
        type : 'POST',
        data : JSON.stringify(post_data),
        dataType : 'json',
        success: function (data) {
            var latex = data['latex'];
            $('#result').html(latex);
            MathJax.Hub.Queue(['Typeset', MathJax.Hub, 'result']);
            $('#error-info-result').hide();
        },
        error: function (xhr) {
            var data = JSON.parse(xhr.responseText);
            var status = data['status'];
            var html = '';
            if (status === 'invalidunit') {
                data['unit'] = convert_varname(data['unit']);
                html = '以下变量单位错误：' + data['unit'];
            } else if (status === 'invalidinstrument') {
                data['var'] = convert_varname(data['var']);
                html = '以下变量测量仪器选择错误：：' + data['var'];
            } else if (status === 'inconsistentunit') {
                data['lhs'] = convert_varname(data['lhs']);
                html = '以下中间变量和方程右侧量纲不一致，请检查单位设置：：' + data['lhs'];
            } else {
                html = '出现错误，请检查各变量的设置';
            }
            $('#error-info-result').html(html);
            $('#error-info-result').show();
        }
    });
    return false;
}

function analyse_equations() {
    var equations_input = $('#equations-input').val().split('\n');
    equations = [];
    for (var i = 0; i < equations_input.length; ++i) {
        var eq = $.trim(equations_input[i]);
        if (eq != '') {
            equations.push(eq);
        }
    }
    var post_data = {
        'equations' : equations
    };
    $.ajax({
        url : '/analyse_equations',
        type : 'POST',
        data : JSON.stringify(post_data),
        dataType : 'json',
        success: function (data) {
            form_variable_state = {};
            intermediate_var_units = {};
            $('#error-info-equation').hide();
            var equations_latex = '';
            for (var i = 0; i < equations.length; ++i) {
                equations_latex += '$$' + equations[i] + '$$\n';
            }
            $('#equations-show').html(equations_latex);
            MathJax.Hub.Queue(['Typeset', MathJax.Hub, 'equations-show']);
            free_vars = data['free_variables'];
            intermediate_vars = data['intermediate_variables'];
            var free_vars_html = '';
            var intermediate_vars_html = '';
            for (var i = 0; i < free_vars.length; ++i) {
                free_vars_html += '<li class="nav-item"><a href="#" class="free-var-item nav-link" data-freevarid="'
                + i + '">' + convert_varname(free_vars[i]) + '</a></li>';
                form_variable_state[i] = {
                    'variable_type' : 'measure',
                    'instrument' : 'wood_ruler1',
                    'deltab' : '',
                    'C' : '3',
                    'measure_unit': '',
                    'data' : '',
                    'constant_unit' : '',
                    'value' : '',
                    'uncertainty_value' : ''
                };
                if (free_vars[i] === '\\pi' || free_vars[i] === 'e') {
                    form_variable_state[i]['variable_type'] = 'constant';
                }
            }
            for (var i = 0; i < intermediate_vars.length; ++i) {
                intermediate_vars_html += '<li class="nav-item"><a href="#" class="intermediate-var-item nav-link" data-intermediatevarid="'
                    + i + '">' + convert_varname(intermediate_vars[i]) + '<a></li>';
                intermediate_var_units[i] = '';
            }
            $('#free-variables').html(free_vars_html);
            $('#intermediate-variables').html(intermediate_vars_html);
            $('.free-var-item').click(on_click_freevar);
            $('.intermediate-var-item').click(on_click_intermediatevar);
            $('[data-freevarid="0"]').click();
            $('#variables').show();
            $('#form-final').show();
            $('#form-final').submit(generate);
            $('#error-info-equations').hide();
        },
        error: function (xhr) {
            var data = JSON.parse(xhr.responseText);
            var status = data['status'];
            if (status === 'failparseequation') {
                $('#error-info-equations').html('公式格式错误。');
            } else if (status === 'invalidequation') {
                $('#error-info-equations').html('公式顺序错误或公式左边变量不止一个。');
            } else {
                $('#error-info-equations').html('服务器无法连接。');
            }
            $('#error-info-equations').show();
        }
    });
    return false;
}

$(document).ready(function () {
    $('#form-equations').submit(analyse_equations);
});