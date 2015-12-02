function parseInterval(value) {
    var result = new Date(1,1,1);
    result.setMilliseconds(value*1000);
    return result;
}

function getAvatar(user_id) {
    $.getJSON('/api/v1/user_image/'+user_id, function(img_url) {
        $('#avatar').html('<img src="'+ img_url +'" width=100 height=100/>');
    });
}
