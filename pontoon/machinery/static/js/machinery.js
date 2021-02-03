$(function () {
    var self = Pontoon;

    /*
     * Get suggestions from machine translation and translation memory
     *
     * original Original string
     */
    function getMachinery(original) {
        var ul = $('#helpers > .machinery').children('ul').empty(),
            tab = $('#search').addClass('loading'), // .loading class used on the /machinery page
            requests = 0,
            preferred = 0,
            remaining = 0,
            sourcesMap = {};

        self.NProgressUnbind();

        function append(data) {
            var sources = sourcesMap[data.original + data.translation],
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

                if (data.quality && sources.siblings('.stress').length === 0) {
                    sources.prepend(
                        '<span class="stress">' + data.quality + '</span>',
                    );
                }
            } else {
                var originalTextForDiff = originalText;
                originalText = originalText
                    ? self.diff(original, originalTextForDiff)
                    : '';

                var li = $(
                    '<li class="suggestion"' +
                        ' title="Copy to clipboard"' +
                        ' data-clipboard-text="' +
                        self.doNotRender(translationText) +
                        '">' +
                        '<header>' +
                        (data.quality
                            ? '<span class="stress">' + data.quality + '</span>'
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
                    $('#search').removeClass('loading');

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

        self.NProgressBind();
    }

    // Trigger search with Enter
    $('#search input')
        .unbind('keydown.pontoon')
        .bind('keydown.pontoon', function (e) {
            var value = $(this).val();

            if (e.which === 13 && value.length > 0) {
                self.locale = $('.locale .selector .language').data();
                getMachinery(value);
                return false;
            }
        });

    // Handle "Copy to clipboard" of search results on main Machinery page
    var clipboard = new Clipboard('.machinery .machinery li');

    clipboard.on('success', function (event) {
        var successMessage = $(
                '<span class="clipboard-success">Copied!</span>',
            ),
            $trigger = $(event.trigger);

        $('.clipboard-success').remove();
        $trigger.find('header').prepend(successMessage);
        setTimeout(function () {
            successMessage.fadeOut(500, function () {
                successMessage.remove();
            });
        }, 1000);
    });
});
