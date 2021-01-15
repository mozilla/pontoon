$(function () {
    $('#main').fullpage({
        navigation: true,
        navigationPosition: 'left',
    });

    // Scroll from Section 1 to Section 2
    $('#section-1 .footer .scroll').on('click', function (e) {
        e.preventDefault();
        $.fn.fullpage.moveSectionDown();
    });

    // Show/hide header border on menu open/close
    $('body > header').on('click', '.selector', function () {
        if (!$(this).siblings('.menu').is(':visible')) {
            $('body > header').addClass('menu-opened');
        }
    });
    $('body').bind('click.main', function () {
        $('body > header').removeClass('menu-opened');
    });
});
