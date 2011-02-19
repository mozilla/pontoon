$(function(){
  // Load project into iframe
  $('#address_button').click(function() {
      $('#source').attr('src', $('#address_input').val());
  });
  $('#address_button').click();
  
  $('#source').load(function() {
    if (!$(this).attr('src')) {
      return;
    }
    
    // remove any other existing pontoon client for GC
    if (Pontoon._clients.length) {
      Pontoon._clients = [];
   	}
    
    var doc = this.contentDocument,
        pc = new Pontoon.client(doc, document);
    turnOn(pc, doc);

    rebuildUIList(pc, doc);
  });
  
  $("#send").click(function () {
	  Pontoon._clients[0].send();
  });
})

function turnOn(pc, doc) {
  pc.enableEditing();
  $(".editableToolbar > .save", doc).click(function() {
    var editable = $($(this).parent().get()[0].target);
    //var html = this.contentWindow.document.body.innerHTML;
    pc.updateEntitiesFromElement(editable);
  })
}

/**
 * shorten an string
 */
function shorten(text, maxlen) {
  if (!maxlen) maxlen = 45;

  if (text.length <= maxlen) return text;
  return text.substr(0, maxlen-4)+new String(' ...');
}

function trim(str) {
  return str.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
}

function rebuildUIList(pc) {
  var ul = $(pc._ptn).find('#list');
  ul.empty();
  for (var i in pc._entities) {
    var entity = pc._entities[i];
    var str = entity.txtString;
    var li = $.create('li', {'children': shorten(str), 'root': pc._ptn});
    li.get()[0].entity = entity;
    li.hover(function() {
      this.entity.hover();
    },function() {
      this.entity.unhover();
    });
    li.click(function() {
      $(pc._doc).find('.editableToolbar > .edit').click();
    });
    entity.node.get()[0].entity = entity;
    entity.ui = li;
    ul.append(li);
  }
}
