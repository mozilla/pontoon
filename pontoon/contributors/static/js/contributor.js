$(function () {
  function loadNextEvents(cb) {
    var currentPage = $timeline.data('page'),
      nextPage = parseInt(currentPage, 10) + 1,
      // Determines if client should request new timeline events.
      finalized = parseInt($timeline.data('finalized'), 10);

    if (finalized || $timelineLoader.is(':visible')) {
      return;
    }

    $timelineLoader.show();

    $.get(timelineUrl, { page: nextPage }).then(
      function (timelineContents) {
        $('#main > .container').append(timelineContents);
        $timelineLoader.hide();
        $timeline.data('page', nextPage);
        cb();
      },
      function (response) {
        $timeline.data('page', nextPage);
        if (response.status === 404) {
          $timeline.data('finalized', 1);
          cb();
        } else {
          Pontoon.endLoader("Couldn't load the timeline.");
        }
        $timelineLoader.hide();
      },
    );
  }

  // Show/animate timeline blocks inside viewport
  function animate() {
    var $blocks = $('#main > .container > div');

    $blocks.each(function () {
      var block_bottom = $(this).offset().top + $(this).outerHeight(),
        window_bottom = $(window).scrollTop() + $(window).height(),
        blockSelf = this;

      // Animation of event that's displayed on the user timeline.
      function showEvent() {
        $(this)
          .find('.tick, .content')
          .css('visibility', 'visible')
          .addClass(function () {
            return $blocks.length > 1 ? 'bounce-in' : '';
          });
      }

      if (block_bottom <= window_bottom) {
        if ($blocks.index($(this)) === $blocks.length - 1) {
          loadNextEvents(function () {
            showEvent.apply(blockSelf);
          });
        } else {
          showEvent.apply(blockSelf);
        }
      }
    });
  }

  var $timelineLoader = $('#timeline-loader'),
    $timeline = $('#main'),
    timelineUrl = $timeline.data('url');

  // The first page of events.
  loadNextEvents(function () {
    $(window).scroll();
  });

  $(window).on('scroll', animate);

  if ($('.notification li').length) {
    Pontoon.endLoader();
  }
});

var Pontoon = (function (my) {
  return $.extend(true, my, {
    insights: {
      renderCharts: function () {
        var approvalRatioChart = $('#approval-ratio-chart');
        Pontoon.insights.renderRatioChart(
          approvalRatioChart,
          approvalRatioChart.data('approval-ratios'),
          approvalRatioChart.data('approval-ratios-12-month-avg'),
        );

        var selfApprovalRatioChart = $('#self-approval-ratio-chart');
        Pontoon.insights.renderRatioChart(
          selfApprovalRatioChart,
          selfApprovalRatioChart.data('self-approval-ratios'),
          selfApprovalRatioChart.data('self-approval-ratios-12-month-avg'),
        );
      },

      renderRatioChart: function (chart, data1, data2) {
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
              itemSort: function (a, b) {
                // Dataset order (needed for z-index) also affects tooltip,
                // so we need to manually sort tooltip items.
                if (a.datasetIndex === 1 && b.datasetIndex === 0) {
                  return 1;
                }
              },
              callbacks: {
                label: function (items, chart) {
                  const label = chart.datasets[items.datasetIndex].label;
                  const value = items.yLabel;

                  return label + ': ' + nf.format(value) + '%';
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
                    callback: function (value) {
                      return value + '%';
                    },
                    display: false,
                  },
                },
              ],
            },
          },
        });
      },
    },
  });
})(Pontoon || {});

/* Main code */
const nf = new Intl.NumberFormat('en', {
  maximumFractionDigits: 2,
});

Pontoon.insights.initialize();
Pontoon.insights.renderCharts();
