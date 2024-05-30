const nf = new Intl.NumberFormat('en', {
  style: 'percent',
});

const longMonthFormat = new Intl.DateTimeFormat('en', {
  month: 'long',
  year: 'numeric',
});

const style = getComputedStyle(document.body);

// eslint-disable-next-line no-var
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
          style.getPropertyValue('--white-1'),
          style.getPropertyValue('--purple'),
          style.getPropertyValue('--lilac'),
          style.getPropertyValue('--pink-2'),
          style.getPropertyValue('--light-pink'),
          style.getPropertyValue('--brown-grey'),
          style.getPropertyValue('--brown-grey-2'),
          style.getPropertyValue('--lilac-purple'),
          style.getPropertyValue('--light-pink-2'),
          style.getPropertyValue('--green-brown'),
          style.getPropertyValue('--light-pink-3'),
          style.getPropertyValue('--dark-pink'),
          style.getPropertyValue('--light-pink-4'),
        ];

        const datasets = chart.data('dataset').map(function (item, index) {
          const color = colors[index % colors.length];
          return {
            type: 'line',
            label: item.name,
            data: item.approval_rate,
            borderColor: [color],
            borderWidth: item.name === 'All' ? 3 : 1,
            pointBackgroundColor: color,
            pointHitRadius: 10,
            pointRadius: 3.25,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: color,
            pointHoverBorderColor: style.getPropertyValue('--white-1'),
            spanGaps: true,
            fill: true,
            tension: 0.4,
            order: color.length - index,
          };
        });

        new Chart(chart, {
          type: 'bar',
          data: {
            labels: chart.data('dates'),
            datasets: datasets,
          },
          options: {
            clip: false,
            scales: {
              x: {
                type: 'time',
                time: {
                  unit: 'month',
                  displayFormats: {
                    month: 'MMM',
                  },
                  tooltipFormat: 'MMMM yyyy',
                },
                grid: {
                  display: false,
                },
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
                  callback: function (value) {
                    return nf.format(value / 100);
                  },
                },
                beginAtZero: true,
                max: 100,
              },
            },
            plugins: {
              htmlLegend: {
                containerID: chart,
              },
              legend: {
                display: false,
              },
              tooltip: {
                position: 'nearest',
                mode: 'index',
                intersect: false,
                borderColor: style.getPropertyValue('--white-1'),
                borderWidth: 1,
                caretPadding: 5,
                padding: {
                  x: 10,
                  y: 10,
                },
                callbacks: {
                  labelColor: (context) =>
                    Pontoon.insights.setLabelColor(context),
                  label: function (context) {
                    const { chart, datasetIndex, parsed } = context;

                    const label = chart.data.datasets[datasetIndex].label;
                    const value = nf.format(parsed.y / 100);
                    return `${label}: ${value}`;
                  },
                  title: function (tooltipItems) {
                    const date = tooltipItems[0].parsed.x;
                    const title = longMonthFormat.format(new Date(date));
                    return title;
                  },
                },
              },
            },
          },
          plugins: [Pontoon.insights.htmlLegendPlugin()],
        });
      },
    },
  });
})(Pontoon || {});

/* Main code */
Pontoon.insights.initialize();
Pontoon.insights.renderCharts();
