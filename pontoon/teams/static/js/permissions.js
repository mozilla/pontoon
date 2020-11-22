$(function () {
    var container = $('#main .container');

    function inputHidden(name, value, cssClass) {
        return $(
            '<input class="' +
                (cssClass || '') +
                '" type="hidden" name="' +
                name +
                '" value="' +
                value +
                '">',
        );
    }

    container.on('click', '#permissions-form .save', function (e) {
        e.preventDefault();
        var $form = $('#permissions-form');

        // Remove stale permissions items (bug 1416890)
        $('input.permissions-form-item').remove();

        // Before submitting the form, update translators and managers
        $.each(['translators', 'managers'], function (i, value) {
            var data = $form.find('.user.' + value + ' li');
            data.each(function () {
                var itemId = $(this).data('id');

                if ($(this).parents('.general').length > 0) {
                    $form.append(
                        inputHidden(
                            'general-' + value,
                            itemId,
                            'permissions-form-item',
                        ),
                    );
                } else {
                    // We have to retrieve an index of parent project locale form
                    var localeProjectIndex = $(this)
                        .parents('.project-locale')
                        .data('index');
                    $form.append(
                        inputHidden(
                            'project-locale-' +
                                localeProjectIndex +
                                '-translators',
                            itemId,
                            'permissions-form-item',
                        ),
                    );
                }
            });
        });

        $.ajax({
            url: $('#permissions-form').prop('action'),
            type: $('#permissions-form').prop('method'),
            data: $('#permissions-form').serialize(),
            success: function () {
                Pontoon.endLoader('Permissions saved.');
            },
            error: function () {
                Pontoon.endLoader('Oops, something went wrong.', 'error');
            },
        });
    });

    // Switch available users
    container.on('click', '.user.available label a', function (e) {
        e.preventDefault();

        $(this).addClass('active').siblings('a').removeClass('active');

        var available = $(this).parents('.user.available');
        available.find('li').show();

        if ($(this).is('.contributors')) {
            available.find('li:not(".contributor")').hide();
        }

        available.find('.search-wrapper input').trigger('input').focus();
    });

    // While in contributors tab, search contributors only
    // Has to be attached to body, like the input.search event in main.js
    $('body').on(
        'input.search',
        '.user.available .menu input[type=search]',
        function () {
            var available = $(this).parents('.user.available');

            if (available.find('label a.contributors').is('.active')) {
                available.find('li:not(".contributor")').hide();
            }
        },
    );

    // Focus project selector search field
    container.on('click', '#project-selector .selector', function () {
        $('#project-selector .search-wrapper input').focus();
    });

    // Add project
    container.on('click', '#project-selector .menu li', function () {
        var slug = $(this).data('slug'),
            $permsForm = $(".project-locale[data-slug='" + slug + "']");

        $('.project-locale:last').after($permsForm.removeClass('hidden'));

        $permsForm.append(
            inputHidden(
                'project-locale-' +
                    $permsForm.data('index') +
                    '-has_custom_translators',
                1,
            ),
        );

        // Update menu (must be above Copying Translators)
        $(this).addClass('hidden').removeClass('limited').removeAttr('style');
        if ($('#project-selector .menu li:not(".hidden")').length === 0) {
            $('#project-selector').addClass('hidden');
        }

        // Copy Translators from the General section
        // Reverse selector order to keep presentation order (prepend)
        $(
            $('.permissions-groups.general .translators li').get().reverse(),
        ).each(function () {
            $permsForm
                .find(
                    '.user.available li[data-id="' + $(this).data('id') + '"]',
                )
                .click();
        });

        // Scroll to the right project locale
        $('html, body').animate(
            {
                scrollTop: $permsForm.offset().top,
            },
            500,
        );
    });

    // Remove project
    container.on('click', '.remove-project', function (e) {
        var $permsForm = $(this).parents('.project-locale');
        e.preventDefault();

        $('#project-selector').removeClass('hidden');
        $("#project-selector li[data-slug='" + $permsForm.data('slug') + "']")
            .removeClass('hidden')
            .addClass('limited');

        $permsForm.find('input[name$=has_custom_translators]').remove();

        $permsForm.addClass('hidden');
        $permsForm.find('.select.translators li').each(function () {
            $permsForm.find('.select.available ul').append($(this).remove());
        });
    });
});
