// eslint-disable-next-line no-var
var Pontoon = (function (my) {
  const nf = new Intl.NumberFormat('en');
  const pf = new Intl.NumberFormat('en', {
    style: 'percent',
    maximumFractionDigits: 2,
  });
  const style = getComputedStyle(document.body);

  return $.extend(true, my, {
    insights: {
      renderCharts: function () {
        Pontoon.insights.renderActiveUsers();
        Pontoon.insights.renderUnreviewedSuggestionsLifespan();
        Pontoon.insights.renderTimeToReviewSuggestions();
        Pontoon.insights.renderTimeToReviewPretranslatons();
        Pontoon.insights.renderTranslationActivity();
        Pontoon.insights.renderReviewActivity();
        Pontoon.insights.renderPretranslationQuality();
      },
      renderActiveUsers: function () {
        $('#insights canvas.chart').each(function () {
          // Collect data
          const parent = $(this).parents('.active-users-chart');
          const id = parent.attr('id');
          const period = $('.period-selector .active')
            .data('period')
            .toString();
          const active = $('.active-users').data(period)[id];
          const total = $('.active-users').data('total')[id];

          // Clear old canvas content to avoid aliasing
          const canvas = this;
          const context = canvas.getContext('2d');
          const dpr = window.devicePixelRatio || 1;
          context.clearRect(0, 0, canvas.width, canvas.height);
          context.lineWidth = 3 * dpr;

          const x = canvas.width / 2;
          const y = canvas.height / 2;
          const radius = (canvas.width - context.lineWidth) / 2;

          let activeLength = 0;
          if (total !== 0) {
            activeLength = (active / total) * 2;
          }
          const activeStart = -0.5;
          const activeEnd = activeStart + activeLength;
          plot(
            activeStart,
            activeEnd,
            style.getPropertyValue('--status-translated'),
          );

          let inactiveLength = 2;
          if (total !== 0) {
            inactiveLength = ((total - active) / total) * 2;
          }
          const inactiveStart = activeEnd;
          const inactiveEnd = inactiveStart + inactiveLength;
          plot(inactiveStart, inactiveEnd, style.getPropertyValue('--grey-9'));

          // Update number
          parent.find('.active').html(active);
          parent.find('.total').html(total);

          function plot(start, end, color) {
            context.beginPath();
            context.arc(x, y, radius, start * Math.PI, end * Math.PI);
            context.strokeStyle = color;
            context.stroke();
          }
        });
      },
      renderUnreviewedSuggestionsLifespan: function () {
        const chart = $('#unreviewed-suggestions-lifespan-chart');
        if (chart.length === 0) {
          return;
        }
        const ctx = chart[0].getContext('2d');

        const gradient = ctx.createLinearGradient(0, 0, 0, 160);
        const greenBlue = style.getPropertyValue('--green-blue');
        gradient.addColorStop(0, greenBlue);
        gradient.addColorStop(1, 'transparent');

        new Chart(chart, {
          type: 'line',
          data: {
            labels: $('#insights').data('dates'),
            datasets: [
              {
                label: 'Age of unreviewed suggestions',
                data: chart.data('lifespans'),
                backgroundColor: gradient,
                borderColor: [style.getPropertyValue('--status-unreviewed')],
                borderWidth: 2,
                pointBackgroundColor: style.getPropertyValue(
                  '--status-unreviewed',
                ),
                pointHitRadius: 10,
                pointRadius: 3.25,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: style.getPropertyValue(
                  '--status-unreviewed',
                ),
                pointHoverBorderColor: style.getPropertyValue('--white-1'),
                fill: true,
                tension: 0.4,
              },
            ],
          },
          options: {
            plugins: {
              tooltip: {
                borderColor: style.getPropertyValue('--status-unreviewed'),
                borderWidth: 1,
                caretPadding: 5,
                padding: {
                  x: 10,
                  y: 10,
                },
                displayColors: false,
                callbacks: {
                  label: (context) => nf.format(context.parsed.y) + ' days',
                },
              },
            },
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
                  beginAtZero: true,
                  maxTicksLimit: 3,
                  precision: 0,
                  callback: (value) => value + ' days',
                },
              },
            },
          },
        });
      },
      renderTimeToReviewSuggestions: function () {
        const chart = $('#time-to-review-suggestions-chart');
        if (chart.length === 0) {
          return;
        }
        const ctx = chart[0].getContext('2d');

        const gradient = ctx.createLinearGradient(0, 0, 0, 160);
        gradient.addColorStop(0, style.getPropertyValue('--green-blue'));
        gradient.addColorStop(1, 'transparent');

        new Chart(chart, {
          type: 'bar',
          data: {
            labels: $('#insights').data('dates'),
            datasets: [
              {
                type: 'line',
                label: 'Current month',
                data: chart.data('time-to-review-suggestions'),
                backgroundColor: gradient,
                borderColor: [style.getPropertyValue('--blue-1')],
                borderWidth: 2,
                pointBackgroundColor: style.getPropertyValue('--blue-1'),
                pointHitRadius: 10,
                pointRadius: 3.25,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: style.getPropertyValue('--blue-1'),
                pointHoverBorderColor: style.getPropertyValue('--white-1'),
                order: 2,
                spanGaps: true,
                fill: true,
                tension: 0.4,
              },
              {
                type: 'line',
                label: '12-month average',
                data: chart.data('time-to-review-suggestions-12-month-avg'),
                borderColor: [style.getPropertyValue('--status-unreviewed')],
                borderWidth: 1,
                pointBackgroundColor: style.getPropertyValue(
                  '--status-unreviewed',
                ),
                pointHitRadius: 10,
                pointRadius: 3.25,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: style.getPropertyValue(
                  '--status-unreviewed',
                ),
                pointHoverBorderColor: style.getPropertyValue('--white-1'),
                order: 1,
                spanGaps: true,
                fill: true,
                tension: 0.4,
              },
            ],
          },
          options: {
            plugins: {
              tooltip: {
                mode: 'index',
                intersect: false,
                borderColor: style.getPropertyValue('--status-unreviewed'),
                borderWidth: 1,
                caretPadding: 5,
                padding: {
                  x: 10,
                  y: 10,
                },
                callbacks: {
                  labelColor: (context) =>
                    Pontoon.insights.setLabelColor(context),
                  label(context) {
                    const { chart, datasetIndex, dataIndex } = context;
                    const dataset = chart.data.datasets[datasetIndex];
                    const value = dataset.data[dataIndex];
                    const label = dataset.label;
                    return `${label}: ${value} days`;
                  },
                },
              },
            },
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
                offset: true,
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
                  callback: (value) => `${value} days`,
                },
                beginAtZero: true,
              },
            },
          },
        });
      },
      renderTimeToReviewPretranslatons: function () {
        const chart = $('#time-to-review-pretranslations-chart');
        if (chart.length === 0) {
          return;
        }
        const ctx = chart[0].getContext('2d');

        const gradient = ctx.createLinearGradient(0, 0, 0, 160);
        gradient.addColorStop(0, style.getPropertyValue('--dark-magenta'));
        gradient.addColorStop(1, 'transparent');

        new Chart(chart, {
          type: 'bar',
          data: {
            labels: $('#insights').data('dates'),
            datasets: [
              {
                type: 'line',
                label: 'Current month',
                data: chart.data('time-to-review-pretranslations'),
                backgroundColor: gradient,
                borderColor: [style.getPropertyValue('--hot-pink')],
                borderWidth: 2,
                pointBackgroundColor: style.getPropertyValue('--hot-pink'),
                pointHitRadius: 10,
                pointRadius: 3.25,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: style.getPropertyValue('--hot-pink'),
                pointHoverBorderColor: style.getPropertyValue('--white-1'),
                order: 2,
                spanGaps: true,
                fill: true,
                tension: 0.4,
              },
              {
                type: 'line',
                label: '12-month average',
                data: chart.data('time-to-review-pretranslations-12-month-avg'),
                borderColor: [style.getPropertyValue('--dark-pink')],
                borderWidth: 1,
                pointBackgroundColor: style.getPropertyValue('--dark-pink'),
                pointHitRadius: 10,
                pointRadius: 3.25,
                pointHoverRadius: 6,
                pointHoverBackgroundColor:
                  style.getPropertyValue('--dark-pink'),
                pointHoverBorderColor: style.getPropertyValue('--white-1'),
                order: 1,
                spanGaps: true,
                fill: true,
                tension: 0.4,
              },
            ],
          },
          options: {
            plugins: {
              tooltip: {
                mode: 'index',
                intersect: false,
                borderColor: style.getPropertyValue('--dark-pink'),
                borderWidth: 1,
                caretPadding: 5,
                padding: {
                  x: 10,
                  y: 10,
                },
                callbacks: {
                  labelColor: (context) =>
                    Pontoon.insights.setLabelColor(context),
                  label(context) {
                    const { chart, datasetIndex, dataIndex } = context;
                    const dataset = chart.data.datasets[datasetIndex];
                    const value = dataset.data[dataIndex];
                    const label = dataset.label;
                    return `${label}: ${value} days`;
                  },
                },
              },
            },
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
                offset: true,
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
                  callback: (value) => `${value} days`,
                },
                beginAtZero: true,
              },
            },
          },
        });
      },
      renderTranslationActivity: function () {
        const chart = $('#translation-activity-chart');
        if (chart.length === 0) {
          return;
        }
        const ctx = chart[0].getContext('2d');

        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, style.getPropertyValue('--dark-green'));
        gradient.addColorStop(1, 'transparent');

        const humanData = chart.data('human-translations') || [];
        const machineryData = chart.data('machinery-translations') || [];
        const newSourcesData = chart.data('new-source-strings') || [];

        new Chart(chart, {
          type: 'bar',
          data: {
            labels: $('#insights').data('dates'),
            datasets: [
              {
                type: 'line',
                label: 'Completion',
                data: chart.data('completion'),
                yAxisID: 'completion-y-axis',
                backgroundColor: gradient,
                borderColor: [style.getPropertyValue('--status-translated')],
                borderWidth: 2,
                pointBackgroundColor: style.getPropertyValue(
                  '--status-translated',
                ),
                pointHitRadius: 10,
                pointRadius: 3.25,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: style.getPropertyValue(
                  '--status-translated',
                ),
                pointHoverBorderColor: style.getPropertyValue('--white-1'),
                fill: true,
                tension: 0.4,
              },
              humanData.length > 0 && {
                type: 'bar',
                label: 'Human translations',
                data: humanData,
                yAxisID: 'strings-y-axis',
                backgroundColor: style.getPropertyValue('--green'),
                hoverBackgroundColor: style.getPropertyValue('--green'),
                stack: 'translations',
                order: 2,
              },
              machineryData.length > 0 && {
                type: 'bar',
                label: 'Machinery translations',
                data: machineryData,
                yAxisID: 'strings-y-axis',
                backgroundColor: style.getPropertyValue('--forest-green-1'),
                hoverBackgroundColor:
                  style.getPropertyValue('--forest-green-1'),
                stack: 'translations',
                order: 1,
              },
              newSourcesData.length > 0 && {
                type: 'bar',
                label: 'New source strings',
                data: newSourcesData,
                yAxisID: 'strings-y-axis',
                backgroundColor: style.getPropertyValue('--black-3'),
                hoverBackgroundColor: style.getPropertyValue('--black-3'),
                stack: 'source-strings',
                order: 3,
                hidden: true,
              },
            ].filter(Boolean), // Filter out empty values
          },
          options: {
            clip: false,
            scales: {
              x: {
                stacked: true,
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
                offset: true,
                ticks: {
                  source: 'data',
                },
              },
              'completion-y-axis': {
                position: 'right',
                title: {
                  display: true,
                  text: 'COMPLETION',
                  color: style.getPropertyValue('--white-1'),
                  fontStyle: 100,
                },
                grid: {
                  display: false,
                },
                ticks: {
                  stepSize: 20,
                  callback: function (value) {
                    return pf.format(value / 100);
                  },
                },
                max: 100,
                beginAtZero: true,
              },
              'strings-y-axis': {
                stacked: true,
                position: 'left',
                title: {
                  display: true,
                  text: 'STRINGS',
                  color: style.getPropertyValue('--white-1'),
                  fontStyle: 100,
                },
                grid: {
                  display: false,
                },
                ticks: {
                  precision: 0,
                  callback: function (value) {
                    return nf.format(value);
                  },
                },
                beginAtZero: true,
              },
            },
            plugins: {
              htmlLegend: {
                containerID: 'translation-activity-chart-legend',
              },
              legend: {
                display: false,
              },
              tooltip: {
                mode: 'index',
                intersect: false,
                position: 'nearest',
                borderColor: style.getPropertyValue('--status-translated'),
                borderWidth: 1,
                caretPadding: 5,
                padding: {
                  x: 10,
                  y: 10,
                },
                itemSort: function (a, b) {
                  // Dataset order affects stacking, tooltip and
                  // legend, but it doesn't work intuitively, so
                  // we need to manually sort tooltip items.
                  if (a.datasetIndex === 2 && b.datasetIndex === 1) {
                    return 1;
                  }
                },
                callbacks: {
                  labelColor: (context) =>
                    Pontoon.insights.setLabelColor(context),
                  label: function (context) {
                    const {
                      chart,
                      raw: items,
                      datasetIndex,
                      dataIndex: index,
                    } = context;

                    const human = chart.data.datasets[1].data[index];
                    const machinery = chart.data.datasets[2].data[index];

                    const label = chart.data.datasets[datasetIndex].label;
                    const value = items;
                    const base = label + ': ' + nf.format(value);

                    switch (label) {
                      case 'Completion':
                        return label + ': ' + pf.format(value / 100);
                      case 'Human translations':
                      case 'Machinery translations': {
                        const pct = Pontoon.insights.getPercent(
                          value,
                          human + machinery,
                        );
                        return `${base} (${pct} of all translations)`;
                      }
                      default:
                        return base;
                    }
                  },
                },
              },
            },
          },
          plugins: [Pontoon.insights.htmlLegendPlugin()],
        });
      },
      renderReviewActivity: function () {
        const chart = $('#review-activity-chart');
        if (chart.length === 0) {
          return;
        }
        const ctx = chart[0].getContext('2d');

        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, style.getPropertyValue('--status-unreviewed'));
        gradient.addColorStop(1, 'transparent');

        const unreviewedData = chart.data('unreviewed') || [];
        const peerApprovedData = chart.data('peer-approved') || [];
        const selfApprovedData = chart.data('self-approved') || [];
        const rejectedData = chart.data('rejected') || [];
        const newSuggestionsData = chart.data('new-suggestions') || [];

        new Chart(chart, {
          type: 'bar',
          data: {
            labels: $('#insights').data('dates'),
            datasets: [
              {
                type: 'line',
                label: 'Unreviewed',
                data: unreviewedData,
                yAxisID: 'strings-y-axis',
                backgroundColor: gradient,
                borderColor: [style.getPropertyValue('--status-unreviewed')],
                borderWidth: 2,
                pointBackgroundColor: style.getPropertyValue(
                  '--status-unreviewed',
                ),
                pointHitRadius: 10,
                pointRadius: 3.25,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: style.getPropertyValue(
                  '--status-unreviewed',
                ),
                pointHoverBorderColor: style.getPropertyValue('--white-1'),
                fill: true,
                tension: 0.4,
              },
              peerApprovedData.length > 0 && {
                type: 'bar',
                label: 'Peer-approved',
                data: peerApprovedData,
                yAxisID: 'strings-y-axis',
                backgroundColor: style.getPropertyValue('--blue-1'),
                hoverBackgroundColor: style.getPropertyValue('--blue-1'),
                stack: 'review-actions',
                order: 3,
              },
              selfApprovedData.length > 0 && {
                type: 'bar',
                label: 'Self-approved',
                data: selfApprovedData,
                yAxisID: 'strings-y-axis',
                backgroundColor: style.getPropertyValue('--grey-5'),
                hoverBackgroundColor: style.getPropertyValue('--grey-5'),
                stack: 'review-actions',
                order: 2,
              },
              rejectedData.length > 0 && {
                type: 'bar',
                label: 'Rejected',
                data: rejectedData,
                yAxisID: 'strings-y-axis',
                backgroundColor: style.getPropertyValue('--magenta'),
                hoverBackgroundColor: style.getPropertyValue('--magenta'),
                stack: 'review-actions',
                order: 1,
              },
              newSuggestionsData.length > 0 && {
                type: 'bar',
                label: 'New suggestions',
                data: chart.data('new-suggestions'),
                yAxisID: 'strings-y-axis',
                backgroundColor: style.getPropertyValue('--black-3'),
                hoverBackgroundColor: style.getPropertyValue('--black-3'),
                stack: 'new-suggestions',
                order: 4,
                hidden: true,
              },
            ].filter(Boolean), // Filter out empty values
          },
          options: {
            clip: false,
            plugins: {
              htmlLegend: {
                containerID: 'review-activity-chart-legend',
              },
              legend: {
                display: false,
              },
              tooltip: {
                mode: 'index',
                intersect: false,
                borderColor: style.getPropertyValue('--status-unreviewed'),
                borderWidth: 1,
                caretPadding: 5,
                padding: {
                  x: 10,
                  y: 10,
                },
                itemSort: function (a, b) {
                  // Dataset order affects stacking, tooltip and
                  // legend, but it doesn't work intuitively, so
                  // we need to manually sort tooltip items.
                  if (
                    (a.datasetIndex === 3 && b.datasetIndex === 2) ||
                    (a.datasetIndex === 3 && b.datasetIndex === 1) ||
                    (a.datasetIndex === 2 && b.datasetIndex === 1)
                  ) {
                    return 1;
                  }
                },
                callbacks: {
                  labelColor: (context) =>
                    Pontoon.insights.setLabelColor(context),
                  label: function (context) {
                    const { chart, parsed, datasetIndex, dataIndex } = context;

                    const label = chart.data.datasets[datasetIndex].label;
                    const value = parsed.y;
                    const base = label + ': ' + nf.format(value);

                    if (chart.data.datasets.length < 4) {
                      return base;
                    }

                    const peerApproved = chart.data.datasets[1].data[dataIndex];
                    const selfApproved = chart.data.datasets[2].data[dataIndex];
                    const rejected = chart.data.datasets[3].data[dataIndex];

                    switch (label) {
                      case 'Self-approved': {
                        const pct = Pontoon.insights.getPercent(
                          value,
                          peerApproved + selfApproved,
                        );
                        return `${base} (${pct} of all approvals)`;
                      }
                      case 'Peer-approved':
                      case 'Rejected': {
                        const pct = Pontoon.insights.getPercent(
                          value,
                          peerApproved + rejected,
                        );
                        return `${base} (${pct} of peer-reviews)`;
                      }
                      default:
                        return base;
                    }
                  },
                },
              },
            },
            scales: {
              x: {
                stacked: true,
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
                offset: true,
                ticks: {
                  source: 'data',
                },
              },
              'strings-y-axis': {
                stacked: true,
                position: 'left',
                title: {
                  display: true,
                  text: 'STRINGS',
                  color: style.getPropertyValue('--white-1'),
                  fontStyle: 100,
                },
                grid: {
                  display: false,
                },
                ticks: {
                  precision: 0,
                  callback: function (value) {
                    return nf.format(value);
                  },
                },
                beginAtZero: true,
              },
            },
          },
          plugins: [Pontoon.insights.htmlLegendPlugin()],
        });
      },
      renderPretranslationQuality: function () {
        const chart = $('#pretranslation-quality-chart');
        if (chart.length === 0) {
          return;
        }
        const ctx = chart[0].getContext('2d');

        const gradient_approval = ctx.createLinearGradient(0, 0, 0, 400);
        gradient_approval.addColorStop(
          0,
          style.getPropertyValue('--dark-purple-2'),
        );
        gradient_approval.addColorStop(1, 'transparent');

        const gradient_chrf = ctx.createLinearGradient(0, 0, 0, 400);
        gradient_chrf.addColorStop(0, style.getPropertyValue('--dark-purple'));
        gradient_chrf.addColorStop(1, 'transparent');

        const approvedData = chart.data('approved') || [];
        const rejectedData = chart.data('rejected') || [];
        const newData = chart.data('new') || [];

        new Chart(chart, {
          type: 'bar',
          data: {
            labels: $('#insights').data('dates'),
            datasets: [
              {
                type: 'line',
                label: 'Approval rate',
                data: chart.data('approval-rate'),
                yAxisID: 'approval-rate-y-axis',
                backgroundColor: gradient_approval,
                borderColor: [style.getPropertyValue('--lilac')],
                borderWidth: 2,
                pointBackgroundColor: style.getPropertyValue('--lilac'),
                pointHitRadius: 10,
                pointRadius: 3.25,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: style.getPropertyValue('--lilac'),
                pointHoverBorderColor: style.getPropertyValue('--white-1'),
                spanGaps: true,
                fill: true,
                tension: 0.4,
              },
              {
                type: 'line',
                label: 'chrf++ score',
                data: chart.data('chrf-score'),
                yAxisID: 'approval-rate-y-axis',
                backgroundColor: gradient_chrf,
                borderColor: [style.getPropertyValue('--purple')],
                borderWidth: 2,
                pointBackgroundColor: style.getPropertyValue('--purple'),
                pointHitRadius: 10,
                pointRadius: 3.25,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: style.getPropertyValue('--purple'),
                pointHoverBorderColor: style.getPropertyValue('--white-1'),
                spanGaps: true,
                fill: true,
                tension: 0.4,
              },
              approvedData.length > 0 && {
                type: 'bar',
                label: 'Approved',
                data: approvedData,
                yAxisID: 'strings-y-axis',
                backgroundColor: style.getPropertyValue('--pink-2'),
                hoverBackgroundColor: style.getPropertyValue('--pink-2'),
                stack: 'reviewed-pretranslations',
                order: 2,
              },
              rejectedData.length > 0 && {
                type: 'bar',
                label: 'Rejected',
                data: rejectedData,
                yAxisID: 'strings-y-axis',
                backgroundColor: style.getPropertyValue('--light-pink'),
                hoverBackgroundColor: style.getPropertyValue('--light-pink'),
                stack: 'reviewed-pretranslations',
                order: 1,
              },
              newData.length > 0 && {
                type: 'bar',
                label: 'New pretranslations',
                data: newData,
                yAxisID: 'strings-y-axis',
                backgroundColor: style.getPropertyValue('--black-3'),
                hoverBackgroundColor: style.getPropertyValue('--black-3'),
                stack: 'new-pretranslations',
                order: 3,
                hidden: true,
              },
            ].filter(Boolean), // Filter out empty values
          },
          options: {
            clip: false,
            plugins: {
              htmlLegend: {
                containerID: 'pretranslation-quality-chart-legend',
              },
              legend: {
                display: false,
              },
              tooltip: {
                mode: 'index',
                intersect: false,
                borderColor: style.getPropertyValue('--pink-3'),
                borderWidth: 1,
                caretPadding: 5,
                xPadding: 10,
                yPadding: 10,
                itemSort: function (a, b) {
                  // Dataset order affects stacking, tooltip and
                  // legend, but it doesn't work intuitively, so
                  // we need to manually sort tooltip items.
                  if (
                    (a.datasetIndex === 3 && b.datasetIndex === 2) ||
                    (a.datasetIndex === 3 && b.datasetIndex === 1) ||
                    (a.datasetIndex === 2 && b.datasetIndex === 1)
                  ) {
                    return 1;
                  }
                },
                callbacks: {
                  labelColor: (context) =>
                    Pontoon.insights.setLabelColor(context),
                  label: function (context) {
                    const { chart, parsed, datasetIndex } = context;

                    const label = chart.data.datasets[datasetIndex].label;
                    const value = parsed.y;
                    const base = label + ': ' + nf.format(value);

                    switch (label) {
                      case 'Approval rate':
                        return label + ': ' + pf.format(value / 100);
                      default:
                        return base;
                    }
                  },
                },
              },
            },
            scales: {
              x: {
                stacked: true,
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
                offset: true,
                ticks: {
                  source: 'data',
                },
              },
              'approval-rate-y-axis': {
                position: 'right',
                title: {
                  display: true,
                  text: 'APPROVAL RATE',
                  color: style.getPropertyValue('--white-1'),
                  fontStyle: 100,
                },
                grid: {
                  display: false,
                },
                ticks: {
                  stepSize: 20,
                  callback: function (value) {
                    return pf.format(value / 100);
                  },
                },
                beginAtZero: true,
                max: 100,
              },
              'strings-y-axis': {
                stacked: true,
                position: 'left',
                title: {
                  display: true,
                  text: 'STRINGS',
                  color: style.getPropertyValue('--white-1'),
                  fontStyle: 100,
                },
                grid: {
                  display: false,
                },
                ticks: {
                  precision: 0,
                  callback: function (value) {
                    return nf.format(value);
                  },
                },
                beginAtZero: true,
              },
            },
          },
          plugins: [Pontoon.insights.htmlLegendPlugin()],
        });
      },
      getPercent: function (value, total) {
        const n = value / total;
        return pf.format(isFinite(n) ? n : 0);
      },
    },
  });
})(Pontoon || {});
