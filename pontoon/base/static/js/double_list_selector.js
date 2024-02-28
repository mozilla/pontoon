/* A 3-column selector to select two lists */
$(function () {
  function getTarget(item) {
    const list = $(item).parents('.select');
    let target = list.siblings('.select:nth-child(2)');

    if (list.is('.select:nth-child(2)')) {
      if ($(item).is('.left') || list.siblings().length === 1) {
        target = list.siblings('.select:first-child');
      } else {
        target = list.siblings('.select:last-child');
      }
    }

    return target;
  }

  function setArrow(element, event) {
    const x = event.pageX - element.offset().left;

    if (element.outerWidth() / 2 > x) {
      element.addClass('left');
    } else {
      element.removeClass('left');
    }
  }

  // Set translators arrow direction
  $('body')
    .on(
      'mouseenter',
      '.double-list-selector .select:nth-child(2) li',
      function (e) {
        setArrow($(this), e);
      },
    )
    .on(
      'mousemove',
      '.double-list-selector .select:nth-child(2) li',
      function (e) {
        setArrow($(this), e);
      },
    );

  // Move items between lists
  const mainSelector = '.double-list-selector';
  const itemSelector = mainSelector + ' .select li';
  const allSelector = mainSelector + ' .move-all';
  $('body').on('click', [itemSelector, allSelector].join(', '), function (e) {
    e.preventDefault();

    const target = getTarget(this);
    const ul = target.find('ul');
    let clone = null;

    // Move selected item
    if ($(this).is('li')) {
      clone = $(this).remove();
    }
    // Move all items in the list
    else {
      clone = $(this)
        .parents('.select')
        .find('li:visible:not(".no-match")')
        .remove();
    }

    ul.append(clone.removeClass('hover'));
    ul.scrollTop(ul[0].scrollHeight);

    $('.double-list-selector .select:first-child').trigger('input').focus();
  });
});
