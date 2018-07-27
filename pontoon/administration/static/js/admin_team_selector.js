$(function() {
  function setArrow(element, event) {
    var x = event.pageX - element.offset().left;

    if (element.outerWidth()/2 > x) {
      element.addClass('left');
    } else {
      element.removeClass('left');
    }
  }

  function getTarget(item) {
    var list = $(item).parents('.select');
    var target = list.siblings('.select.selected');

    if (list.is('.selected')) {
      if ($(item).is('.left')) {
        target = list.siblings('.select.available');
      }
      else {
        target = list.siblings('.select.readonly');
      }
    }

    return target;
  }

  // Set arrow direction in the middle list
  $('body')
    .on('mouseenter', '.locale.select.selected li', function (e) { setArrow($(this), e); })
    .on('mousemove', '.locale.select.selected li', function (e) { setArrow($(this), e); });

  // Move items between lists
  var mainSelector = '.admin-locale-selector';
  var itemSelector = mainSelector + ' .select li';
  var allSelector = mainSelector + ' .move-all';
  $('body').on('click.pontoon', [itemSelector, allSelector].join(', '), function (e) {
    e.preventDefault();

    var target = getTarget(this);
    var ul = target.find('ul');

    // Move selected item
    if ($(this).is('li')) {
      var clone = $(this).remove();
    }
    // Move all items in the list
    else {
      var clone = $(this).parents('.select').find('li:visible:not(".no-match")').remove();
    }

    ul.append(clone.removeClass('hover'));
    ul.scrollTop(ul[0].scrollHeight);
  });
});
