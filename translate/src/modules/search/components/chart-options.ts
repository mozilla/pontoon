// Build the time-range chart options on demand so that they use the current
// values of the theme CSS variables.
export function getChartOptions(
  data: number[][],
  setExtremes: (arg0: { min: number; max: number }) => void,
) {
  const style = getComputedStyle(document.body);

  return {
    credits: {
      enabled: false,
    },
    title: {
      enabled: false,
    },
    scrollbar: {
      enabled: false,
    },
    time: {
      useUTC: false,
    },
    tooltip: {
      enabled: false,
    },
    chart: {
      animation: false,
      backgroundColor: 'transparent',
      marginLeft: 5,
      marginRight: 4,
      spacingBottom: 30,
      spacingTop: 0,
      style: {
        fontFamily: 'inherit',
      },
    },
    xAxis: [
      {
        lineWidth: 0,
        tickLength: 0,
        labels: {
          enabled: false,
        },
        events: {
          setExtremes,
        },
      },
    ],
    yAxis: [
      {
        type: 'logarithmic',
        minorTickInterval: 0,
        gridLineWidth: 0,
        labels: {
          enabled: false,
        },
      },
    ],
    rangeSelector: {
      selected: 0,
      buttons: [
        {
          type: 'all',
          text: 'All',
        },
        {
          type: 'day',
          count: 30,
          text: '30 days',
        },
        {
          type: 'day',
          count: 7,
          text: '7 days',
        },
        {
          type: 'day',
          count: 1,
          text: '24 h',
        },
        {
          type: 'minute',
          count: 60,
          text: '60 min',
        },
      ],
      buttonPosition: {
        x: -4,
        y: 95,
      },
      buttonSpacing: 20,
      buttonTheme: {
        fill: 'none',
        stroke: 'none',
        width: null,
        style: {
          color: style.getPropertyValue('--translation-color'),
          fontWeight: 300,
          textTransform: 'uppercase',
        },
        states: {
          hover: {
            fill: 'none',
            style: {
              color: style.getPropertyValue('--accent-color'),
            },
          },
          select: {
            fill: 'none',
            style: {
              color: style.getPropertyValue('--accent-color-alt'),
              fontWeight: 300,
            },
          },
          disabled: {
            style: {
              color: style.getPropertyValue('--translation-secondary-color'),
              cursor: 'default',
            },
          },
        },
      },
      inputEnabled: false,
    },
    navigator: {
      height: 80,
      maskFill: 'rgba(77, 89, 103, 0.2)',
      outlineColor: style.getPropertyValue('--time-range-navigator'),
      handles: {
        backgroundColor: style.getPropertyValue('--time-range-navigator'),
        borderColor: style.getPropertyValue('--time-range-handles'),
      },
      series: {
        type: 'column',
        color: style.getPropertyValue('--time-range-series'),
      },
      xAxis: {
        lineWidth: 1,
        lineColor: style.getPropertyValue('--time-range-navigator'),
        gridLineWidth: 0,
        labels: {
          enabled: false,
        },
      },
    },
    series: [
      {
        animation: false,
        data,
        type: 'column',
      },
    ],
  };
}
