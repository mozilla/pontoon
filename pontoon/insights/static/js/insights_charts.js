var Pontoon = (function (my) {
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
          var canvas = this;

          var dpr = window.devicePixelRatio || 1;
          canvas.style.width = canvas.width + 'px';
          canvas.style.height = canvas.height + 'px';
          canvas.width = canvas.width * dpr;
          canvas.height = canvas.height * dpr;
        });

        // Set up default Chart.js configuration
        Chart.defaults.global.defaultFontColor = '#AAA';
        Chart.defaults.global.defaultFontFamily = 'Open Sans';
        Chart.defaults.global.defaultFontStyle = '100';
        Chart.defaults.global.datasets.bar.barPercentage = 0.7;
        Chart.defaults.global.datasets.bar.categoryPercentage = 0.7;
      },
      // Legend configuration doesn't allow for enough flexibility,
      // so we build our own legend
      // eslint-disable-next-line no-unused-vars
      customLegend: function (chart) {
        return function (chart) {
          function renderLabels(chart) {
            return chart.data.datasets
              .map(function (dataset) {
                var disabled = dataset.hidden ? 'disabled' : '';
                var color = dataset.borderColor || dataset.backgroundColor;

                return (
                  '<li class="' +
                  disabled +
                  '">' +
                  '<i class="icon" style="background-color:' +
                  color +
                  '"></i>' +
                  '<span class="label">' +
                  dataset.label +
                  '</span>' +
                  '</li>'
                );
              })
              .join('');
          }

          return '<ul>' + renderLabels(chart) + '</ul>';
        };
      },
      // Custom legend item event handler
      attachCustomLegendHandler: function (chart, selector) {
        $('body').on('click', selector, function () {
          var li = $(this).parent();
          var index = li.index();

          var meta = chart.getDatasetMeta(index);
          var dataset = chart.data.datasets[index];

          meta.hidden = meta.hidden === null ? !dataset.hidden : null;
          chart.update();

          li.toggleClass('disabled');
        });
      },
    },
  });
})(Pontoon || {});
