$(function () {
    var container = $('#main .container');

    function isValidForm($form, locales, message) {
        $form.find('.errors p').css('visibility', 'hidden');

        if (!locales) {
            $form
                .find('.locale-selector .errors p')
                .css('visibility', 'visible');
        }

        if (!message) {
            $form
                .find('.message-wrapper .errors p')
                .css('visibility', 'visible');
        }

        return locales && message;
    }

    // Send notification
    container.on('click', '#send-notification .send', function (e) {
        e.preventDefault();
        var $form = $('#send-notification');

        // Validate form
        var locales = $form.find('[name=selected_locales]').val(),
            message = $form.find('[name=message]').val();

        if (!isValidForm($form, locales, message)) {
            return;
        }

        // Submit form
        $.ajax({
            url: $form.prop('action'),
            type: $form.prop('method'),
            data: $form.serialize(),
            success: function (data) {
                if (data.selected_locales || data.message) {
                    isValidForm($form, !data.selected_locales, !data.message);
                    return false;
                }

                Pontoon.endLoader('Notification sent.');
                container.empty().append(data);
            },
            error: function () {
                Pontoon.endLoader('Oops, something went wrong.', 'error');
            },
        });
    });

    // Recipient shortcuts
    container.on('click', '.locale-selector .shortcuts a', function (e) {
        e.preventDefault();

        var locales = $(this).data('ids').reverse(),
            $localeSelector = $(this).parents('.locale-selector');

        $localeSelector.find('.selected .move-all').click();

        $(locales).each(function (i, id) {
            $localeSelector
                .find('.locale.select:first')
                .find('[data-id=' + id + ']')
                .click();
        });
    });
});
