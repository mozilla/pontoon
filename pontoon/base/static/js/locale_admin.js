$(function() {

  // Before submitting the form, update selected users
  $('form').submit(function (e) {
    var selected = $('.user.selected li').map(function() {
      return $(this).data('id');
    }).get();
    $('[name="users-selected"]').val(selected);
  });

  // Switch available users
  $('.user.available label a').click(function(e) {
    e.preventDefault();

    $(this).addClass('active').siblings('a').removeClass('active');
    $('.user.available li').show();

    if ($(this).is('.contributors')) {
      $('.user.available li:not(".contributor")').hide();
    }

    $('#available').trigger("keyup").focus();
  });

  // While in contributors tab, search contributors only
  $('.menu input[type=search]').on('keyup.search', function(e) {
    if ($('.user.available label a.contributors').is('.active')) {
      $('.user.available li:not(".contributor")').hide();
    }
  });

  // Select users
  $('.user.select').on('click.pontoon', 'li', function (e) {
    var target = $(this).parents('.select').siblings('.select').find('ul'),
        clone = $(this).remove();

    target.prepend(clone.removeClass('hover'));
    $('#available').trigger("keyup").focus();
  });

  // Remove all users
  $('.remove-all').click(function (e) {
    e.preventDefault();

    $('.selected li').click();
  });

});
