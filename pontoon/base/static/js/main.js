/* Must be available immediately */
// Add case insensitive :contains-like selector to jQuery (search)
$.expr[':'].containsi = function (a, i, m) {
    return (
        (a.textContent || a.innerText || '')
            .toUpperCase()
            .indexOf(m[3].toUpperCase()) >= 0
    );
};

/* Public functions used across different files */
var Pontoon = (function (my) {
    return $.extend(true, my, {
        /*
         * Bind NProgress (slim progress bar on top of the page) to each AJAX request
         */
        NProgressBind: function () {
            NProgress.configure({ showSpinner: false });
            $(document)
                .bind('ajaxStart.nprogress', function () {
                    NProgress.start();
                })
                .bind('ajaxStop.nprogress', function () {
                    NProgress.done();
                });
        },

        /*
         * Unbind NProgress
         */
        NProgressUnbind: function () {
            $(document).unbind('.nprogress');
        },

        /*
         * Mark all notifications as read and update UI accordingly
         */
        markAllNotificationsAsRead: function () {
            this.NProgressUnbind();

            $.ajax({
                url: '/notifications/mark-all-as-read/',
                success: function () {
                    $('#notifications.unread .button .icon').animate(
                        { color: '#4D5967' },
                        1000,
                    );
                    var unreadNotifications = $(
                        '.notifications .menu ul.notification-list li.notification-item[data-unread="true"]',
                    );

                    unreadNotifications.animate(
                        { backgroundColor: 'transparent' },
                        1000,
                        function () {
                            // Remove inline style and unread mark to make hover work again
                            unreadNotifications
                                .removeAttr('style')
                                .removeAttr('data-unread');
                        },
                    );
                },
            });

            this.NProgressBind();
        },

        /*
         * Log UX action
         */
        logUxAction: function (action_type, experiment, data) {
            this.NProgressUnbind();

            $.ajax({
                url: '/log-ux-action/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $('body').data('csrf'),
                    action_type,
                    experiment,
                    data: JSON.stringify(data),
                },
            });

            this.NProgressBind();
        },

        /*
         * Close notification
         */
        closeNotification: function () {
            $('.notification').animate(
                {
                    top: '-60px',
                },
                {
                    duration: 200,
                },
                function () {
                    $(this).addClass('hide').empty();
                },
            );
        },

        /*
         * Remove loader
         *
         * text End of operation text (e.g. Done!)
         * type Notification type (e.g. error)
         * duration How long should the notification remain open (default: 2000 ms)
         */
        endLoader: function (text, type, duration) {
            if (text) {
                $('.notification')
                    .html('<li class="' + (type || '') + '">' + text + '</li>')
                    .removeClass('hide')
                    .animate(
                        {
                            top: 0,
                        },
                        {
                            duration: 200,
                        },
                    );
            }

            if (Pontoon.notificationTimeout) {
                clearTimeout(Pontoon.notificationTimeout);
            }
            Pontoon.notificationTimeout = setTimeout(function () {
                Pontoon.closeNotification();
            }, duration || 2000);
        },

        /*
         * Do not render HTML tags
         *
         * string String that has to be displayed as is instead of rendered
         */
        doNotRender: function (string) {
            return $('<div/>').text(string).html();
        },
    });
})(Pontoon || {});

/* Main code */
$(function () {
    /*
     * If Google Analytics is enabled, frontend will send additional about Ajax calls.
     *
     * To send an event to GA, We pass following informations:
     * event category - hardcoded 'ajax' string.
     * event action - hardcoded 'request' string.
     * event label - contains url that was called by $.ajax() call.
     *
     * GA Analytics enriches every event with additional information like e.g. browser, resolution, country etc.
     */
    $(document).ajaxComplete(function (event, jqXHR, settings) {
        if (typeof ga !== 'function') {
            return;
        }

        ga('send', 'event', 'ajax', 'request', settings.url);
    });

    /*
     * Display Pontoon Add-On Promotion, if:
     *
     * - Promotion not dismissed
     * - Add-On not installed
     * - Page loaded on Firefox or Chrome (add-on not available for other browsers)
     */
    setTimeout(function () {
        var dismissed = !$('#addon-promotion').length;
        var installed = window.PontoonAddon && window.PontoonAddon.installed;
        if (!dismissed && !installed) {
            var isFirefox = navigator.userAgent.indexOf('Firefox') !== -1;
            var isChrome = navigator.userAgent.indexOf('Chrome') !== -1;
            var downloadHref = '';
            if (isFirefox) {
                downloadHref =
                    'https://addons.mozilla.org/firefox/addon/pontoon-tools/';
            }
            if (isChrome) {
                downloadHref =
                    'https://chrome.google.com/webstore/detail/pontoon-add-on/gnbfbnpjncpghhjmmhklfhcglbopagbb';
            }
            if (downloadHref) {
                $('#addon-promotion').find('.get').attr('href', downloadHref);
                $('body').addClass('addon-promotion-active');
            }
        }
        // window.PontoonAddon is made available by the Pontoon Add-On,
        // but not immediatelly after the DOM is ready
    }, 1000);

    // Dismiss Add-On Promotion
    $('#addon-promotion .dismiss').click(function () {
        Pontoon.NProgressUnbind();

        $.ajax({
            url: '/dismiss-addon-promotion/',
            success: function () {
                $('body').removeClass('addon-promotion-active');
            },
        });

        Pontoon.NProgressBind();
    });

    // Hide Add-On Promotion if Add-On installed while active
    window.addEventListener('message', (e) => {
        const data = JSON.parse(e.data);
        if (data._type === 'PontoonAddonInfo') {
            if (data.value.installed) {
                $('body').removeClass('addon-promotion-active');
            }
        }
    });

    Pontoon.NProgressBind();

    var unreadNotificationsExist = $('#notifications').is('.unread');

    // Log display of the unread notification icon
    if (unreadNotificationsExist) {
        Pontoon.logUxAction(
            'Render: Unread notifications icon',
            'Notifications 1.0',
            {
                pathname: window.location.pathname,
            },
        );
    }

    // Log clicks on the notifications icon
    $('#notifications .button').click(function () {
        if ($('#notifications').is('.opened')) {
            return;
        }

        Pontoon.logUxAction('Click: Notifications icon', 'Notifications 1.0', {
            pathname: window.location.pathname,
            unread: unreadNotificationsExist,
        });
    });

    // Display any notifications
    var notifications = $('.notification li');
    if (notifications.length) {
        Pontoon.endLoader(notifications.text());
    }

    // Close notification on click
    $('body > header').on('click', '.notification', function () {
        Pontoon.closeNotification();
    });

    // Mark notifications as read when notification menu opens
    $('#notifications.unread .button').click(function () {
        Pontoon.markAllNotificationsAsRead();
    });

    function getRedirectUrl() {
        return window.location.pathname + window.location.search;
    }

    // Sign in button action
    $('#fxa-sign-in, #standalone-signin a, #sidebar-signin').on(
        'click',
        function () {
            var $this = $(this);
            var loginUrl = $this.prop('href'),
                startSign = loginUrl.match(/\?/) ? '&' : '?';
            $this.prop(
                'href',
                loginUrl + startSign + 'next=' + getRedirectUrl(),
            );
        },
    );

    // Sign out button action
    $('.sign-out a, #sign-out a').on('click', function (ev) {
        var $this = $(this),
            $form = $this.find('form');

        ev.preventDefault();
        $form.prop('action', $this.prop('href') + '?next=' + getRedirectUrl());
        $form.submit();
    });

    // Show/hide menu on click
    $('body').on('click', '.selector', function (e) {
        if (!$(this).siblings('.menu').is(':visible')) {
            e.stopPropagation();
            $('.menu:not(".permanent")').hide();
            $('.select').removeClass('opened');
            $(this)
                .siblings('.menu')
                .show()
                .end()
                .parents('.select')
                .addClass('opened');
            $('.menu:not(".permanent"):visible input[type=search]')
                .focus()
                .trigger('input');
        }
    });

    // Hide menus on click outside
    $('body').bind('click.main', function () {
        $('.menu:not(".permanent")').hide();
        $('.select').removeClass('opened');
        $('.menu:not(".permanent") li').removeClass('hover');
    });

    // Menu hover
    $('body')
        .on('mouseenter', '.menu li', function () {
            // Ignore on nested menus
            if ($(this).parents('li').length) {
                return false;
            }

            $('.menu li.hover').removeClass('hover');
            $(this).toggleClass('hover');
        })
        .on('mouseleave', '.menu li', function () {
            // Ignore on nested menus
            if ($(this).parents('li').length) {
                return false;
            }

            $('.menu li.hover').removeClass('hover');
        });

    // Menu search
    $('body')
        .on('click', '.menu input[type=search]', function (e) {
            e.stopPropagation();
        })
        .on('input.search', '.menu input[type=search]', function (e) {
            // Tab
            if (e.which === 9) {
                return;
            }

            var ul = $(this).parent().siblings('ul'),
                val = $(this).val(),
                // Only search a limited set if defined
                limited = ul.find('li.limited').length > 0 ? '.limited' : '';

            ul.find('li' + limited)
                .show()
                .end()
                .find('li' + limited + ':not(":containsi(\'' + val + '\')")')
                .hide();

            if (ul.find('li:not(".no-match"):visible').length === 0) {
                ul.find('.no-match').show();
            } else {
                ul.find('.no-match').hide();
            }
        })
        .on('keydown.search', '.menu input[type=search]', function (e) {
            // Prevent form submission on Enter
            if (e.which === 13) {
                return false;
            }
        });

    // General keyboard shortcuts
    generalShortcutsHandler = function (e) {
        function moveMenu(type) {
            var options =
                type === 'up' ? ['first', 'last', -1] : ['last', 'first', 1];
            var items = menu.find(
                'li:visible:not(.horizontal-separator, :has(li))',
            );
            var element = null;

            if (
                hovered.length === 0 ||
                menu.find('li:not(:has(li)):visible:' + options[0]).is('.hover')
            ) {
                menu.find('li.hover').removeClass('hover');
                element = items[options[1]]();
            } else {
                var current = menu.find('li.hover'),
                    next = items.index(current) + options[2];

                current.removeClass('hover');
                element = $(items.get(next));
            }

            if (element) {
                element.addClass('hover');
                element[0].scrollIntoView({
                    behavior: 'smooth',
                    block: 'nearest',
                });
            }
        }

        var key = e.which;

        if ($('.menu:not(".permanent")').is(':visible')) {
            var menu = $('.menu:not(".permanent"):visible'),
                hovered = menu.find('li.hover');

            // Skip for the tabs
            if (menu.is('.tabs')) {
                return;
            }

            // Up arrow
            if (key === 38) {
                moveMenu('up');
                return false;
            }

            // Down arrow
            if (key === 40) {
                moveMenu('down');
                return false;
            }

            // Enter: confirm
            if (key === 13) {
                var a = hovered.find('a');
                if (a.length > 0) {
                    a.click();
                } else {
                    hovered.click();
                }
                return false;
            }

            // Escape: close
            if (key === 27) {
                $('body').click();
                return false;
            }
        }
    };
    $('html').on('keydown', generalShortcutsHandler);
});
