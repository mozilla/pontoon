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
            'include_fields': 'id,summary,creation_time,last_change_time'
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
                  class: 'date-created',
                  html: formatter.format(new Date(bug.creation_time))
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
                    '<th class="date-created">Date Created</th>' +
                  '</tr>' +
                '</thead>'
              }).append(tbody);

              container.append(table.show());

              var count = data.bugs.length;
              countCallback(tab, count);

            } else {
              contentCallback('Zarro Boogs Found.');
            }
          },
          error: function(error) {
            if (error.status === 0 && error.statusText !== 'abort') {
              contentCallback('Oops, something went wrong. We were unable to load the bugs. Please try again later.');
            }
          }
        });
      }

    }
  });
}(Pontoon || {}));
