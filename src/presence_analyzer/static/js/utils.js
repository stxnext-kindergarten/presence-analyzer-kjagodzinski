function parseInterval(value) {
    var result = new Date(1,1,1);
    result.setMilliseconds(value*1000);
    return result;
}

function getAvatar(user_id) {
    $('#avatar').empty();
    $.getJSON('/api/v1/user_image/'+user_id, function(img_url) {
        $('#avatar').append('<img src="'+ img_url +'" />');
        $('#avatar').show();
    });
}
