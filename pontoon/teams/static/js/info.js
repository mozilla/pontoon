$(function () {
    var container = $('#main .container');

    function toggleWidgets() {
        container
            .find('.controls > *')
            .toggle()
            .end()
            .find('.read-only-info')
            .toggle()
            .end()
            .find('.read-write-info')
            .toggleClass('hidden');
    }

    container.on('click', '#info-wrapper .edit-info', function (e) {
        e.preventDefault();
        var content = container.find('.info').html();
        var textArea = container
            .find('.read-write-info textarea')
            .val($.trim(content));
        toggleWidgets();
        textArea.focus();
    });

    container.on('click', '#info-wrapper .cancel', function (e) {
        e.preventDefault();
        toggleWidgets();
    });

    container.on('click', '#info-wrapper .save', function (e) {
        e.preventDefault();
        var textArea = container.find('.read-write-info textarea');
        $.ajax({
            url: textArea.parent().data('url'),
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('body').data('csrf'),
                team_info: textArea.val(),
            },
            success: function (data) {
                container
                    .find('.info')
                    .html(data)
                    .toggle(data !== '');
                container.find('.no-results').toggle(data === '');
                toggleWidgets();
                Pontoon.endLoader('Team info saved.');
            },
            error: function (request) {
                Pontoon.endLoader(request.responseText, 'error');
            },
        });
    });
});
