$(function() {

  // Translate selected project
  $('.project .menu li').click(function (e) {
    e.preventDefault();
    window.location = $('#server')
      .data('locale') + '/' + $(this).find('.name').data('slug');
  });

});
