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

        // Set up chart group navigation
        $('body').on(
          'click',
          '#insights .chart-group-navigation li',
          function () {
            var items = $('.chart-group-navigation li').removeClass('active');
            $(this).addClass('active');
            var index = items.index(this);
            var itemWidth = $('.chart-item').first().outerWidth();

            // Show the selected graph view
            $('.chart-group').css('marginLeft', -index * itemWidth);
          },
        );

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
    },
  });
})(Pontoon || {});
