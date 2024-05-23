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
        Chart.defaults.font.weight = '100'; // Chart.js uses 'weight' instead of 'style' for font
        Chart.defaults.plugins.legend.display = false;
        Chart.defaults.datasets.bar.barPercentage = 0.7;
        Chart.defaults.datasets.bar.categoryPercentage = 0.7;
      },
      // Custom legend item event handler
    },
  });
})(Pontoon || {});
