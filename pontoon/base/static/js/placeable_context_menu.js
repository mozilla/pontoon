/*
PlaceableContextMenu is responsible for displaying context menu with suggestions
if entity contains any placeables.

User can invoke this context menu via ctrl+alt+p shortcut. Tab cycles betwen available
options.

Class has only an one dependency, `component.textarea-caret-position`.
*/

var PlaceableContextMenu = {
    open: function() {
      var self = this,
          placeables = $("#original .placeable"),
          items = $.map(placeables, function(item){
            return $(item).text();
          });

      if (items.length === 0 || self.isOpened()) {
        return;
      };

      self.render(items);
    },

    render: function(items) {
      var self = this,
          $menu = $('#placeableMenu');
          renderedItems = $.map(items, function(item) {
            return $('<li><a href="#">' + item + '</a></li>');
          }),
          $translation = $('#translation'),
          caretPos = getCaretCoordinates($translation[0], $translation.prop('selectionEnd')),
          translationPos = $translation.position(),
          menuPos = {
            top: translationPos.top + caretPos.top,
            left: translationPos.left + caretPos.left
          };

      $menu.html(renderedItems);

      $menu.find('a').click(function (ev) {
        ev.preventDefault();
        self.insertItem($(this).text());
      });

      $menu.css('top', menuPos.top);
      $menu.css('left', menuPos.left);
      $menu.addClass('opened');
      $menu.find('a:first').focus();
      $menu.find('a:first').parent().addClass('active');
    },

    close: function() {
      var self = this,
          $menu = $('#placeableMenu'),
          $translation = $('#translation');

      $menu.removeClass('opened');
      $menu.html('');
      self.itemIndex = 0;
    },

    isOpened: function() {
      var self = this;

      return $('#placeableMenu').is('.opened');
    },

    insertItem: function(item) {
      var self = this,
          $translation = $('#translation'),
          selectionStart = $translation.prop('selectionStart'),
          selectionEnd = $translation.prop('selectionEnd'),
          cursorPos = selectionStart + item.length,
          before = $translation.val(),
          after = before.substring(0, selectionStart) + item + before.substring(selectionEnd);

      $translation.val(after).focus();
      $translation[0].setSelectionRange(cursorPos, cursorPos);
      self.close();
    },

    focusOnNextItem: function() {
      var self = this,
          $items = $('#placeableMenu a');

      if (!$.isNumeric(self.itemIndex)) {
        self.itemIndex = 0;
      };

      if ((self.itemIndex || 0)+1 < $items.length) {
        self.itemIndex++;
      } else {
        self.itemIndex = 0;
      };

      var currentItem = $($items.get(self.itemIndex));

      $items.parent().removeClass('active');
      currentItem.parent().addClass('active');
      currentItem.focus();
    },
};

$(function() {
  $(window).keyup(function(ev) {
    // The context menu should be invoked when user presses ctrl+alt+p.
    if ($('#editor').is('.opened') && !PlaceableContextMenu.isOpened() && ev.ctrlKey && ev.altKey && ev.which == 80) {
      PlaceableContextMenu.open();
    };

    // Tab key should cause rotation between available items.
    if($('#editor').is('.opened') && PlaceableContextMenu.isOpened() && ev.which == 9) {
      ev.preventDefault();
      PlaceableContextMenu.focusOnNextItem();
    };
  });
});
