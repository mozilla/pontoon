const nf = new Intl.NumberFormat('en', {
  style: 'percent',
});

const sf = new Intl.NumberFormat('en', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const longMonthFormat = new Intl.DateTimeFormat('en', {
  month: 'long',
  year: 'numeric',
});

const style = getComputedStyle(document.body);

function saveCommunityHealthLocales() {
  const selectedLocales = $('.multiple-item-selector .item.selected')
    .find('input[type=hidden]')
    .val();

  $.ajax({
    url: '/insights/ajax/edit-locales/',
    type: 'POST',
    data: {
      csrfmiddlewaretoken: $('body').data('csrf'),
      community_health_locales: selectedLocales,
    },
    error(request) {
      if (request.responseText === 'error') {
        Pontoon.endLoader('Oops, something went wrong.', 'error');
      } else {
        Pontoon.endLoader(request.responseText, 'error');
      }
    },
  });
}

function renderCommunityHealthPanel() {
  $.ajax({
    url: '/insights/ajax/render-panel/',
    success(response) {
      if (response.html) {
        Chart.getChart('community-health-chart')?.destroy();
        $('.community-health-score-container').html(response.html);
        Pontoon.insights.renderGlobalChart($('#community-health-chart'), 'chs');
      }
    },
    error(request) {
      if (request.responseText === 'error') {
        Pontoon.endLoader('Oops, something went wrong.', 'error');
      } else {
        Pontoon.endLoader(request.responseText, 'error');
      }
    },
  });
}

$('#edit-locales').on('click', function (e) {
  e.preventDefault();

  const container = $('.community-health-score-container');
  const localeSelector = $('.community-health-locale-selector');

  container.toggleClass('hidden');
  localeSelector.toggleClass('hidden');

  const isHidden = container.hasClass('hidden');

  $('#edit-locales')
    .toggleClass('back', isHidden)
    .find('span')
    .toggleClass('fa-chevron-right', !isHidden)
    .toggleClass('fa-chevron-left', isHidden);

  if (!isHidden) {
    renderCommunityHealthPanel();
  }
});

$('body').on('click', '#show-scores', function (e) {
  e.stopPropagation();

  const table = $('.community-health-table');
  table.toggleClass('show-score-view');

  const showScores = table.hasClass('show-score-view');

  // Keep each cells sort key in sync
  table.find('td.cell').each(function () {
    const td = $(this);
    const key = showScores
      ? td.attr('data-score-sort')
      : td.attr('data-base-sort');
    if (key !== undefined) {
      td.attr('data-sort', key);
    }
  });

  $('#show-scores').text(showScores ? 'Show default' : 'Show scores');
});

$(function () {
  $('body').on('click', '.multiple-item-selector .item.select li', function () {
    saveCommunityHealthLocales();
  });

  $('body').on('click', '.multiple-item-selector .move-all', function () {
    saveCommunityHealthLocales();
  });
});

// eslint-disable-next-line no-var
var Pontoon = (function (my) {
  return $.extend(true, my, {
    insights: {
      renderCharts: function () {
        Pontoon.insights.renderGlobalChart($('#community-health-chart'), 'chs');
        Pontoon.insights.renderGlobalChart(
          $('#team-pretranslation-quality-chart'),
          'approval_rate',
        );
        Pontoon.insights.renderGlobalChart(
          $('#project-pretranslation-quality-chart'),
          'approval_rate',
        );
      },
      renderGlobalChart: function (chart, key) {
        if (chart.length === 0) {
          return;
        }

        const isScore = key === 'chs';

        const colors = [
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
          const color =
            item.name === 'Average (all locales)'
              ? style.getPropertyValue('--white-1')
              : colors[index % colors.length];
          return {
            type: 'line',
            label: item.name,
            data: item[key],
            borderColor: [color],
            borderWidth: item.name === 'Average (all locales)' ? 3 : 1,
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
            hidden: item.name === 'Average (all locales)' ? false : true,
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
                    return isScore ? sf.format(value) : nf.format(value / 100);
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
                    const value = isScore
                      ? sf.format(parsed.y)
                      : nf.format(parsed.y / 100);
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
