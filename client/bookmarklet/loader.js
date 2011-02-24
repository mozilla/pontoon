(function() {
  function inject_scripts() {
    for (var i=0; i < arguments.length; i++) {
      var script = document.createElement('script');
      script.type = 'text/javascript';
      script.src = arguments[i];
      document.getElementsByTagName('body')[0].appendChild(script);
    };
  }
  function inject_stylesheets() {
    for (var i=0; i < arguments.length; i++) {
      var stylesheet = document.createElement('link');
      stylesheet.rel = 'stylesheet';
      stylesheet.href = arguments[i];
      document.getElementsByTagName('head')[0].appendChild(stylesheet);
    };
  }

  inject_scripts(PontoonBookmarklet + 'client/lib/js/jquery-1.5.min.js'); /* https://ajax.googleapis.com/ajax/libs/jquery/1.5/jquery.min.js */

  /* TODO: This is terrible, use checks before executing code instead */
  setTimeout(function() {
    inject_scripts(PontoonBookmarklet + 'client/lib/js/jquery.editableText.js');
  }, 200);

  setTimeout(function() {
    inject_scripts(PontoonBookmarklet + 'client/lib/js/pontoon.js');
  }, 400);

  setTimeout(function() {
    inject_scripts(PontoonBookmarklet + 'client/bookmarklet/bookmarklet.js');
  }, 600);

  inject_stylesheets(PontoonBookmarklet + 'client/bookmarklet/bookmarklet.css');
  inject_stylesheets(PontoonBookmarklet + 'client/lib/css/pontoon.css');
  
  /* TODO: Remove. Already loaded in ib/pontoon.js. Dynamically set or use absolute path. */
  inject_stylesheets(PontoonBookmarklet + 'client/lib/css/editable.css');

})();
