/*
 * Draw progress indicator and value
 */
$(function() {
  $('canvas.chart').each(function() {
    // Get data
    var stats = {},
        progress = $(this).parents('.progress');

    progress.siblings('.legend').find('li').each(function() {
      stats[$(this).attr('class')] = $(this).find('.value').data('value');
    });

    var fraction = {
          translated: stats.all ? stats.translated / stats.all : 0,
          suggested: stats.all ? stats.suggested / stats.all : 0,
          fuzzy: stats.all ? stats.fuzzy / stats.all : 0,
          missing: stats.all ? stats.missing / stats.all : 1 /* Draw "empty" progress if no projects enabled */
        },
        number = Math.floor(fraction.translated * 100);

    // Update graph
    var canvas = this,
        context = canvas.getContext('2d');

    // Clear old canvas content to avoid aliasing
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.lineWidth = 3;

    var x = canvas.width/2,
        y = canvas.height/2,
        radius = (canvas.width - context.lineWidth)/2,
        end = null;

    progress.siblings('.legend').find('li:not(.all)').each(function() {
      var length = fraction[$(this).attr('class')] * 2,
          start = (end !== null) ? end : -0.5,
          color = window.getComputedStyle(
            $(this).find('.status')[0], ':before'
          ).getPropertyValue('color');

      end = start + length;

      context.beginPath();
      context.arc(x, y, radius, start * Math.PI, end * Math.PI);
      context.strokeStyle = color;
      context.stroke();
    });

    // Update number
    progress.find('.number').html(number).show();
  });
});
