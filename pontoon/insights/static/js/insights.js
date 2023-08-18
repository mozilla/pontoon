const nf = new Intl.NumberFormat('en', {
  style: 'percent',
});

const shortMonthFormat = new Intl.DateTimeFormat('en', {
  month: 'short',
});

const longMonthFormat = new Intl.DateTimeFormat('en', {
  month: 'long',
  year: 'numeric',
});

var Pontoon = (function (my) {
  return $.extend(true, my, {
    insights: {
      renderCharts: function () {
        Pontoon.insights.renderPretranslationQualityChart(
          $('#team-pretranslation-quality-chart'),
        );
        Pontoon.insights.renderPretranslationQualityChart(
          $('#project-pretranslation-quality-chart'),
        );
      },
      renderPretranslationQualityChart: function (chart) {
        if (chart.length === 0) {
          return;
        }

        const colors = [
          '#fff',
          '#8074a8',
          '#c6c1f0',
          '#c46487',
          '#ffbed1',
          '#9c9290',
          '#c5bfbe',
          '#9b93c9',
          '#ddb5d5',
          '#7c7270',
          '#f498b6',
          '#b173a0',
          '#c799bc',
        ];

        const datasets = chart.data('dataset').map(function (item, index) {
          var color = colors[index % colors.length];
          return {
            type: 'line',
            label: item.name,
            data: item.approval_rate,
            borderColor: [color],
            borderWidth: item.name === 'All' ? 3 : 1,
            pointBackgroundColor: color,
            pointHitRadius: 10,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: color,
            pointHoverBorderColor: '#FFF',
            spanGaps: true,
          };
        });

        const pretranslationQualityChart = new Chart(chart, {
          type: 'bar',
          data: {
            labels: chart.data('dates'),
            datasets: datasets,
          },
          options: {
            legend: {
              display: false,
            },
            legendCallback: Pontoon.insights.customLegend(chart),
            tooltips: {
              mode: 'index',
              intersect: false,
              borderColor: '#FFF',
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
                title: function (items) {
                  const date = parseInt(items[0].label);
                  const title = longMonthFormat.format(new Date(date));
                  return `${title}`;
                },
              },
            },
            scales: {
              xAxes: [
                {
                  gridLines: {
                    display: false,
                  },
                  ticks: {
                    source: 'data',
                    callback: (value) =>
                      shortMonthFormat.format(new Date(value)),
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

        // Render custom legend
        var chartId = chart.attr('id');
        chart
          .parent()
          .next('.legend')
          .html(pretranslationQualityChart.generateLegend());
        Pontoon.insights.attachCustomLegendHandler(
          pretranslationQualityChart,
          `#${chartId}-legend .label`,
        );
      },
    },
  });
})(Pontoon || {});

/* Main code */
Pontoon.insights.initialize();
Pontoon.insights.renderCharts();
