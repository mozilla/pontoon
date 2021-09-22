/*
 * Manage tab content as single-page application
 */
$(function () {
    var urlSplit = $('#server').data('url-split'),
        container = $('#main .container'),
        inProgress = false;

    // Page load
    loadTabContent(window.location.pathname + window.location.search);

    // History
    window.onpopstate = function () {
        loadTabContent(window.location.pathname + window.location.search);
    };

    // Menu
    $('body').on(
        'click',
        '#middle .links a, #main .contributors .links a',
        function (e) {
            // Keep default middle-, control- and command-click behaviour (open in new tab)
            if (e.which === 2 || e.metaKey || e.ctrlKey) {
                return;
            }

            // Filtered teams are only supported by the Teams tab, so we need to drop them
            // when switching to other tabs and update stats in the heading section by
            // reloading the page
            if (new URLSearchParams(window.location.search).get('teams')) {
                return;
            }

            e.preventDefault();

            var url = $(this).attr('href');
            loadTabContent(url);
            window.history.pushState({}, '', url);
        },
    );

    function showTabMessage(text) {
        var message = $('<p>', {
            class: 'no-results',
            html: text,
        });

        container.append(message);
    }

    function updateTabCount(tab, count) {
        tab.find('span').remove();
        if (count > 0) {
            $('<span>', {
                class: 'count',
                html: count,
            }).appendTo(tab);
        }
    }

    function loadTabContent(path) {
        if (inProgress) {
            inProgress.abort();
        }

        var url = '/' + path.split('/' + urlSplit + '/')[1],
            tab = $('#middle .links a[href="' + path.split('?')[0] + '"]');

        // Update menu
        $('#middle .links li').removeClass('active');
        tab.parents('li').addClass('active');

        container.empty();

        if (url !== '/bugs/') {
            inProgress = $.ajax({
                url: '/' + urlSplit + '/ajax' + url,
                success: function (data) {
                    container.append(data);

                    if (url.startsWith('/contributors/')) {
                        var count = $('table > tbody > tr').length;
                        updateTabCount(tab, count);
                    }

                    if (url.startsWith('/insights/')) {
                        Pontoon.insights.initialize();
                    }

                    if (url === '/') {
                        $('.controls input').focus();
                    }
                },
                error: function (error) {
                    if (error.status === 0 && error.statusText !== 'abort') {
                        showTabMessage('Oops, something went wrong.');
                    }
                },
            });
        } else {
            inProgress = Pontoon.bugzilla.getLocaleBugs(
                $('#server').data('locale'),
                container,
                tab,
                updateTabCount,
                showTabMessage,
            );
        }
    }
});
