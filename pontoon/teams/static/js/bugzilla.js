const Pontoon = ((my => $.extend(true, my, {
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
    //modification by Okpo starts here
    //current fields on pontoon are: ID, SUMMARY, LAST CHANGED, DATE CREATED
    // add ASSIGNEE and STATUS to the current list of bugs....
    getLocaleBugs(locale, container, tab, countCallback, errorCallback) {
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
          'include_fields': 'id,summary,creation_time,last_change_time,assignee,status'
        },
        success(data) {
          if (data.bugs.length) {
            data.bugs.sort((l, r) => l.last_change_time < r.last_change_time ? 1 : -1);

            const tbody = $('<tbody>'),
                  formatter = new Intl.DateTimeFormat('en-GB', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                  });

            $.each(data.bugs, (i, bug) => {
              // Prevent malicious bug summary from executin JS code
              const summary = Pontoon.doNotRender(bug.summary);

              const tr = $('<tr>', {
                title: summary
              });

              $('<td>', {
                class: 'id',
                html: `<a href="https://bugzilla.mozilla.org/show_bug.cgi?id=${bug.id}">${bug.id}</a>`
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
            // add assignee and status
              $('<td>', {
                class: 'assignee',
                html: formatter.format(new Date(bug.assignee))
              }).appendTo(tr);

              $('<td>', {
                class: 'status',
                html: formatter.format(new Date(bug.status))
              }).appendTo(tr);

              tbody.append(tr);
            });

            const table = $('<table>', {
              class: 'buglist striped',
              html: '<thead>' +
                '<tr>' +
                  '<th class="id">ID</th>' +
                  '<th class="summary">Summary</th>' +
                  '<th class="last-changed">Last Changed</th>' +
                  '<th class="date-created">Date Created</th>' +
                  '<th class="assignee">Assignee</th>' +
                  '<th class="status">Status</th>' +
                '</tr>' +
              '</thead>'
            }).append(tbody);

            container.append(table.show());

            const count = data.bugs.length;
            countCallback(tab, count);

          } else {
            errorCallback('Zarro Boogs Found.');
          }
        },
        error(error) {
          if (error.status === 0 && error.statusText !== 'abort') {
            errorCallback('Oops, something went wrong. We were unable to load the bugs. Please try again later.');
          }
        }
      });
    }

  }
}))(Pontoon || {}));