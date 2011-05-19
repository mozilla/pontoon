// remap jQuery to $
(function($){

  // Inject HTML
  $('body').append(
    '<aside id="pontoon">'+

      '<header>'+
        '<span id="logo">Pontoon</span>'+
        '<span class="separator"></span>'+

        '<span id="flag" class="flag PL"></span>'+
        '<button class="button select" id="locale"><span class="language">Polski</span><span> &#9652;</span></button>'+
        '<ul id="locale-list">'+
          '<li><span class="flag DE"></span><span class="language">Deutsch</span></li>'+
          '<li><span class="flag FR"></span><span class="language">Français</span></li>'+
          '<li><span class="flag HR"></span><span class="language">Hrvatski</span></li>'+
          '<li><span class="flag PL"></span><span class="language">Polski</span></li>'+
          '<li><span class="flag SI"></span><span class="language">Slovenščina</span></li>'+
        '</ul>'+
        '<span class="separator"></span>'+

        '<div id="progress"><span></span></div>'+
        '<span id="progress-value"></span>'+

        '<button id="switch"></button>'+
        '<button class="button" id="send">Send</button>'+
      '</header>'+

      '<div id="entitylist"></div>'+
    '</aside>'
  );

  // Turn on Pontoon client
  Pontoon.init(document, document);

})(this.jQuery);
