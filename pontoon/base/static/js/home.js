/* Jquery plugin scrollify */
$(function() {
  $.scrollify({
		section:".snaps",
    scrollbars:false,
    interstitialSection: "",
    before: function(i,snaps) {
      var ref = snaps[i].attr("data-section-name");

      $(".pagination a.active").removeClass("active");

      $(".pagination a[href=#" + ref + "]").addClass("active");

    },
    after:function(i,snaps) {
      var ref = snaps[i].attr("data-section-name");
    },
    afterResize:initialPosition,
    afterRender:initialPosition
	});

  $(".pagination a").on("click",function() {
    $.scrollify.move($(this).attr("href"));
  });

  function initialPosition() {

    var current = $.scrollify.current();

  }
});
