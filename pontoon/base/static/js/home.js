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
    updateHash: false,
	});

  $(".pagination").on("click",function() {
    $.scrollify.move($(this).attr("href"));
  });

  $(".section1-footer").on("click",function(){
    $.scrollify.move("#section-2");
  });
});
