$(function () {
    $('.locale-selector .locale .menu li:not(".no-match")').click(function () {
        $(this)
            .parents('.locale-selector')
            .find('.locale .selector')
            .html($(this).html());
    });
});
