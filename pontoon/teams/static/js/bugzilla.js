var Pontoon = (function (my) {
  return $.extend(true, my, {
    bugzilla: {

      /*
       * Retrieve bugs for the given locale and update bug count and tab content
       * using the provided elements and callbacks.
       * 
       * Heavily inspired by the similar functionality available in Elmo.
       * 
       * Source: https://github.com/mozilla/elmo/blob/master/apps/bugsy/static/bugsy/js/bugcount.js
       * Authors: Pike, peterbe, adngdb
       */
      getLocaleBugs: function (locale, container, tab, countCallback, errorCallback) {
        return $.ajax({
          url: 'https://bugzilla.mozilla.org/rest/bug',
          data: {
            'field0-0-0': 'component',
            'type0-0-0': 'regexp',
            'value0-0-0': '^' + locale + ' / ',
            'field0-0-1': 'cf_locale',
            'type0-0-1': 'regexp',
            'value0-0-1': '^' + locale + ' / ',
            'resolution': '---',
            'include_fields': 'id,summary,last_change_time,assigned_to'
          },
          success: function(data) {
            if (data.bugs.length) {
              data.bugs.sort(function(l, r) {
                return l.last_change_time < r.last_change_time ? 1 : -1;
              });

              var tbody = $('<tbody>'),
                  formatter = new Intl.DateTimeFormat('en-GB', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                  });

              $.each(data.bugs, function(i, bug) {
                // Prevent malicious bug summary from executin JS code
                var summary = Pontoon.doNotRender(bug.summary);

                var tr = $('<tr>', {
                  title: summary
                });

                $('<td>', {
                  class: 'id',
                  html: '<a href="https://bugzilla.mozilla.org/show_bug.cgi?id=' + bug.id + '">' + bug.id + '</a>'
                }).appendTo(tr);

                $('<td>', {
                  class: 'summary',
                  html: summary
                }).appendTo(tr);

                $('<td>', {
                  class: 'last-changed',
                  html: formatter.format(new Date(bug.last_change_time))
                }).appendTo(tr);

                $('<td>', {
                  class: 'assigned-to',
                  html: bug.assigned_to
                }).appendTo(tr);


                tbody.append(tr);
              });

              var table = $('<table>', {
                class: 'buglist striped',
                html: '<thead>' +
                  '<tr>' +
                    '<th class="id">ID</th>' +
                    '<th class="summary">Summary</th>' +
                    '<th class="last-changed">Last Changed</th>' +
                    '<th class="assigned-to">Assigned To</th>' +
                  '</tr>' +
                '</thead>'
              }).append(tbody);

              container.append(table.show());

              var count = data.bugs.length;
              countCallback(tab, count);

            } else {
              errorCallback('Zarro Boogs Found.');
            }
          },
           
          error: function(error) {
            if (error.status === 0 && error.statusText !== 'abort') {
              errorCallback('Oops, something went wrong. We were unable to load the bugs. Please try again later.');
            }
          }
        });
      }(),
      
       /*
       * Sort table
       */
      sort: function() {
        $('body').on('click', 'table.buglist tabel.striped th', function () { 
          function getID(el) {
            return $(el).find('.id').length;
          }

          function getSummary(el) {
            return $(el).find('.summary').length;
          }

          function getLastChanged(el) {
            return $(el).find('.last-changed"').length;
          }

          function getAssignedTo(el) {
            return $(el).find('.assigned-to"').length;
          }

          function getString(el) {
            return $(el).find('td:eq(' + index + ')').text();
          }

        var node = $(this),
        index = node.index(),
        table = node.parents('.table.buglist tabel.striped'),
        list = table.find('tbody'),
        items = list.find('tr'),
        dir = node.hasClass('asc') ? -1 : 1,
        cls = node.hasClass('asc') ? 'desc' : 'asc';

        $(table).find('th').removeClass('asc desc');
        node.addClass(cls);

        items.sort(function(a, b) {
          
          // Sort by assigned-to
          if (node.is('.assigned-to')) {
            return (getAssignedTo(a) - getAssignedTo(b)) * dir;
           
           // Sort by last-changed
          } else  if (node.is('.last-changed')) {
            return (getLastChanged(a) - getLastChanged(b)) * dir;

          // Sort by summary
          } else if (node.is('.summary')) {
            return (getSummary(a) - getSummary(b)) * dir;

            // Sort by id
          } else if (node.is('.id')) {
            return (getID(a) - getID(b)) * dir;

          // Sort by alphabetical order
          } else {
            return getString(a).localeCompare(getString(b)) * dir;
          }
        });

        list.append(items);
        });
      }()
    }
  });
}(Pontoon || {}));
