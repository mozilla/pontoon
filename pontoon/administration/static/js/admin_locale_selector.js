$(function() {
  function setArrow(element, event) {
    var x = event.pageX - element.offset().left;

    if (element.outerWidth()/2 > x) {
      element.addClass('left');
    } else {
      element.removeClass('left');
    }
  }

  // Set translators arrow direction
  $('body')
    .on('mouseenter', '.locale.select.selected li', function (e) { setArrow($(this), e); })
    .on('mousemove', '.locale.select.selected li', function (e) { setArrow($(this), e); });

  /**
   * Function keeps track of inputs that contain informations abouyt the order of selected locales.
   */
  function updateSelectedLocales() {
    var $selectedList = $('.admin-locale-selector .locale.selected'),
        $selectedLocalesField = $selectedList.find('input[type=hidden]'),
        selectedLocales = $selectedList.find('li[data-id]').map(function() {
           return $(this).data('id');
        }).get();

    $selectedLocalesField.val(selectedLocales.join());
  }

  // Choose locales
  $('body').on('click', '.admin-locale-selector .locale.select li', function () {
    var ls = $(this).parents('.locale.select'),
        target = ls.siblings('.locale.select').find('ul'),
        item = $(this).remove();

    target.append(item);
    target.scrollTop(target[0].scrollHeight);
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

  if ($.ui && $.ui.sortable) {
    $('.admin-locale-selector .locale.select .sortable').sortable({
      axis: 'y',
      containment: 'parent',
      update: updateSelectedLocales,
      tolerance: 'pointer'
    });
  }

  $('body').on('submit', '.form.user-locales-settings', function () {
    updateSelectedLocales();
  });
});
