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
        .map((dataset, index) => {
          const disabled = chart.getDatasetMeta(index).hidden ? 'disabled' : '';
          const color = dataset.borderColor || dataset.backgroundColor;

          return `<li class="${disabled}"><i class="icon" style="background-color:${color}"></i><span class="label">${dataset.label}</span></li>`;
        })
        .join('');

      // Add the generated legend items to the list
      ul.innerHTML = labels;

      // Add click event listeners for toggling dataset visibility
      Array.from(ul.getElementsByTagName('li')).forEach((li, index) => {
        li.onclick = (e) => {
          const meta = chart.getDatasetMeta(index);
          const dataset = chart.data.datasets[index];

          if (e.altKey || e.metaKey) {
            // Show clicked and hide the rest
            chart.data.datasets.forEach((ds, i) => {
              const meta = chart.getDatasetMeta(i);
              meta.hidden = i === index ? null : true;
            });
            Array.from(ul.getElementsByTagName('li')).forEach((li, i) => {
              li.classList.toggle('disabled', i !== index);
            });
          } else {
            // Toggle clicked
            meta.hidden = meta.hidden === null ? !dataset.hidden : null;
            li.classList.toggle('disabled');
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
            pointRadius: 3.25,
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
            clip: false,
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
                  labelColor: function (context) {
                    return {
                      borderColor: '#fff',
                      backgroundColor:
                        context.dataset.hoverBackgroundColor ||
                        context.dataset.pointBackgroundColor,
                      borderWidth: 0.3,
                    };
                  },
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
          plugins: [htmlLegendPlugin],
        });
      },
    },
  });
})(Pontoon || {});

/* Main code */
Pontoon.insights.initialize();
Pontoon.insights.renderCharts();
