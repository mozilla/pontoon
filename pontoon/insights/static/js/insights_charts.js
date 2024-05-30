// eslint-disable-next-line no-var
var Pontoon = (function (my) {
  const style = getComputedStyle(document.body);
  return $.extend(true, my, {
    insights: {
      initialize: function () {
        // Show/hide info tooltips on click on the icon
        $('#insights h3 .fa-info').on('click', function (e) {
          e.stopPropagation();
          $(this).next('.tooltip').toggle();
          $(this).toggleClass('active');
        });

        // Hide info tooltips on click outside
        $(window).click(function () {
          $('#insights .tooltip').hide();
          $('#insights h3 .fa-info').removeClass('active');
        });

        // Select active users period
        $('#insights h3 .period-selector .selector').on('click', function () {
          $('#insights h3 .period-selector .selector').removeClass('active');
          $(this).addClass('active');
          Pontoon.insights.renderActiveUsers();
        });

        // Set up canvas to be HiDPI display ready
        $('#insights canvas.chart').each(function () {
          const canvas = this;

          const dpr = window.devicePixelRatio || 1;
          canvas.style.width = canvas.width + 'px';
          canvas.style.height = canvas.height + 'px';
          canvas.width = canvas.width * dpr;
          canvas.height = canvas.height * dpr;
        });

        // Set up default Chart.js configuration
        Chart.defaults.color = style.getPropertyValue('--light-grey-7');
        Chart.defaults.borderColor = style.getPropertyValue('--dark-grey-1');
        Chart.defaults.font.family = 'Open Sans';
        Chart.defaults.font.weight = '100';
        Chart.defaults.plugins.legend.display = false;
        Chart.defaults.datasets.bar.barPercentage = 0.7;
        Chart.defaults.datasets.bar.categoryPercentage = 0.7;
      },
      // Custom styling callback for Tooltip labels
      setLabelColor: function (context) {
        const style = getComputedStyle(document.body);
        return {
          borderColor: style.getPropertyValue('--tooltip-color'),
          backgroundColor:
            context.dataset.pointBackgroundColor ||
            context.dataset.backgroundColor,
        };
      },
      // Custom legend callback for styling and event handling
      getOrCreateLegendList: function (id) {
        const legendContainer = document.getElementById(id);
        let listContainer = legendContainer.querySelector('ul');

        if (!listContainer) {
          listContainer = document.createElement('ul');
          legendContainer.appendChild(listContainer);
        }

        return listContainer;
      },
      htmlLegendPlugin: function () {
        return {
          id: 'htmlLegend',
          afterUpdate(chart) {
            const containerID = chart.canvas.id + '-legend';
            const ul = Pontoon.insights.getOrCreateLegendList(containerID);

            // Remove old legend items
            while (ul.firstChild) {
              ul.firstChild.remove();
            }

            const items =
              chart.options.plugins.legend.labels.generateLabels(chart);

            items.forEach((item) => {
              const li = document.createElement('li');

              const disabled = item.hidden ? 'disabled' : '';
              const color =
                item.strokeStyle == style.getPropertyValue('--dark-grey-1')
                  ? item.fillStyle
                  : item.strokeStyle;

              li.className = disabled;
              li.innerHTML = `<i class="icon" style="background-color:${color}"></i><span class="label">${item.text}</span>`;

              li.onclick = (event) => {
                // Check if Alt or Meta key was pressed
                if (event.altKey || event.metaKey) {
                  chart.data.datasets.forEach((obj, i) => {
                    const meta = chart.getDatasetMeta(i);
                    meta.hidden = i === item.datasetIndex ? null : true;
                  });
                  $(li).parent().find('li').addClass('disabled');
                } else {
                  const meta = chart.getDatasetMeta(item.datasetIndex);
                  const dataset = chart.data.datasets[item.datasetIndex];
                  meta.hidden = meta.hidden === null ? !dataset.hidden : null;
                }

                chart.update();
              };
              ul.appendChild(li);
            });
          },
        };
      },
    },
  });
})(Pontoon || {});
