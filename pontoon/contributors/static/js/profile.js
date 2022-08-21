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
