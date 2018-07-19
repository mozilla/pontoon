/* Jquery plugin scrollify */
$(function() {
  $.scrollify({
		section:".snaps",
    scrollbars:false,
    interstitialSection: "",
    before: function(i,snaps) {
      var ref = snaps[i].attr("data-section-name");

      $(".pagination.active").removeClass("active");

      $(".pagination[href=#" + ref + "]").addClass("active");
      if (ref === "section-1" || ref === "section-6")
        $('.home-header').css('background-color','transparent')
      else
        $('.home-header').css('background-color','#272A2F')

    },
    after:function(i,snaps) {
      var ref = snaps[i].attr("data-section-name");
    },
    afterResize:initialPosition,
    afterRender:initialPosition
	});

  $(".pagination").on("click",function() {
    $.scrollify.move($(this).attr("href"));
  });

  function initialPosition() {

    var current = $.scrollify.current();

  }
});
