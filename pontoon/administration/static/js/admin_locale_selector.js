$(function() {
  /*
   * Function keeps track of inputs that contain information about the order of selected locales.
   */
  function updateSelectedLocales() {
    var $selectedList = $('.admin-locale-selector .locale.selected'),
        $selectedLocalesField = $selectedList.find('input[type=hidden]'),
        selectedLocales = $selectedList.find('li[data-id]').map(function() {
           return $(this).data('id');
        }).get();

    $selectedLocalesField.val(selectedLocales.join());
  }

  function setArrow(element, event) {
    var x = event.pageX - element.offset().left;

    if (element.outerWidth()/2 > x) {
      element.addClass('left');
    } else {
      element.removeClass('left');
    }
  }

  // Set arrow direction in the middle list
  $('body')
    .on('mouseenter', '.locale.select.selected li', function (e) { setArrow($(this), e); })
    .on('mousemove', '.locale.select.selected li', function (e) { setArrow($(this), e); });

  // Select locales
  $('body').on('click.pontoon', '.admin-locale-selector .select li', function () {
    var $wrapper = $(this).parents('.select').parent();
    var target = $wrapper.find('.select.selected');

    if ($(this).parents('.selected').length) {
      if ($(this).is('.left')) {
        target = $wrapper.find('.select.available');
      }
      else {
        target = $wrapper.find('.select.readonly');
      }
    }

    var clone = $(this).remove();
    var $ul = target.find('ul');
    $ul.append(clone.removeClass('hover'));

    $ul.scrollTop($ul[0].scrollHeight);
    updateSelectedLocales();
  });

  // Choose/remove all locales
  $('body').on('click', '.admin-locale-selector .choose-all, .admin-locale-selector .remove-all', function (e) {
    e.preventDefault();
    var ls = $(this).parents('.locale.select'),
        target = ls.siblings('.locale.select').find('ul'),
        items = ls.find('li:visible:not(".no-match")').remove();

    target.append(items);
    target.scrollTop(target[0].scrollHeight);
    updateSelectedLocales();
  });

  $('body').on('submit', '.form.user-locales-settings', function () {
    updateSelectedLocales();
  });
});
