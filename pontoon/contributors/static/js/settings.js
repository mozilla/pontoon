$(function () {
    // Toggle user profile attribute
    $('#check-boxes .check-box').click(function () {
        var self = $(this);

        $.ajax({
            url: '/api/v1/user/' + $('#server').data('username') + '/',
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('body').data('csrf'),
                attribute: self.data('attribute'),
                value: !self.is('.enabled'),
            },
            success: function () {
                self.toggleClass('enabled');
                var is_enabled = self.is('.enabled');
                var status = is_enabled ? 'enabled' : 'disabled';

                Pontoon.endLoader(self.text() + ' ' + status + '.');
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

    // Save custom homepage
    $('#homepage .locale .menu li:not(".no-match")').click(function () {
        var custom_homepage = $(this).find('.language').data('code');

        $.ajax({
            url: '/save-custom-homepage/',
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('body').data('csrf'),
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

    // Save preferred source locale
    $('#preferred-locale .locale .menu li:not(".no-match")').click(function () {
        var preferred_source_locale = $(this).find('.language').data('code');

        $.ajax({
            url: '/save-preferred-source-locale/',
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('body').data('csrf'),
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
