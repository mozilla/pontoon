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
         * Remove duplicate items from the array of numeric values
         *
         * TODO: Switch to ES6 and replace with Set
         */
        removeDuplicates: function (array) {
            var seen = {};
            return array.filter(function (item) {
                return seen.hasOwnProperty(item) ? false : (seen[item] = true);
            });
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
         * Update scrollbar position in the menu
         *
         * menu Menu element
         */
        updateScroll: function (menu) {
            var hovered = menu.find('[class*=hover]'),
                maxHeight = menu.height(),
                visibleTop = menu.scrollTop(),
                visibleBottom = visibleTop + maxHeight,
                hoveredTop = visibleTop + hovered.position().top,
                hoveredBottom = hoveredTop + hovered.outerHeight();

            if (hoveredBottom >= visibleBottom) {
                menu.scrollTop(Math.max(hoveredBottom - maxHeight, 0));
            } else if (hoveredTop < visibleTop) {
                menu.scrollTop(hoveredTop);
            }
        },

        /*
         * Do not render HTML tags
         *
         * string String that has to be displayed as is instead of rendered
         */
        doNotRender: function (string) {
            return $('<div/>').text(string).html();
        },

        /*
         * Strip HTML tags from the given string
         */
        stripHTML: function (string) {
            return $($.parseHTML(string)).text();
        },

        /*
         * Converts a number to a string containing commas every three digits
         */
        numberWithCommas: function (number) {
            return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        },

        /*
         * Markup XML Tags
         *
         * Find any XML Tags in a string and mark them up, while making sure
         * the rest of the text in a string is displayed not rendered.
         */
        markXMLTags: function (string) {
            var self = this;

            var markedString = '';
            var startMarker = '<mark class="placeable" title="XML Tag">';
            var endMarker = '</mark>';

            var re = /(<[^(><.)]+>)/gi;
            var results;
            var previousIndex = 0;

            function doNotRenderSubstring(start, end) {
                return self.doNotRender(string.substring(start, end));
            }

            // Find successive matches
            while ((results = re.exec(string)) !== null) {
                markedString +=
                    // Substring between the previous and the current tag: do not render
                    doNotRenderSubstring(previousIndex, results.index) +
                    // Tag: do not render and wrap in markup
                    startMarker +
                    doNotRenderSubstring(results.index, re.lastIndex) +
                    endMarker;
                previousIndex = re.lastIndex;
            }

            // Substring between the last tag and the end of the string: do not render
            markedString += doNotRenderSubstring(previousIndex, string.length);

            return markedString;
        },

        /*
         * Get markup for a placeable instance.
         */
        getPlaceableMarkup: function (title, replacement) {
            return (
                '<mark class="placeable" title="' +
                title +
                '">' +
                replacement +
                '</mark>'
            );
        },

        /*
         * Mark single instance of a placeable in string
         */
        markPlaceable: function (string, regex, title, replacement) {
            replacement = replacement || '$&';
            return string.replace(
                regex,
                this.getPlaceableMarkup(title, replacement),
            );
        },

        /*
         * Markup placeables
         */
        markPlaceables: function (string, whiteSpaces) {
            var self = this;
            whiteSpaces = whiteSpaces !== false;

            string = self.doNotRender(string);

            /* Special spaces */
            // Pontoon.doNotRender() replaces \u00A0 with &nbsp;
            string = self.markPlaceable(
                string,
                /&nbsp;/gi,
                'Non-breaking space',
            );
            string = self.markPlaceable(
                string,
                /[\u202F]/gi,
                'Narrow non-breaking space',
            );
            string = self.markPlaceable(string, /[\u2009]/gi, 'Thin space');

            /* Multiple spaces */
            string = string.replace(/  +/gi, function (match) {
                var title = 'Multiple spaces',
                    replacement = '';

                for (var i = 0; i < match.length; i++) {
                    replacement += ' &middot; ';
                }
                return self.getPlaceableMarkup(title, replacement);
            });

            if (whiteSpaces) {
                string = self.markWhiteSpaces(string);
            }

            return string;
        },

        /*
         * Mark leading/trailing spaces in multiline strings (that contain newlines inside).
         * Should be applied to a fully concatenated string, doesn't handle substrings well.
         */
        markWhiteSpaces: function (string) {
            /* 'm' modifier makes regex applicable to every separate line in string, not the string as the whole. */

            /* Leading space */
            string = string.replace(
                /^(<(ins|del)>)*( )/gim,
                '$1' + this.getPlaceableMarkup('Leading space', ' '),
            );

            /* Trailing space */
            string = string.replace(
                /( )(<\/(ins|del)>)*$/gim,
                this.getPlaceableMarkup('Trailing space', ' ') + '$2',
            );

            /* Newline */
            string = this.markPlaceable(
                string,
                /\n/gi,
                'Newline character',
                '¶$&',
            );

            /* Tab */
            string = this.markPlaceable(
                string,
                /\t/gi,
                'Tab character',
                '&rarr;',
            );
            return string;
        },

        /*
         * Mark diff between the string and the reference string
         */
        diff: function (reference, string) {
            var self = this,
                diff_obj = new diff_match_patch(),
                diff = diff_obj.diff_main(reference, string),
                output = '';
            diff_obj.diff_cleanupSemantic(diff);
            diff_obj.diff_cleanupEfficiency(diff);

            $.each(diff, function () {
                var type = this[0],
                    slice = this[1];

                switch (type) {
                    case DIFF_INSERT:
                        output +=
                            '<ins>' +
                            self.markPlaceables(slice, false) +
                            '</ins>';
                        break;

                    case DIFF_DELETE:
                        output +=
                            '<del>' +
                            self.markPlaceables(slice, false) +
                            '</del>';
                        break;

                    case DIFF_EQUAL:
                        output += self.markPlaceables(slice, false);
                        break;
                }
            });

            /* Marking of leading/trailing spaces has to be the last step to avoid false positives. */
            return self.markWhiteSpaces(output);
        },

        /*
         * Linkifies any traces of URLs present in a given string.
         *
         * Matches the URL Regex and parses the required matches.
         * Can find more than one URL in the given string.
         *
         * Escapes HTML tags.
         */
        linkify: function (string) {
            // http://, https://, ftp://
            var urlPattern = /\b(?:https?|ftp):\/\/[a-z0-9-+&@#/%?=~_|!:,.;]*[a-z0-9-+&@#/%=~_|]/gim;
            // www. sans http:// or https://
            var pseudoUrlPattern = /(^|[^/])(www\.[\S]+(\b|$))/gim;

            return this.doNotRender(string)
                .replace(
                    urlPattern,
                    '<a href="$&" target="_blank" rel="noopener noreferrer">$&</a>',
                )
                .replace(
                    pseudoUrlPattern,
                    '$1<a href="http://$2" target="_blank" rel="noopener noreferrer">$2</a>',
                );
        },

        /*
         * Show no connection error in helpers
         *
         * list List to append no connection error to
         */
        noConnectionError: function (list) {
            list.append(
                '<li class="disabled">' +
                    '<p>Content not available while offline.</p>' +
                    '<p>Check your connection and try again.</p>' +
                    '</li>',
            );
        },

        /*
         * Get suggestions from machine translation and translation memory
         *
         * original Original string
         * customSearch Instead of source string, use custom search keyword as input
         * loader Loader element id
         */
        getMachinery: function (original, customSearch, loader) {
            loader = loader || 'helpers li a[href="#machinery"]';
            var self = this,
                ul = $('#helpers > .machinery').children('ul').empty(),
                tab = $('#' + loader).addClass('loading'), // .loading class used on the /machinery page
                requests = 0,
                preferred = 0,
                remaining = 0,
                sourcesMap = {};

            if (!customSearch) {
                var entity = self.getEditorEntity();
            }

            self.NProgressUnbind();

            function append(data) {
                var title =
                        loader !== 'search'
                            ? ' title="Copy Into Translation (Tab)"'
                            : ' title="Copy to clipboard"',
                    sources = sourcesMap[data.original + data.translation],
                    occurrencesTitle = 'Number of translation occurrences',
                    originalText = data.original,
                    translationText = data.translation;

                if (sources) {
                    sources.append(
                        '<li><a class="translation-source" href="' +
                            data.url +
                            '" target="_blank" rel="noopener noreferrer" title="' +
                            data.title +
                            '">' +
                            '<span>' +
                            data.source +
                            '</span>' +
                            (data.count
                                ? '<sup title="' +
                                  occurrencesTitle +
                                  '">' +
                                  data.count +
                                  '</sup>'
                                : '') +
                            '</a></li>',
                    );

                    if (
                        data.quality &&
                        sources.siblings('.stress').length === 0
                    ) {
                        sources.prepend(
                            '<span class="stress">' + data.quality + '</span>',
                        );
                    }
                } else {
                    if (data.source !== 'Caighdean') {
                        var originalTextForDiff = originalText;

                        originalText = originalText
                            ? self.diff(original, originalTextForDiff)
                            : '';
                    }
                    var li = $(
                        '<li class="suggestion"' +
                            title +
                            ' data-clipboard-text="' +
                            self.doNotRender(translationText) +
                            '">' +
                            '<header>' +
                            (data.quality
                                ? '<span class="stress">' +
                                  data.quality +
                                  '</span>'
                                : '') +
                            '<ul class="sources">' +
                            '<li data-source="' +
                            data.source +
                            '">' +
                            '<a class="translation-source" href="' +
                            data.url +
                            '" target="_blank" rel="noopener noreferrer" title="' +
                            data.title +
                            '">' +
                            '<span>' +
                            data.source +
                            '</span>' +
                            (data.count
                                ? '<sup title="' +
                                  occurrencesTitle +
                                  '">' +
                                  data.count +
                                  '</sup>'
                                : '') +
                            '</a>' +
                            '</li>' +
                            '</ul>' +
                            '</header>' +
                            '<p class="original">' +
                            originalText +
                            '</p>' +
                            '<p class="translation" dir="' +
                            self.locale.direction +
                            '" lang="' +
                            self.locale.code +
                            '" data-script="' +
                            self.locale.script +
                            '">' +
                            self.markPlaceables(translationText) +
                            '</p>' +
                            '<p class="translation-clipboard">' +
                            self.doNotRender(translationText) +
                            '</p>' +
                            '</li>',
                    );
                    ul.append(li);
                    sourcesMap[data.original + data.translation] = li.find(
                        '.sources',
                    );
                    if (data.source === 'Translation memory') {
                        preferred++;
                    } else {
                        remaining++;
                    }
                }

                // Sort by quality
                var listitems = ul.children('li'),
                    sourceMap = {
                        'Translation memory': 1,
                        Mozilla: 2,
                        Microsoft: 3,
                        'Systran Translate': 4,
                        'Google Translate': 5,
                        'Microsoft Translator': 6,
                        Caighdean: 7,
                    };

                function getTranslationSource(el) {
                    var sources = $(el).find('.translation-source span');

                    if (sources.length > 1) {
                        return Math.min.apply(
                            Math,
                            $.map(sources, function (elem) {
                                return sourceMap[$(elem).text()];
                            }),
                        );
                    } else {
                        return sourceMap[sources.text()];
                    }
                }

                listitems.sort(function (a, b) {
                    var stressA = $(a).find('.stress'),
                        stressB = $(b).find('.stress'),
                        valA = stressA.length
                            ? parseInt(stressA.html().split('%')[0])
                            : 0,
                        valB = stressB.length
                            ? parseInt(stressB.html().split('%')[0])
                            : 0,
                        sourceA = getTranslationSource(a),
                        sourceB = getTranslationSource(b);

                    return valA < valB
                        ? 1
                        : valA > valB
                        ? -1
                        : sourceA > sourceB
                        ? 1
                        : sourceA < sourceB
                        ? -1
                        : 0;
                });

                ul.html(listitems);

                // Sort sources inside results.
                ul.find('.sources').each(function () {
                    var $sourcesList = $(this),
                        sources = $sourcesList.children('li'),
                        sortedItems = sources.sort(function (a, b) {
                            var sourceA = sourceMap[$(a).find('span').text()],
                                sourceB = sourceMap[$(b).find('span').text()];
                            return sourceA > sourceB
                                ? 1
                                : sourceA < sourceB
                                ? -1
                                : 0;
                        });

                    $sourcesList.children('li').remove();

                    sortedItems.each(function () {
                        $sourcesList.append(this);
                    });
                });
            }

            function error(error) {
                if (error.status === 0 && error.statusText !== 'abort') {
                    // Allows requesting Machinery again
                    editor.machinery = null;
                    if (ul.children('li').length === 0) {
                        self.noConnectionError(ul);
                    }
                }
            }

            function complete(jqXHR, status) {
                if (status !== 'abort') {
                    requests--;
                    tab.find('.count')
                        .find('.preferred')
                        .html(preferred)
                        .toggle(preferred > 0)
                        .end()
                        .find('.plus')
                        .html('+')
                        .toggle(preferred > 0 && remaining > 0)
                        .end()
                        .find('.remaining')
                        .html(remaining)
                        .toggle(remaining > 0)
                        .end()
                        .toggle(preferred > 0 || remaining > 0);

                    // All requests complete
                    if (requests === 0) {
                        // Stop the loader
                        $('#' + loader).removeClass('loading');

                        // No match
                        if (ul.children('li').length === 0) {
                            tab.find('.count').hide();
                            ul.append(
                                '<li class="disabled">' +
                                    '<p>No translations available.</p>' +
                                    '</li>',
                            );
                        }
                    }
                }
            }

            // Translation memory
            requests++;

            if (self.XHRtranslationMemory) {
                self.XHRtranslationMemory.abort();
            }

            self.XHRtranslationMemory = $.ajax({
                url: '/translation-memory/',
                data: {
                    text: original,
                    locale: self.locale.code,
                    pk: !customSearch ? entity.pk : '',
                },
            })
                .success(function (data) {
                    if (data) {
                        $.each(data, function () {
                            append({
                                original: this.source,
                                quality: Math.round(this.quality) + '%',
                                url: '/',
                                title: 'Pontoon Homepage',
                                source: 'Translation memory',
                                translation: this.target,
                                count: this.count,
                            });
                        });
                    }
                })
                .error(error)
                .complete(complete);

            // Google Translate
            if (
                $('#server').data('is-google-translate-supported') &&
                self.locale.google_translate_code
            ) {
                requests++;

                if (self.XHRgoogleTranslate) {
                    self.XHRgoogleTranslate.abort();
                }

                self.XHRgoogleTranslate = $.ajax({
                    url: '/google-translate/',
                    data: {
                        text: original,
                        locale: self.locale.google_translate_code,
                    },
                })
                    .success(function (data) {
                        if (data.translation) {
                            append({
                                url: 'https://translate.google.com/',
                                title: 'Visit Google Translate',
                                source: 'Google Translate',
                                original: original,
                                translation: data.translation,
                            });
                        }
                    })
                    .error(error)
                    .complete(complete);
            }

            // Microsoft Translator
            if (
                $('#server').data('is-microsoft-translator-supported') &&
                self.locale.ms_translator_code
            ) {
                requests++;

                if (self.XHRmicrosoftTranslator) {
                    self.XHRmicrosoftTranslator.abort();
                }

                self.XHRmicrosoftTranslator = $.ajax({
                    url: '/microsoft-translator/',
                    data: {
                        text: original,
                        locale: self.locale.ms_translator_code,
                    },
                })
                    .success(function (data) {
                        if (data.translation) {
                            append({
                                url: 'https://www.bing.com/translator',
                                title: 'Visit Bing Translator',
                                source: 'Microsoft Translator',
                                original: original,
                                translation: data.translation,
                            });
                        }
                    })
                    .error(error)
                    .complete(complete);
            }

            // Systran Translate
            if (
                $('#server').data('is-systran-translate-supported') &&
                self.locale.systran_translate_code
            ) {
                requests++;

                if (self.XHRsystranTranslate) {
                    self.XHRsystranTranslate.abort();
                }

                self.XHRsystranTranslate = $.ajax({
                    url: '/systran-translate/',
                    data: {
                        text: original,
                        locale: self.locale.systran_translate_code,
                    },
                })
                    .success(function (data) {
                        if (data.translation) {
                            append({
                                url:
                                    'https://translate.systran.net/translationTools',
                                title: 'Visit Systran Translate',
                                source: 'Systran Translate',
                                original: original,
                                translation: data.translation,
                            });
                        }
                    })
                    .error(error)
                    .complete(complete);
            }

            // Microsoft Terminology
            if (self.locale.ms_terminology_code.length) {
                requests++;

                if (self.XHRmicrosoftTerminology) {
                    self.XHRmicrosoftTerminology.abort();
                }

                self.XHRmicrosoftTerminology = $.ajax({
                    url: '/microsoft-terminology/',
                    data: {
                        text: original,
                        locale: self.locale.ms_terminology_code,
                    },
                })
                    .success(function (data) {
                        if (data.translations) {
                            $.each(data.translations, function () {
                                append({
                                    original: this.source,
                                    quality: Math.round(this.quality) + '%',
                                    url:
                                        'https://www.microsoft.com/Language/en-US/Search.aspx?sString=' +
                                        this.source +
                                        '&langID=' +
                                        self.locale.ms_terminology_code,
                                    title:
                                        'Visit Microsoft Terminology Service API.\n' +
                                        '© 2018 Microsoft Corporation. All rights reserved.',
                                    source: 'Microsoft',
                                    translation: this.target,
                                });
                            });
                        }
                    })
                    .error(error)
                    .complete(complete);
            }

            // Transvision
            if (self.locale.transvision) {
                requests++;

                if (self.XHRtransvision) {
                    self.XHRtransvision.abort();
                }

                self.XHRtransvision = $.ajax({
                    url: '/transvision/',
                    data: {
                        text: original,
                        locale: self.locale.code,
                    },
                })
                    .success(function (data) {
                        if (data) {
                            $.each(data, function () {
                                append({
                                    original: this.source,
                                    quality: Math.round(this.quality) + '%',
                                    url:
                                        'https://transvision.mozfr.org/?repo=global' +
                                        '&recherche=' +
                                        encodeURIComponent(original) +
                                        '&locale=' +
                                        self.locale.code,
                                    title: 'Visit Transvision',
                                    source: 'Mozilla',
                                    translation: this.target,
                                });
                            });
                        }
                    })
                    .error(error)
                    .complete(complete);
            }

            // Caighdean
            if (!customSearch && self.locale.code === 'ga-IE') {
                requests++;

                if (self.XHRcaighdean) {
                    self.XHRcaighdean.abort();
                }

                self.XHRcaighdean = $.ajax({
                    url: '/caighdean/',
                    data: {
                        id: entity.pk,
                        locale: self.locale.code,
                    },
                })
                    .success(function (data) {
                        if (data.translation) {
                            append({
                                url: 'https://github.com/kscanne/caighdean',
                                title: 'Visit Caighdean Machine Translation',
                                source: 'Caighdean',
                                original: data.original,
                                translation: data.translation,
                            });
                        }
                    })
                    .error(error)
                    .complete(complete);
            }

            self.NProgressBind();
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

    Pontoon.NProgressBind();

    // Display any notifications
    var notifications = $('.notification li');
    if (notifications.length) {
        Pontoon.endLoader(notifications.text());
    }

    // Close notification on click
    $('body > header').on('click', '.notification', function () {
        Pontoon.closeNotification();
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
            $('#iframe-cover:not(".hidden")').hide(); // iframe fix
            $(this)
                .siblings('.menu')
                .show()
                .end()
                .parents('.select')
                .addClass('opened');
            $('#iframe-cover:not(".hidden")').show(); // iframe fix
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
        .on('mouseenter', '.menu li, .menu .static-links div', function () {
            // Ignore on nested menus
            if ($(this).parents('li').length) {
                return false;
            }

            $('.menu li.hover, .static-links div').removeClass('hover');
            $(this).toggleClass('hover');
        })
        .on('mouseleave', '.menu li, .menu .static-links div', function () {
            // Ignore on nested menus
            if ($(this).parents('li').length) {
                return false;
            }

            $('.menu li.hover, .static-links div').removeClass('hover');
        });

    // Mark notifications as read when notification menu opens
    $('#notifications.unread .button .icon').click(function () {
        Pontoon.markAllNotificationsAsRead();
    });

    // Profile menu
    $('#profile .menu li').click(function (e) {
        if ($(this).has('a').length) {
            return;
        }
        e.preventDefault();

        if ($(this).is('.download')) {
            Pontoon.updateFormFields($('form#download-file'));
            $('form#download-file').submit();
        } else if ($(this).is('.upload')) {
            $('#id_uploadfile').click();
        } else if ($(this).is('.check-box')) {
            e.stopPropagation();
        }
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

    // Tabs
    $('.tabs nav a').click(function (e) {
        e.preventDefault();

        var tab = $(this),
            section = tab.attr('href').substr(1);

        tab.parents('li')
            .siblings()
            .removeClass('active')
            .end()
            .addClass('active')
            .end()

            .parents('.tabs')
            .find('section')
            .hide()
            .end()
            .find('section.' + section)
            .show();
    });

    // Toggle user profile attribute
    $('.check-box').click(function () {
        var self = $(this);

        $.ajax({
            url: '/api/v1/user/' + $('#server').data('username') + '/',
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('#server').data('csrf'),
                attribute: self.data('attribute'),
                value: !self.is('.enabled'),
            },
            success: function () {
                self.toggleClass('enabled');
                var is_enabled = self.is('.enabled'),
                    status = is_enabled ? 'enabled' : 'disabled';

                Pontoon.endLoader(self.text() + ' ' + status + '.');

                if (self.is('.force-suggestions') && Pontoon.user) {
                    Pontoon.user.forceSuggestions = is_enabled;
                    Pontoon.postMessage('UPDATE-ATTRIBUTE', {
                        object: 'user',
                        attribute: 'forceSuggestions',
                        value: is_enabled,
                    });
                    Pontoon.updateSaveButtons();
                }
            },
            error: function () {
                Pontoon.endLoader('Oops, something went wrong.', 'error');
            },
        });
    });

    // General keyboard shortcuts
    generalShortcutsHandler = function (e) {
        function moveMenu(type) {
            var options =
                    type === 'up'
                        ? ['first', 'last', -1]
                        : ['last', 'first', 1],
                items = menu.find(
                    'li:visible:not(.horizontal-separator, .time-range-toolbar, :has(li))',
                );

            if (
                hovered.length === 0 ||
                menu.find('li:not(:has(li)):visible:' + options[0]).is('.hover')
            ) {
                menu.find('li.hover').removeClass('hover');
                items[options[1]]().addClass('hover');
            } else {
                var current = menu.find('li.hover'),
                    next = items.index(current) + options[2];

                current.removeClass('hover');
                $(items.get(next)).addClass('hover');
            }

            if (menu.parent().is('.project, .part, .locale')) {
                Pontoon.updateScroll(menu.find('ul'));
            }
        }

        var key = e.which;

        if ($('.menu:not(".permanent")').is(':visible')) {
            var menu = $('.menu:visible'),
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

        if (
            $('#sidebar').is(':visible') &&
            (Pontoon.app.advanced || !$('#editor').is('.opened'))
        ) {
            // Ctrl + Shift + F: Focus Search
            if (e.ctrlKey && e.shiftKey && key === 70) {
                $('#search').focus();
                return false;
            }

            // Ctrl + Shift + A: Select All Strings
            if (
                Pontoon.user.canTranslate() &&
                e.ctrlKey &&
                e.shiftKey &&
                key === 65
            ) {
                Pontoon.selectAllEntities();
                return false;
            }

            // Escape: Deselect entities and switch to first entity
            if (
                Pontoon.user.canTranslate() &&
                $('#entitylist .entity.selected').length &&
                key === 27
            ) {
                if (Pontoon.app.advanced) {
                    Pontoon.openFirstEntity();
                } else {
                    Pontoon.goBackToEntityList();
                }
                return false;
            }
        }
    };
    $('html').on('keydown', generalShortcutsHandler);
});
