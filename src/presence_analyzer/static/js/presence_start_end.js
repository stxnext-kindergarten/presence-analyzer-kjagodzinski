google.load('visualization', '1', {packages:['corechart', 'timeline'], 'language': 'pl'});

(function($) {
    $(document).ready(function() {
        var loading = $('#loading');
        $.getJSON('/api/v1/users', function(result) {
            var dropdown = $('#user_id');
            $.each(result, function(item) {
                dropdown.append($('<option />').val(this.user_id).text(this.name));
            });
            dropdown.show();
            loading.hide();
        });
        $('#user_id').change(function() {
            var selected_user = $('#user_id').val(),
                chart_div = $('#chart_div'),
                no_data = $('#no_data').html('<b>Data not found</b>');
            no_data.hide();
            if (selected_user) {
                loading.show();
                chart_div.hide();
                getAvatar(selected_user);
                $.getJSON('/api/v1/presence_start_end/'+selected_user, function(result) {
                    var finalresult = [];
                    $.each(result, function(index, value) {
                        finalresult.push([
                            value[0],
                            parseInterval(value[1]['start']),
                            parseInterval(value[1]['end'])
                        ]);
                    });
                    var data = new google.visualization.DataTable();
                    data.addColumn('string', 'Weekday');
                    data.addColumn({type: 'datetime', id: 'Start'});
                    data.addColumn({type: 'datetime', id: 'End'});
                    data.addRows(finalresult);
                    var options = {
                        hAxis: {title: 'Weekday'}
                    },
                        formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'});
                    formatter.format(data, 1);
                    formatter.format(data, 2);
                    chart_div.show();
                    loading.hide();
                    var chart = new google.visualization.Timeline(chart_div[0]);
                    chart.draw(data, options);
                }).fail(function() {
                   loading.hide();
                   no_data.show();
                });
            }
        });
    });
})(jQuery);
