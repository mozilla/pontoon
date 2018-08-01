/* Jquery plugin scrollify */

$(function() {
  $.scrollify({
		section:".snaps",
    scrollbars:false,
    interstitialSection: "",
    easing: "easeInOutSine",
    scrollSpeed: 975,
    before: function(i,snaps) {
      var ref = snaps[i].attr("data-section-name");

      $(".pagination.active").removeClass("active");

      $(".pagination[href=#" + ref + "]").addClass("active");

      $('.home-header').css('background-color','#272A2F')
    },
    after: function(i,snaps) {
      var ref = snaps[i].attr("data-section-name");

      if (ref === "section-6")
        $('.home-header').css({'background-color':'transparent','transition-duration':'0.3s'})
      else if (ref === "section-1")
        $('.home-header').css({'background-color':'transparent','transition-duration':'0.3s'})
      else
        $('.home-header').css('background-color','#272A2F')
    },
    updateHash: false,
	});

  $(window).on('load', function() {
    setTimeout(function() {
      $(window).scrollTop(0);
    });
  });

  $(".pagination").on("click",function() {
    $.scrollify.move($(this).attr("href"));
  });

  $(".section1-footer").on("click",function(){
    $.scrollify.move("#section-2");
  });
});

$.easing['easeInOutCubic'] = function (x, t, b, c, d) {
  return (t/=d/2) < 1 ? c/2*t*t*t + b : c/2*((t-=2)*t*t + 2) + b;
};

$.easing['easeInOutSine'] = function (x, t, b, c, d) {
  return -c/2 * (Math.cos(Math.PI*t/d) - 1) + b;
};
