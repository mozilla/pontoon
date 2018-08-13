/* Jquery plugin scrollify */

$(function() {
  $.scrollify({
		section: ".snaps",
    scrollbars: false,
    interstitialSection: "",
    easing: "easeInOutSine",
    scrollSpeed: 975,
    before: function(i, snaps) {
      var ref = snaps[i].attr("id");

      $(".side-navigation li.active").removeClass("active");
      $(".side-navigation li[href=#" + ref + "]").addClass("active");
      $('body > header').css('background-color', '#272A2F');
    },
    after: function(i, snaps) {
      var ref = snaps[i].attr("id");

      if (ref === "section-6" || ref === "section-1") {
        $('body > header').css({
          'background-color': 'transparent',
          'transition-duration': '0.3s'
        });
      }
      else {
        $('body > header').css('background-color', '#272A2F');
      }
    },
    updateHash: false,
	});

  $(window).on('load', function() {
    setTimeout(function() {
      $(window).scrollTop(0);
    });
  });

  $(".side-navigation li").on("click", function() {
    $.scrollify.move($(this).attr("href"));
  });

  $("#section-1 .footer a").on("click", function(e) {
    e.preventDefault();
    $.scrollify.move("#section-2");
  });

  // Show/hide header border on menu open/close
  $('body > header').on('click', '.selector', function (e) {
    if (!$(this).siblings('.menu').is(':visible')) {
      $('body > header').addClass('menu-opened');
    }
  });
  $('body').bind('click.main', function () {
    $('body > header').removeClass('menu-opened');
  });
});

$.easing['easeInOutSine'] = function (x, t, b, c, d) {
  return -c/2 * (Math.cos(Math.PI*t/d) - 1) + b;
};
