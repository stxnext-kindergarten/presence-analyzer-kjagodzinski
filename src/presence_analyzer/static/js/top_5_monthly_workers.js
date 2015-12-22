google.load('visualization', '1', {packages:['corechart', 'timeline'], 'language': 'pl'});

(function($) {
    $(document).ready(function() {
        var loading = $('#loading');
        $.getJSON('/api/v1/months', function(result) {
            var dropdown = $('#month');
            $.each(result, function(item) {
                dropdown.append($('<option />').val(this.name).text(this.name));
            });
            dropdown.show();
            loading.hide();
        });
        $('#month').change(function() {
            var selected_month = $('#month').val(),
                chart_div = $('#chart_div'),
                no_data = $('#no_data').html('<b>Data not found</b>');
            no_data.hide();
            if (selected_month) {
                loading.show();
                chart_div.hide();
                $('#avatar').empty()
                $.getJSON('/api/v1/top5monthly/'+selected_month, function(result) {
                    var finalresult = [];
                    $.each(result, function(index, value) {
                        $('#avatar').append('<img src="'+ value['avatar'] +'" />');
                        $('#avatar').show();
                        finalresult.push([
                            value['name'],
                            /**
                             *  parseInterval(32400) setting the time to 9:00am
                             *  as a default time of starting work
                             */
                            parseInterval(32400),
                            parseInterval(value['mean']+32400)
                        ]);
                    });
                    var data = new google.visualization.DataTable();
                    data.addColumn({type: 'string', id:'User'});
                    data.addColumn({type: 'datetime', id: 'Start'});
                    data.addColumn({type: 'datetime', id: 'End'});
                    data.addRows(finalresult);
                    var formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'});
                    formatter.format(data, 1);
                    chart_div.show();
                    loading.hide();
                    var chart = new google.visualization.Timeline(chart_div[0]);
                    chart.draw(data);
                }).fail(function() {
                   loading.hide();
                   no_data.show();
                });
            }
        });
    });
})(jQuery);
