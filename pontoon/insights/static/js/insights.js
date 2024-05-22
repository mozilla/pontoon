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
  const getOrCreateLegendList = (id) => {
    id = id + '-legend';
    const legendContainer = document.getElementById(id);
    let listContainer = legendContainer.querySelector('ul');

    if (!listContainer) {
      listContainer = document.createElement('ul');
      legendContainer.appendChild(listContainer);
    }

    return listContainer;
  };
  const htmlLegendPlugin = {
    id: 'htmlLegend',
    afterUpdate(chart) {
      const ul = getOrCreateLegendList(chart.canvas.id);

      // Remove old legend items
      while (ul.firstChild) {
        ul.firstChild.remove();
      }

      // Generate custom legend items using the provided logic
      const labels = chart.data.datasets
        .map((dataset) => {
          const disabled = dataset.hidden ? 'disabled' : '';
          const color = dataset.borderColor || dataset.backgroundColor;

          return `<li class="${disabled}"><i class="icon" style="background-color:${color}"></i><span class="label">${dataset.label}</span></li>`;
        })
        .join('');

      // Add the generated legend items to the list
      ul.innerHTML = `<ul>${labels}</ul>`;

      // Add click event listeners for toggling dataset visibility
      Array.from(ul.getElementsByTagName('li')).forEach((li, index) => {
        li.onclick = () => {
          const { type } = chart.config;
          if (type === 'pie' || type === 'doughnut') {
            // Pie and doughnut charts only have a single dataset and visibility is per item
            chart.toggleDataVisibility(index);
          } else {
            chart.setDatasetVisibility(index, !chart.isDatasetVisible(index));
          }
          chart.update();
        };
      });
    },
  };

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
            pointRadius: 4,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: color,
            pointHoverBorderColor: style.getPropertyValue('--white-1'),
            spanGaps: true,
            fill: true,
            tension: 0.4,
          };
        });

        new Chart(chart, {
          type: 'bar',
          data: {
            labels: chart.data('dates'),
            datasets: datasets,
          },
          options: {
            tooltips: {
              position: 'nearest',
              mode: 'index',
              intersect: false,
              borderColor: style.getPropertyValue('--white-1'),
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
              x: {
                type: 'time',
                time: {
                  displayFormats: {
                    month: 'MMM',
                  },
                  tooltipFormat: 'MMMM YYYY',
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
            },
          },
          plugins: [htmlLegendPlugin],
        });
      },
    },
  });
})(Pontoon || {});

/* Main code */
Pontoon.insights.initialize();
Pontoon.insights.renderCharts();
