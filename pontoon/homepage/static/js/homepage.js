/*
 * fullPage plugin by Alvaro Trigo
 * URL: https://github.com/alvarotrigo/fullPage.js/
 */
new fullpage('#main', {
  licenseKey: 'OPEN-SOURCE-GPLV3-LICENSE',
  navigation: true,
  navigationPosition: 'left',
  onLeave: function(origin, destination, direction) {
    $('body > header').css('background-color', '#272A2F');
  },
  afterLoad: function(origin, destination, direction) {
    color = '#272A2F';
    if (destination.item.id === 'section-1' || destination.item.id === 'section-6') {
      color = 'transparent';
    }
    $('body > header').css('background-color', color);
  },
});

$(function() {
  // Scroll from Section 1 to Section 2
  $('#section-1 .footer .scroll').on('click', function(e) {
    e.preventDefault();
    fullpage_api.moveSectionDown();
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
