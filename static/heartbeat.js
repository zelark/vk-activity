var send = function(method, uri, data) {
    var request = {
        url: uri,
        type: method,
        contentType: "application/json",
        accepts: "application/json",
        cache: false,
        dataType: 'json',
        data: JSON.stringify(data),
        error: function(jqXHR) {
            console.log("ajax error " + jqXHR.status);
        }
    };
    return $.ajax(request);
};

var drawMinutes = function() {

    var mpc = 120; // minutes per cycle
    var shift_angle = 300 / 120.0
    var base_radius = 200;
    var base_shift = -90 + (shift_angle + 10) / 2;
    var deg_indent = 0;

    // create all minutes
    $('.vday').empty();
    for (var i = 0; i < 12; i++) {
        for (var j = 0; j < mpc; j++) {
            $('.vday').append('<div id="' + (i * mpc + j) + '" class="vmin none"></div>');
        }
    }

    $('div.vmin').each(function(index) {
        if (index % 120 === 0) {
            deg_indent = 0;
        } else if (index % 60 == 0) {
            deg_indent += 10;
        }
        else if (index % 10 == 0) {
            deg_indent += 4
        }

        var degree = (index % mpc) * shift_angle + base_shift + deg_indent;
        var pillar = Math.floor(index / mpc);
        var radius = base_radius + pillar * 10 + pillar;
        if (pillar > 5) {
            radius += 4;
        }

        $(this).css({transform: 'rotate(' + degree + 'deg) translate(' + radius + 'px)'});
    });
};

var userURI = function() {
    return 'http://' + window.location.host
            + '/vk/activity/v1.0/users'
            + window.location.pathname
            + window.location.search;
}();

$(document).ready(function() {

    var render = function(minutes) {
        for (var minute in minutes) {
            $("#" + minute).attr('class', 'vmin');
            $("#" + minute).addClass(getClassName(minutes[minute]));
        }
    };

    var getClassName = function(online) {
        var className = 'none';
        if (online == 1) {
            className = 'on';
        }
        else if (online == 0) {
            className = 'off';
        }
        return className;
    };

    var update = function() {
        send('GET', userURI).done(render);
    };

    drawMinutes();
    update();
    setInterval(update, 60 * 1000);

});
