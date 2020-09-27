/* @flow */

// Default Time Range chart configuration
export const CHART_OPTIONS = {
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
                setExtremes: null,
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
        buttonTheme: {
            fill: 'none',
            stroke: 'none',
            width: null,
            style: {
                color: '#FFFFFF',
                fontWeight: 300,
                textTransform: 'uppercase',
            },
            states: {
                hover: {
                    fill: 'none',
                    style: {
                        color: '#7BC876',
                    },
                },
                select: {
                    fill: 'none',
                    style: {
                        color: '#7BC876',
                        fontWeight: 300,
                    },
                },
                disabled: {
                    style: {
                        color: '#888888',
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
        outlineColor: '#4D5967',
        handles: {
            backgroundColor: '#4D5967',
            borderColor: '#272A2F',
        },
        series: {
            type: 'column',
            color: '#7BC876',
        },
        xAxis: {
            lineWidth: 1,
            lineColor: '#4D5967',
            gridLineWidth: 0,
            labels: {
                enabled: false,
            },
        },
    },
    series: [
        {
            animation: false,
            data: [],
            type: 'column',
        },
    ],
};
