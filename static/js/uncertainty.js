var api_url = '';
//var api_url = 'http://120.78.177.94:8000';
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
    'stopwatch' : ['s', 'ms', 'min']
};

function on_change_instrument() {
    var instrument = $('#instrument').val();
    if (instrument === 'custom') {
        $('#custom').show();
        $('#unit-group').hide();
    } else {
        $('#custom').hide();
        units = UnitsForInstrument[instrument];
        var html = '';
        for (var i = 0; i < units.length; ++i) {
            html += '<option value="' + units[i] + '">' + units[i] + '</option>';
        }
        $('#unit').html(html);
        $('#unit-group').show();
    }
}

function generate() {
    var name = $('#name').val();
    var instrument = $('#instrument').val();
    var data_str = $('#data').val();
    var unit = $('#unit').val();
    var p = $('#p').val();
    if (instrument === 'custom') {
        var C = $('#C').val();
        var deltab = $('#deltab').val();
        instrument = [deltab, C];
        unit = '';
    }
    var data = data_str.split(',');
    for (var i = 0; i < data.length; ++i) {
        data[i] = $.trim(data[i]);
    }
    var post_data = {
        'name' : name,
        'instrument' : instrument,
        'data' : data,
        'unit' : unit,
        'p' : p
    };
    $.ajax({
        url : api_url + '/measure_uncertainty',
        type : 'POST',
        data : JSON.stringify(post_data),
        dataType : 'json',
        success: function (data) {
            $('#result').html(data['latex']);
            MathJax.Hub.Queue(['Typeset', MathJax.Hub, 'result']);
            $('#error-info').hide();
        },
        error: function (xhr) {
            var data = JSON.parse(xhr.responseText);
            var status = data['status'];
            if (status === 'invalidunit') {
                $('#error-info').html('单位错误。');
            } else if (status === 'invalidinstrument') {
                $('#error-info').html('仪器错误。');
            } else if (status === 'invalidnumber' || status === 'badrequest') {
                $('#error-info').html('数据格式错误。');
            } else {
                $('#error-info').html('服务器无法连接。');
            }
            $('#error-info').show();
        }
    });
    return false;
}

$(document).ready(function () {
    on_change_instrument();
    $('#instrument').change(on_change_instrument);
    $('#form').submit(generate);
});