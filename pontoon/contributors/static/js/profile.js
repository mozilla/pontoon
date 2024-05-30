const nf = new Intl.NumberFormat('en', {
  style: 'percent',
});

const monthNameFormat = new Intl.DateTimeFormat('en-US', {
  month: 'short',
});

const shortDateFormat = new Intl.DateTimeFormat('en-US', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
});

const style = getComputedStyle(document.body);

// eslint-disable-next-line no-var
var Pontoon = (function (my) {
  return $.extend(true, my, {
    insights: {
      renderCharts: function () {
        const approvalRateChart = $('#approval-rate-chart');
        Pontoon.insights.renderRateChart(
          approvalRateChart,
          approvalRateChart.data('approval-rates'),
          approvalRateChart.data('approval-rates-12-month-avg'),
        );

        const selfApprovalRateChart = $('#self-approval-rate-chart');
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
        const ctx = chart[0].getContext('2d');

        const gradient = ctx.createLinearGradient(0, 0, 0, 160);
        gradient.addColorStop(0, style.getPropertyValue('--dark-green'));
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
                borderColor: [style.getPropertyValue('--forest-green-1')],
                borderWidth: 2,
                pointBackgroundColor:
                  style.getPropertyValue('--forest-green-1'),
                pointHitRadius: 10,
                pointRadius: 3.25,
                pointHoverRadius: 6,
                pointHoverBackgroundColor:
                  style.getPropertyValue('--forest-green-1'),
                pointHoverBorderColor: style.getPropertyValue('--white-1'),
                order: 2,
                fill: true,
                tension: 0.4,
              },
              {
                type: 'line',
                label: '12-month average',
                data: data2,
                borderColor: [style.getPropertyValue('--status-translated')],
                borderWidth: 1,
                pointBackgroundColor: style.getPropertyValue(
                  '--status-translated',
                ),
                pointHitRadius: 10,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: style.getPropertyValue(
                  '--status-translated',
                ),
                pointHoverBorderColor: style.getPropertyValue('--white-1'),
                order: 1,
                fill: true,
                tension: 0.4,
              },
            ],
          },
          options: {
            clip: false,
            plugins: {
              tooltip: {
                mode: 'index',
                intersect: false,
                borderColor: style.getPropertyValue('--status-translated'),
                borderWidth: 1,
                caretPadding: 5,
                padding: {
                  x: 10,
                  y: 10,
                },
                callbacks: {
                  labelColor: this.setLabelValue,
                  label: function (context) {
                    const { parsed, chart, datasetIndex } = context;
                    const label = chart.data.datasets[datasetIndex].label;
                    const value = nf.format(parsed.y / 100);

                    return `${label}: ${value}`;
                  },
                },
              },
            },
            scales: {
              x: {
                type: 'time',
                time: {
                  displayFormats: {
                    month: 'MMM',
                  },
                  tooltipFormat: 'MMMM yyyy',
                },
                grid: {
                  display: false,
                },
                offset: true,
                ticks: {
                  source: 'data',
                },
              },
              y: {
                grid: {
                  display: false,
                },
                position: 'right',
                ticks: {
                  maxTicksLimit: 3,
                  precision: 0,
                  callback: (value) => nf.format(value / 100),
                },
                beginAtZero: true,
                max: 100,
              },
            },
          },
        });
      },
      setLabelValue: function (context) {
        return {
          borderColor: style.getPropertyValue('--tooltip-color'),
          backgroundColor:
            context.dataset.hoverBackgroundColor ||
            context.dataset.pointBackgroundColor,
          borderWidth: 0.3,
        };
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
        const startDate = new Date();
        startDate.setMonth(startDate.getMonth() - 12);
        startDate.setUTCDate(startDate.getUTCDate() + 1);
        startDate.setUTCHours(0, 0, 0, 0);
        const endDate = new Date();

        let graphHTML = '';
        const step = 13;

        const currentDate = startDate;
        let currentMonth = currentDate.getMonth();
        const monthPosition = [{ monthIndex: currentMonth, x: 0 }];

        let week = 0;
        let gx = week * step;
        let weekHTML = `<g transform="translate(${gx.toString()}, 0)">`;

        while (currentDate.getTime() <= endDate.getTime()) {
          if (currentDate.getDay() == 0) {
            weekHTML = `<g transform="translate(${gx.toString()}, 0)">`;
          }

          const monthOfTheDay = currentDate.getMonth();

          if (currentDate.getDay() == 0 && monthOfTheDay != currentMonth) {
            currentMonth = monthOfTheDay;
            monthPosition.push({ monthIndex: currentMonth, x: gx });
          }

          const count = contributions[currentDate.getTime()] || 0;

          // Pick color based on count range
          let color;
          switch (true) {
            case count === 0:
              color = style.getPropertyValue('--dark-grey-1');
              break;
            case count < 10:
              color = style.getPropertyValue('--forest-green-1');
              break;
            case count < 25:
              color = style.getPropertyValue('--green');
              break;
            case count < 50:
              color = style.getPropertyValue('--green-2');
              break;
            default:
              color = style.getPropertyValue('--status-translated');
          }

          const y = currentDate.getDay() * step;
          const date = currentDate.getTime();
          weekHTML += `<rect class="day" width="10" height="10" y="${y}" fill="${color}" data-count="${count}" data-date="${date}" rx="2" ry="2"/>`;

          if (currentDate.getDay() == 6) {
            weekHTML += '</g>';
            graphHTML += weekHTML;
            weekHTML = null;
            week++;
            gx = week * step;
          }

          currentDate.setUTCDate(currentDate.getUTCDate() + 1);
        }

        // Add week items
        if (weekHTML != null) {
          weekHTML += '</g>';
          graphHTML += weekHTML;
        }

        // Remove the first incomplete month label
        if (monthPosition[1].x - monthPosition[0].x < 40) {
          monthPosition.shift();
        }

        // Remove the last incomplete month label
        if (monthPosition.at(-1).x > 660) {
          monthPosition.pop();
        }

        // Add month labels
        for (let x = 0; x < monthPosition.length; x++) {
          const item = monthPosition[x];
          const monthName = monthNameFormat.format(
            new Date(2022, item.monthIndex),
          );
          graphHTML += `<text x="${item.x}" y="-7" class="month">${monthName}</text>`;
        }

        // Add day labels
        graphHTML += `
            <text text-anchor="middle" class="wday" dx="-10" dy="23">M<title>Monday</title></text>
            <text text-anchor="middle" class="wday" dx="-10" dy="49">W<title>Wednesday</title></text>
            <text text-anchor="middle" class="wday" dx="-10" dy="75">F<title>Friday</title></text>`;

        graph.html(`
            <svg width="690" height="110" viewBox="0 0 702 110" class="js-calendar-graph-svg">
              <g transform="translate(16, 20)">${graphHTML}</g>
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

          // Update contribution graph
          $.ajax({
            url: '/update-contribution-graph/',
            data: {
              contribution_type: type,
              user: user,
            },
            success: function ({ contributions, title }) {
              $('#contribution-graph').data('contributions', contributions);
              $('#contributions .title').html(title);
              Pontoon.profile.renderContributionGraph();
            },
            error: function () {
              Pontoon.endLoader('Oops, something went wrong.', 'error');
            },
          });

          // Update contribution timeline
          $.ajax({
            url: '/update-contribution-timeline/',
            data: {
              contribution_type: type,
              user: user,
            },
            success: function (data) {
              $('#timeline').html(data);
            },
            error: function () {
              Pontoon.endLoader('Oops, something went wrong.', 'error');
            },
          });
        });
      },
      handleContributionGraphClick: function () {
        $('body').on('click', '#contribution-graph .day', function () {
          // .addClass() and .removeClass() jQuery methods don't work on SVG elements
          $('#contribution-graph .day').attr('class', 'day');
          $(this).attr('class', 'day selected');

          const day = $(this).data('date');
          const type = $('#contributions .type-selector span').data('type');
          const user = $('#server').data('user');

          // Update contribution timeline
          $.ajax({
            url: '/update-contribution-timeline/',
            data: {
              day: day,
              contribution_type: type,
              user: user,
            },
            success: function (data) {
              $('#timeline').html(data);
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
Pontoon.profile.handleContributionGraphClick();

// Set up chart group navigation
$('body').on('click', '#insights .chart-group-navigation li', function () {
  const items = $('.chart-group-navigation li').removeClass('active');
  $(this).addClass('active');
  const index = items.index(this);
  const itemWidth = $('.chart-item').first().outerWidth();

  // Show the selected graph view
  $('.chart-group').css('marginLeft', -index * itemWidth);
});

$('#account-status-form').on('submit', function (event) {
  event.preventDefault();

  const form = $(this);
  $.ajax({
    url: form.attr('action'),
    type: 'POST',
    data: {
      csrfmiddlewaretoken: $('body').data('csrf'),
    },
    success: function () {
      location.reload();
    },
  });
});
