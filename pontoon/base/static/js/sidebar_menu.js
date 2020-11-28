/* Sidebar with left column acting as menu and right column as panel do display content */
$(function () {
    $('body').on('click', '.menu.left-column > ul > li > a', function (e) {
        e.preventDefault();

        $(this)
            .parents('li')
            .addClass('selected')
            .siblings()
            .removeClass('selected');

        $($(this).data('target')).show().siblings().hide();
    });
});
