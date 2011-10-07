(function () {

  var jqueryAppended = false,
    obj = document.createElement('script');;

  // Main code
  function jqueryLoaded() {
    $.noConflict();
    jQuery(document).ready(function($) {

      // Toolbar stylesheet
      var ss = $('<link rel="stylesheet" href="../../client/lib/css/editable.css">');
      $('head').append(ss);      

      // Context menu
      $('body')
        .attr("contextmenu", "context")
        .append(
        '<menu type="context" id="context">' +
          '<menuitem class="mode" label="Advanced mode" icon="../../client/lib/images/logo-small.png"></menuitem>' +
        '</menu>')
        .find("#context .mode").live("click", function() {
          $("#switch").click();
          if ($("#main").is(".opened")) {
            $(this).attr("label", "Basic mode");
          } else {
            $(this).attr("label", "Advanced mode");
          }
        });

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