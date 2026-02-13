/*
 * Draw progress indicator and value
 */
$(function () {
  $('canvas.chart').each(function () {
    // Get data
    const stats = {},
      progress = $(this).parents('.progress');

    progress
      .siblings('.legend')
      .find('li')
      .each(function () {
        stats[$(this).attr('class')] = $(this).find('.value').data('value');
      });

    stats.all = progress
      .siblings('.non-plottable')
      .find('.all .value')
      .data('value');

    const fraction = {
        translated: stats.all ? stats.translated / stats.all : 0,
        warnings: stats.all ? stats.warnings / stats.all : 0,
        errors: stats.all ? stats.errors / stats.all : 0,
        missing: stats.all
          ? stats.missing / stats.all
          : 1 /* Draw "empty" progress if no projects enabled */,
      },
      number = Math.floor((fraction.translated + fraction.warnings) * 100);

    // Update graph
    const canvas = this,
      context = canvas.getContext('2d');

    // Set up canvas to be HiDPI display ready
    const dpr = window.devicePixelRatio || 1;
    canvas.style.width = canvas.width + 'px';
    canvas.style.height = canvas.height + 'px';
    canvas.width = canvas.width * dpr;
    canvas.height = canvas.height * dpr;

    // Clear old canvas content to avoid aliasing
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.lineWidth = 3 * dpr;

    const x = canvas.width / 2,
      y = canvas.height / 2,
      radius = (canvas.width - context.lineWidth) / 2;
    let end = -0.5;

    progress
      .siblings('.legend')
      .find('li')
      .each(function () {
        const length = fraction[$(this).attr('class')] * 2,
          start = end,
          color = window
            .getComputedStyle($(this).find('.status')[0], ':before')
            .getPropertyValue('color');

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
