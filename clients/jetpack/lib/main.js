const host = "http://horv.at/p/"
const widgets = require("widget");
const tabs = require("tabs");

var widget = widgets.Widget({
  id: "pontoon-link",
  label: "Pontoon",
  contentURL: host + "client/www/favicon.ico",
  onClick: function() {
    tabs.open(host + "?url=" + tabs.activeTab.url);
  }
});