$(document).ready(function() {

    var QueryString = function() {
        // This function is anonymous, is executed immediately and
        // the return value is assigned to QueryString!
        var query_string = {};
        var query = window.location.search.substring(1);
        var vars = query.split("&");
        for (var i = 0; i < vars.length; i++) {
            var pair = vars[i].split("=");
            // If first entry with this name.
            if (typeof query_string[pair[0]] === "undefined") {
                query_string[pair[0]] = pair[1];
            // If second entry with this name
            } else if (typeof query_string[pair[0]] === "string") {
                var arr = [query_string[pair[0]], pair[1]];
                query_string[pair[0]] = arr;
            // If third or later entry with this name
            } else {
                query_string[pair[0]].push(pair[1]);
            }
        }
        return query_string;
    }();

    var getClassName = function(online) {
        var className = 'vminute_null';
        if (online == 1) {
            className = 'vminute_online';
        } else if (online == 0) {
            className = 'vminute_offline';
        }
        return className;
    };

    var drawMinutes = function() {

        var mpc = 120; // minutes per cycle
        var shift_angle = 300 / 120.0
        var base_radius = 200;
        var base_shift = -90 + (shift_angle + 10) / 2;
        var deg_indent = 0;

        // create all minutes
        for (var i = 0; i < 12; i++) {
            for (var j = 0; j < mpc; j++) {
                $('.vday').append('<div id="' + (i * mpc + j) + '" class="vminute"></div>');
            }
        }

        $('div.vminute').each(function(index) {
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

    drawMinutes();

    var pathname = window.location.pathname.split('/');
    var user_id = pathname[pathname.length - 1];

    if (typeof QueryString.date != 'undefined') {
        userURI = 'http://' + window.location.host
            + '/vk/activity/v1.0/users/' + user_id
            + '?date=' + QueryString.date;
    } else {
        userURI = 'http://' + window.location.host
            + '/vk/activity/v1.0/users/' + user_id;
    }

    var ajax = function(uri, method, data) {
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

    var render = function(minutes) {
        for (var minute in minutes) {
            $("#" + minute).attr('class', getClassName(minutes[minute]));
        }
    };

    var update = function() {
        ajax(userURI, 'GET').done(render)
    };

    update();

});
