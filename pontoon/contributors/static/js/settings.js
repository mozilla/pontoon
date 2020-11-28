$(function () {
    $('#homepage .locale .menu li:not(".no-match")').click(function () {
        var custom_homepage = $(this).find('.language').data('code');

        $.ajax({
            url: '/save-custom-homepage/',
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('#server').data('csrf'),
                custom_homepage: custom_homepage,
            },
            success: function (data) {
                if (data === 'ok') {
                    Pontoon.endLoader('Custom homepage saved.');
                }
            },
            error: function (request) {
                if (request.responseText === 'error') {
                    Pontoon.endLoader('Oops, something went wrong.', 'error');
                } else {
                    Pontoon.endLoader(request.responseText, 'error');
                }
            },
        });
    });
});

$(function () {
    $('#preferred-locale .locale .menu li:not(".no-match")').click(function () {
        var preferred_source_locale = $(this).find('.language').data('code');

        $.ajax({
            url: '/save-preferred-source-locale/',
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('#server').data('csrf'),
                preferred_source_locale: preferred_source_locale,
            },
            success: function (data) {
                if (data === 'ok') {
                    Pontoon.endLoader('Preferred source locale saved.');
                }
            },
            error: function (request) {
                if (request.responseText === 'error') {
                    Pontoon.endLoader('Oops, something went wrong.', 'error');
                } else {
                    Pontoon.endLoader(request.responseText, 'error');
                }
            },
        });
    });
});
