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

      if (ref === "section-1")
        $('.home-header').css({'background-color':'transparent','transition-duration':'0.3s'})
      else
        $('.home-header').css('background-color','#272A2F')
    },
    after: function(i,snaps) {
      var ref = snaps[i].attr("data-section-name");

      if (ref === "section-6" || ref === "section-1")
        $('.home-header').css({'background-color':'transparent','transition-duration':'0.3s'})
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
