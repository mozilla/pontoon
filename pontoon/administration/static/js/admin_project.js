$(function () {
    // Before submitting the form
    $('#admin-form').submit(function () {
        // Update locales
        var locales = [
            {
                list: 'selected',
                input: $('#id_locales'),
            },
            {
                list: 'readonly',
                input: $('#id_locales_readonly'),
            },
        ];

        locales.forEach(function (type) {
            var ids = $('.admin-team-selector .locale.' + type.list)
                .find('li[data-id]')
                .map(function () {
                    return $(this).data('id');
                })
                .get();
            type.input.val(ids);
        });

        // Update form action
        var slug = $('#id_slug').val();
        if (slug.length > 0) {
            slug += '/';
        }
        $('#admin-form').attr(
            'action',
            $('#admin-form').attr('action').split('/projects/')[0] +
                '/projects/' +
                slug
        );
    });

    // Submit form with Enter (keyCode === 13)
    $('html')
        .unbind('keydown.pontoon')
        .bind('keydown.pontoon', function (e) {
            if (
                $('input[type=text]:focus').length > 0 ||
                $('input[type=url]:focus').length > 0
            ) {
                var key = e.keyCode || e.which;
                if (key === 13) {
                    // A short delay to allow digest of autocomplete before submit
                    setTimeout(function () {
                        $('#admin-form').submit();
                    }, 1);
                    return false;
                }
            }
        });

    // Submit form with button
    $('.save').click(function (e) {
        e.preventDefault();
        $('#admin-form').submit();
    });

    // Manually Sync project
    $('.sync').click(function (e) {
        e.preventDefault();

        var button = $(this),
            title = button.html();

        if (button.is('.in-progress')) {
            return;
        }

        button.addClass('in-progress').html('Syncing...');

        $.ajax({
            url: '/admin/projects/' + $('#id_slug').val() + '/sync/',
        })
            .success(function () {
                button.html('Started');
            })
            .error(function () {
                button.html('Whoops!');
            })
            .complete(function () {
                setTimeout(function () {
                    button.removeClass('in-progress').html(title);
                }, 2000);
            });
    });

    // Manually Pretranslate project
    $('.pretranslate').click(function (e) {
        e.preventDefault();

        var button = $(this),
            title = button.html();

        if (button.is('.in-progress')) {
            return;
        }

        button.addClass('in-progress').html('Pretranslating...');

        $.ajax({
            url: '/admin/projects/' + $('#id_slug').val() + '/pretranslate/',
        })
            .success(function () {
                button.html('Started');
            })
            .error(function () {
                button.html('Whoops!');
            })
            .complete(function () {
                setTimeout(function () {
                    button.removeClass('in-progress').html(title);
                }, 2000);
            });
    });

    // Suggest slugified name for new projects
    $('#id_name').blur(function () {
        if ($('input[name=pk]').length > 0 || !$('#id_name').val()) {
            return;
        }
        $('#id_slug').attr('placeholder', 'Retrieving...');
        $.ajax({
            url: '/admin/get-slug/',
            data: {
                name: $('#id_name').val(),
            },
            success: function (data) {
                var value = data === 'error' ? '' : data;
                $('#id_slug').val(value);
            },
            error: function () {
                $('#id_slug').attr('placeholder', '');
            },
        });
    });

    $('body').on('blur', '[id^=id_tag_set-][id$=-name]', function () {
        var target = $('input#' + $(this).attr('id').replace('-name', '-slug'));
        var $this = this;
        if (target.val() || !$(this).val()) {
            return;
        }
        target.attr('placeholder', 'Retrieving...');
        $.ajax({
            url: '/admin/get-slug/',
            data: {
                name: $($this).val(),
            },
            success: function (data) {
                var value = data === 'error' ? '' : data;
                target.val(value);
                target.attr('placeholder', '');
            },
            error: function () {
                target.attr('placeholder', '');
            },
        });
    });

    // Copy locales from another project
    $('#copy-locales option').on('click', function () {
        var projectLocales = [];

        try {
            projectLocales = JSON.parse($(this).val());
        } catch (error) {
            // No project selected
            return;
        }

        $('.readonly .move-all').click();
        $('.selected .move-all.left').click();

        $(projectLocales).each(function (i, id) {
            $('.locale.select:first')
                .find('[data-id=' + id + ']')
                .click();
        });
    });

    // Show new strings input or link when source type is "database".
    function displayNewStringsInput(input) {
        if (input.val() === 'database') {
            $('.new-strings').show();
            $('.manage-strings').show();

            // For now, we also hide the entire Repositories section. We might
            // want to revisit that behavior later.
            $('.repositories').hide();
        } else {
            $('.new-strings').hide();
            $('.manage-strings').hide();
            $('.repositories').show();
        }
    }
    var dataSourceInput = $('#id_data_source');
    dataSourceInput.on('change', function () {
        displayNewStringsInput(dataSourceInput);
    });
    displayNewStringsInput(dataSourceInput);

    // Suggest public repository website URL
    $('body').on('blur', '.repo input', function () {
        var val = $(this)
            .val()
            .replace(/\.git$/, '')
            .replace('git@github.com:', 'https://github.com/')
            .replace('ssh://', 'https://');

        $(this).parents('.repository').find('.website-wrapper input').val(val);
    });

    // Delete inline form item (e.g. subpage or external resource)
    $('body').on('click.pontoon', '.delete-inline', function (e) {
        e.preventDefault();
        $(this).parent().toggleClass('delete');
        $(this).next().prop('checked', !$(this).next().prop('checked'));
    });
    $('.inline [checked]').click().prev().click();

    // Add inline form item (e.g. subpage or external resource)
    var count = {
        subpage: $('.subpage:last').data('count'),
        externalresource: $('.externalresource:last').data('count'),
        entity: $('.entity:last').data('count'),
        tag: $('.tag:last').data('count'),
    };
    $('.add-inline').click(function (e) {
        e.preventDefault();

        var type = $(this).data('type');
        var form = $('.' + type + ':last')
            .html()
            .replace(/__prefix__/g, count[type]);

        $('.' + type + ':last').before(
            '<div class="' + type + ' inline clearfix">' + form + '</div>'
        );
        count[type]++;

        // These two forms of selectors cover all the cases for django-generated forms we use.
        $('#id_' + type + '_set-TOTAL_FORMS').val(count[type]);
        $('#id_form-TOTAL_FORMS').val(count[type]);
    });

    // Toggle branch input
    function toggleBranchInput(element) {
        $(element)
            .parents('.repository')
            .toggleClass('git', $(element).val() === 'git');
    }
    // On select change
    $('body').on('change', '.repository .type-wrapper select', function () {
        toggleBranchInput(this);
    });
    // On page load
    $('.repository .type-wrapper select').each(function () {
        toggleBranchInput(this);
    });

    // Add repo
    var $totalForms = $('#id_repositories-TOTAL_FORMS');
    $('.add-repo').click(function (e) {
        e.preventDefault();
        var count = parseInt($totalForms.val(), 10);

        var $emptyForm = $('.repository-empty');
        var form = $emptyForm.html().replace(/__prefix__/g, count);
        $('.repository:last').after(
            '<div class="repository clearfix">' + form + '</div>'
        );

        toggleBranchInput($('.repository:last').find('.type-wrapper select'));

        $totalForms.val(count + 1);
    });
});
