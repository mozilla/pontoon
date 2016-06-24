// Contains behaviours of widgets that are shared between admin and end-user interface.
;$(function() {
  /**
   * Function keeps track of inputs that contain informations abouyt the order of selected locales.
   */
  function updateSelectedLocales() {
    var $selectedList = $('.locale.selected'),
        $selectedLocalesField = $selectedList.find('input[type=hidden]'),
        selectedLocalesLength = $selectedList.find('li[data-id]').length,
        selectedLocales = $selectedList.find('li[data-id]').map(function(index) {
           return $(this).data('id');
        }).get();

    $selectedLocalesField.val(selectedLocales.join());
  };

  // Choose locales
  $('.locale.select').on('click.pontoon', 'li', function (e) {
    var target = $(this).parents('.locale.select').siblings('.locale.select').find('ul'),
        clone = $(this).remove();
    target.prepend(clone);
    updateSelectedLocales();
  });

  // Choose/remove all locales
  $('.choose-all, .remove-all').click(function (e) {
    e.preventDefault();
    var ls = $(this).parents('.locale.select'),
        target = ls.siblings('.locale.select').find('ul'),
        items = ls.find('li:visible:not(".no-match")').remove();
    target.prepend(items);
    updateSelectedLocales();
  });

  $('.locale.select .sortable').sortable({
    axis: 'y',
    containment: 'parent',
    update: updateSelectedLocales,
    tolerance: 'pointer'
  });

  $('form.user-locales-settings').submit(function(ev) {
    updateSelectedLocales();
  });
});
