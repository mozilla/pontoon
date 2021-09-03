// Contains behaviours of widgets that are shared between admin and end-user interface.
$(function () {
    /**
     * Function keeps track of inputs that contain information about the order of selected locales.
     */
    function updateSelectedLocales() {
        var $selectedList = $('.multiple-team-selector .locale.selected'),
            $selectedLocalesField = $selectedList.find('input[type=hidden]'),
            selectedLocales = $selectedList
                .find('li[data-id]')
                .map(function () {
                    return $(this).data('id');
                })
                .get();

        $selectedLocalesField.val(selectedLocales.join());
    }

    // Choose locales
    $('body').on(
        'click',
        '.multiple-team-selector .locale.select li',
        function () {
            var ls = $(this).parents('.locale.select'),
                target = ls.siblings('.locale.select').find('ul'),
                item = $(this).remove();

            target.append(item);
            target.scrollTop(target[0].scrollHeight);
            updateSelectedLocales();
        },
    );

    // Choose/remove all locales
    $('body').on('click', '.multiple-team-selector .move-all', function (e) {
        e.preventDefault();
        var ls = $(this).parents('.locale.select'),
            target = ls.siblings('.locale.select').find('ul'),
            items = ls.find('li:visible:not(".no-match")').remove();

        target.append(items);
        target.scrollTop(target[0].scrollHeight);
        updateSelectedLocales();
    });

    if ($.ui && $.ui.sortable) {
        $('.multiple-team-selector .locale.select .sortable').sortable({
            axis: 'y',
            containment: 'parent',
            update: updateSelectedLocales,
            tolerance: 'pointer',
        });
    }

    $('body').on('submit', '.form.user-locales-settings', function () {
        updateSelectedLocales();
    });
});
