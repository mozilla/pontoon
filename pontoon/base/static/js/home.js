$(function() {

  // Update project if already set
  var url = $('#server').data('url');
  if (url) {
    $('.project-url:contains("' + url + '")').parents('li').click();
  }

  // Update locale if already set
  var locale = $('#server').data('locale');
  if (locale) {
    locale = locale.toLowerCase();
    $('.locale .language.' + locale).parents('li').click();
  }

  $('#project-load').hide();
  $('#intro').css('display', 'table').hide().fadeIn();

  // Authentication and profile menu
  $("#browserid").click(function(e) {
    $('#loading').toggleClass('loader').html('&nbsp;');
    e.preventDefault();
    navigator.id.get(function(assertion) {
      if (assertion) {
        $.ajax({
          url: 'browserid/',
          type: 'POST',
          data: {
            assertion: assertion,
            csrfmiddlewaretoken: $('#server').data('csrf')
          },
          success: function(data) {
            if (data !== 'error') {
              $('#action').remove();
              $('#signout').removeClass('hidden').find('a').attr('title', data.browserid.email);
              if (data.manager) {
                $('#admin').removeClass('hidden');
              }
              $('form').removeClass('hidden');
              $('.notification').addClass('hidden');
            } else {
              $('.notification').html('<li>Oops, something went wrong.</li>').removeClass('hidden');
              $('#loading').toggleClass('loader').html('or');
            }
          },
          error: function() {
            $('.notification').html('<li>Oops, something went wrong.</li>').removeClass('hidden');
            $('#loading').toggleClass('loader').html('or');
          }
        });
      } else {
        $('#loading').toggleClass('loader').html('or');
      }
    });
  });

});
