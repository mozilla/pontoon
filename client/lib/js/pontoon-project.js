(function () {

  var jqueryAppended = false,
    obj = document.createElement('script');;

  // Main code
  function jqueryLoaded() {
    $.noConflict();
    jQuery(document).ready(function($) {

      // Code that uses jQuery's $ can follow here.
      
    });
  }

  // Load jQuery if not loaded yet
  (function () {
    if (!window.jQuery) {
      if (!jqueryAppended) {
        obj.src = "//ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js";
        document.getElementsByTagName("body")[0].appendChild(obj);
        jqueryAppended = true;
        arguments.callee();
      } else {
        window.setTimeout(arguments.callee, 100);
  	  }
    } else {
      jqueryLoaded();
    }
  }());
  
})();