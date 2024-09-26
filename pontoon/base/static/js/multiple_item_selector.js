// Controls behaviour of multiple item selector widget.
$(function () {
  /**
   * Function keeps track of inputs that contain information about the order of selected items.
   */
  function updateSelectedItems(element) {
    const widget = $(element).parents('.multiple-item-selector');
    const selectElement = widget.find('select');
    const selectedItems = widget
      .find('.item.selected li[data-id]')
      .map(function () {
        return $(this).data('id');
      })
      .get();

    for (const option of selectElement[0].options) {
      option.selected = selectedItems.includes(parseInt(option.value));
    }
  }

  // Choose items
  $('body').on('click', '.multiple-item-selector .item.select li', function () {
    const ls = $(this).parents('.item.select'),
      target = ls.siblings('.item.select').find('ul'),
      item = $(this).remove();

    target.append(item);
    target.scrollTop(target[0].scrollHeight);
    updateSelectedItems(this);
  });

  // Choose/remove all items
  $('body').on('click', '.multiple-item-selector .move-all', function (e) {
    e.preventDefault();
    const ls = $(this).parents('.item.select'),
      target = ls.siblings('.item.select').find('ul'),
      items = ls.find('li:visible:not(".no-match")').remove();

    target.append(items);
    target.scrollTop(target[0].scrollHeight);
    updateSelectedItems(this);
  });

  if ($.ui && $.ui.sortable) {
    $('.multiple-item-selector .item.select .sortable').sortable({
      axis: 'y',
      containment: 'parent',
      update: updateSelectedItems,
      tolerance: 'pointer',
    });
  }
});
