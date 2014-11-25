(function () {
  /**
   * Patch TOC list.
   *
   * Will mutate the underlying span to have a correct ul for nav.
   *
   * @param $ul: Span containing nested UL's to mutate.
   * @param minLevel: Starting level for nested lists. (1: global, 2: local).
   */
  var patchToc = function ($ul, minLevel) {
    var findA;

    // Find all a "internal" tags, traversing recursively.
    findA = function ($elem, level) {
      var level = level || 0,
          $items = $elem.find("> li > a.internal, > ul, > li > ul");

      // Iterate everything in order.
      $items.each(function (index, item) {
        var $item = $(item),
            tag = item.tagName.toLowerCase(),
            pad = 15 + ((level - minLevel) * 10),
            curPad = parseInt($item.css('padding-left'));

        if (tag === 'a' && level >= minLevel) {
          // Add to existing padding.
          $item.css('padding-left', curPad + pad + "px");
        } else if (tag === 'ul') {
          // Recurse.
          findA($item, level + 1);
        }
      });
    };

    findA($ul);
  };

  $(function () {
    // Add styling, structure to TOC's.
    $(".dropdown-menu").each(function () {
      $(this).find("ul").each(function (index, item){
        var $item = $(item);
        $item.addClass('unstyled');
      });
      $(this).find("li").each(function () {
        $(this).parent().append(this);
      });
    });

    // Patch in level.
    patchToc($("ul.globaltoc"), 2);
    patchToc($("ul.localtoc"), 2);

    // Enable dropdown.
    $('.dropdown-toggle').dropdown();

    // Add Bootstrap classes to tables
    $('table.docutils').addClass('table').removeClass('docutils');
    $('table.footnote.table').removeClass('table');
  });
})();
