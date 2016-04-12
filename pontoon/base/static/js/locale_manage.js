$(function() {

  // Before submitting the form, update translators and managers
  $('form').submit(function (e) {
    $.each(['translators', 'managers'], function(i, value) {
      var data = $('.user.' + value + ' li').map(function() {
        return $(this).data('id');
      }).get();
      $('[name="' + this + '"]').val(data);
    });
  });

  // Switch available users
  $('.user.available label a').click(function(e) {
    e.preventDefault();

    $(this).addClass('active').siblings('a').removeClass('active');
    $('.user.available li').show();

    if ($(this).is('.contributors')) {
      $('.user.available li:not(".contributor")').hide();
    }

    $('#available').trigger('input').focus();
  });

  // While in contributors tab, search contributors only
  $('.menu input[type=search]').on('input.search', function(e) {
    if ($('.user.available label a.contributors').is('.active')) {
      $('.user.available li:not(".contributor")').hide();
    }
  });

  // Set translators arrow direction
  function setArrow(element, event) {
    var x = event.pageX - element.offset().left;
    if (element.outerWidth()/2 > x) {
      element.addClass('left');
    } else {
      element.removeClass('left');
    }
  }
  $('.user.select.translators')
    .on('mouseenter', 'li', function (e) { setArrow($(this), e); })
    .on('mousemove', 'li', function (e) { setArrow($(this), e); });

  // Select users
  $('.select').on('click.pontoon', 'li', function (e) {
    var target = $('.select.translators');

    if ($(this).parents('.translators').length) {
      if ($(this).is('.left')) {
        target = $('.select.available');
      } else {
        target = $('.select.managers');
      }
    }

    var clone = $(this).remove();

    target.find('ul').prepend(clone.removeClass('hover'));
    $('#available').trigger('input').focus();
  });

});
