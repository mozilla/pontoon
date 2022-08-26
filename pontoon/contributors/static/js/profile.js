const nf = new Intl.NumberFormat('en', {
  style: 'percent',
});

const monthNameFormat = new Intl.DateTimeFormat('en-US', {
  month: 'short',
});

const shortDateFormat = new Intl.DateTimeFormat('en-US', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
});

var Pontoon = (function (my) {
  return $.extend(true, my, {
    insights: {
      renderCharts: function () {
        var approvalRateChart = $('#approval-rate-chart');
        Pontoon.insights.renderRateChart(
          approvalRateChart,
          approvalRateChart.data('approval-rates'),
          approvalRateChart.data('approval-rates-12-month-avg'),
        );

        var selfApprovalRateChart = $('#self-approval-rate-chart');
        Pontoon.insights.renderRateChart(
          selfApprovalRateChart,
          selfApprovalRateChart.data('self-approval-rates'),
          selfApprovalRateChart.data('self-approval-rates-12-month-avg'),
        );
      },
      renderRateChart: function (chart, data1, data2) {
        if (chart.length === 0) {
          return;
        }
        var ctx = chart[0].getContext('2d');

        var gradient = ctx.createLinearGradient(0, 0, 0, 160);
        gradient.addColorStop(0, '#7BC87633');
        gradient.addColorStop(1, 'transparent');

        new Chart(chart, {
          type: 'bar',
          data: {
            labels: $('#insights').data('dates'),
            datasets: [
              {
                type: 'line',
                label: 'Current month',
                data: data1,
                backgroundColor: gradient,
                borderColor: ['#41554c'],
                borderWidth: 2,
                pointBackgroundColor: '#41554c',
                pointHitRadius: 10,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#41554c',
                pointHoverBorderColor: '#FFF',
                order: 2,
              },
              {
                type: 'line',
                label: '12-month average',
                data: data2,
                borderColor: ['#7BC876'],
                borderWidth: 1,
                pointBackgroundColor: '#7BC876',
                pointHitRadius: 10,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#7BC876',
                pointHoverBorderColor: '#FFF',
                order: 1,
              },
            ],
          },
          options: {
            legend: {
              display: false,
            },
            tooltips: {
              mode: 'index',
              intersect: false,
              borderColor: '#7BC876',
              borderWidth: 1,
              caretPadding: 5,
              xPadding: 10,
              yPadding: 10,
              callbacks: {
                label: function (items, chart) {
                  const label = chart.datasets[items.datasetIndex].label;
                  const value = nf.format(items.yLabel / 100);

                  return `${label}: ${value}`;
                },
              },
            },
            scales: {
              xAxes: [
                {
                  type: 'time',
                  time: {
                    displayFormats: {
                      month: 'MMM',
                    },
                    tooltipFormat: 'MMMM YYYY',
                  },
                  gridLines: {
                    display: false,
                  },
                  offset: true,
                  ticks: {
                    source: 'data',
                  },
                },
              ],
              yAxes: [
                {
                  gridLines: {
                    display: false,
                  },
                  position: 'right',
                  ticks: {
                    beginAtZero: true,
                    maxTicksLimit: 3,
                    max: 100,
                    precision: 0,
                    callback: (value) => nf.format(value / 100),
                  },
                },
              ],
            },
          },
        });
      },
    },
    profile: {
      /*
       * This method is heavily inspired by the Github-Contribution-Graph,
       * authored by bachvtuan.
       *
       * @see {@link https://github.com/bachvtuan/Github-Contribution-Graph}
       */
      renderContributionGraph: function () {
        const graph = $('#contribution-graph');
        const contributions = graph.data('contributions');

        // Set start date to 365 days before now
        let startDate = new Date();
        startDate.setMonth(startDate.getMonth() - 12);
        startDate.setUTCDate(startDate.getUTCDate() + 1);
        startDate.setUTCHours(0, 0, 0, 0);
        const endDate = new Date();

        let graphHTML = '';
        const step = 13;

        let monthPosition = [{ monthIndex: startDate.getMonth(), x: 0 }];
        let usingMonth = startDate.getMonth();

        let week = 0;
        let gx = week * step;
        let weekHTML = `<g transform="translate(${gx.toString()}, 0)">`;

        while (startDate.getTime() <= endDate.getTime()) {
          if (startDate.getDay() == 0) {
            weekHTML = `<g transform="translate(${gx.toString()}, 0)">`;
          }

          const monthInDay = startDate.getMonth();

          if (startDate.getDay() == 0 && monthInDay != usingMonth) {
            usingMonth = monthInDay;
            monthPosition.push({ monthIndex: usingMonth, x: gx });
          }

          const count = contributions[startDate.getTime()] || 0;

          // Pick color based on count range
          let color;
          switch (true) {
            case count === 0:
              color = '#333941';
              break;
            case count < 10:
              color = '#41554c';
              break;
            case count < 25:
              color = '#4f7256';
              break;
            case count < 50:
              color = '#64906D';
              break;
            default:
              color = '#7bc876';
          }

          const y = startDate.getDay() * step;
          const date = startDate.getTime();
          weekHTML += `<rect class="day" width="10" height="10" y="${y}" fill="${color}" data-count="${count}" data-date="${date}" rx="2" ry="2"/>`;

          if (startDate.getDay() == 6) {
            weekHTML += '</g>';
            graphHTML += weekHTML;
            weekHTML = null;
            week++;
            gx = week * step;
          }

          startDate.setUTCDate(startDate.getUTCDate() + 1);
        }

        // Add week items
        if (weekHTML != null) {
          weekHTML += '</g>';
          graphHTML += weekHTML;
        }

        // Remove the first incomplete month label
        if (monthPosition[1].x - monthPosition[0].x < 40) {
          monthPosition.shift(0);
        }

        // Add month labels
        for (let x = 0; x < monthPosition.length; x++) {
          const item = monthPosition[x];
          const monthName = monthNameFormat.format(
            new Date(2022, item.monthIndex),
          );
          graphHTML += `<text x="${item.x}" y="-5" class="month">${monthName}</text>`;
        }

        // Add day labels
        graphHTML += `
            <text text-anchor="middle" class="wday" dx="695" dy="22">M</text>
            <text text-anchor="middle" class="wday" dx="695" dy="48">W</text>
            <text text-anchor="middle" class="wday" dx="695" dy="74">F</text>`;

        graph.html(`
            <svg width="690" height="110" viewBox="0 0 702 110" class="js-calendar-graph-svg">
              <g transform="translate(0, 20)">${graphHTML}</g>
            </svg>`);

        // Handle tooltip
        $(graph)
          .find('.day')
          .hover(
            function (e) {
              const count = $(e.target).attr('data-count');
              const date = shortDateFormat.format(
                $(e.target).attr('data-date'),
              );
              const action = count == 1 ? 'contribution' : 'contributions';
              const text = `${count} ${action} on ${date}`;

              const tooltip = $('.svg-tip').show();
              tooltip.html(text);

              const offset = $(e.target).offset();
              const width = Math.round(tooltip.width() / 2 + 5);
              const height = tooltip.height() * 2 + 10;
              tooltip.css({ top: offset.top - height - 5 });
              tooltip.css({ left: offset.left - width });
            },
            function () {
              $('.svg-tip').hide();
            },
          );
      },
      handleContributionTypeSelector: function () {
        $('#contributions .type-selector .menu li').click(function () {
          $(this)
            .parents('.type-selector')
            .find('.selector .value')
            .html($(this).html());

          const type = $('#contributions .type-selector span').data('type');
          const user = $('#server').data('user');

          $.ajax({
            url: '/update-contribution-graph/',
            data: {
              contribution_type: type,
              user: user,
            },
            success: function (data) {
              const contributions = JSON.parse(data.contributions);
              $('#contribution-graph').data('contributions', contributions);
              $('#contributions .title').html(data.title);
              Pontoon.profile.renderContributionGraph();
            },
            error: function () {
              Pontoon.endLoader('Oops, something went wrong.', 'error');
            },
          });
        });
      },
    },
  });
})(Pontoon || {});

/* Main code */
Pontoon.insights.initialize();
Pontoon.insights.renderCharts();

Pontoon.profile.renderContributionGraph();
Pontoon.profile.handleContributionTypeSelector();
