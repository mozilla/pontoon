var Pontoon = (function (my) {
    return $.extend(true, my, {
        insights: {
            load: function () {
                var insights = $('#insights');

                // Tooltips
                $('h3 .fa-info').hover(
                    function () {
                        $(this).next().show();
                    },
                    function () {
                        $(this).next().hide();
                    }
                );

                // Active users
                $('#insights canvas.chart').each(function () {
                    var wrapper = $(this).parents('.wrapper');
                    var active = wrapper.data('active');
                    var all = wrapper.data('all');

                    // Update graph
                    var canvas = this;
                    var context = canvas.getContext('2d');

                    // Set up canvas to be HiDPI display ready
                    var dpr = window.devicePixelRatio || 1;
                    canvas.style.width = canvas.width + 'px';
                    canvas.style.height = canvas.height + 'px';
                    canvas.width = canvas.width * dpr;
                    canvas.height = canvas.height * dpr;

                    // Clear old canvas content to avoid aliasing
                    context.clearRect(0, 0, canvas.width, canvas.height);
                    context.lineWidth = 3 * dpr;

                    var x = canvas.width / 2;
                    var y = canvas.height / 2;
                    var radius = (canvas.width - context.lineWidth) / 2;

                    var activeLength = 0;
                    if (all !== 0) {
                        activeLength = (active / all) * 2;
                    }
                    var activeStart = -0.5;
                    var activeEnd = activeStart + activeLength;
                    plot(activeStart, activeEnd, '#7BC876');

                    var inactiveLength = 2;
                    if (all !== 0) {
                        inactiveLength = ((all - active) / all) * 2;
                    }
                    var inactiveStart = activeEnd;
                    var inactiveEnd = inactiveStart + inactiveLength;
                    plot(inactiveStart, inactiveEnd, '#5F7285');

                    // Update number
                    wrapper.find('.active').html(active).show();
                    wrapper.find('.all').html(all).show();
                    wrapper.parent().find('.all').html(all).show();

                    function plot(start, end, color) {
                        context.beginPath();
                        context.arc(
                            x,
                            y,
                            radius,
                            start * Math.PI,
                            end * Math.PI
                        );
                        context.strokeStyle = color;
                        context.stroke();
                    }
                });

                // Unreviewed suggestion lifespan
                var unreviewed = $('#unreviewed-lifespan-container');
                Highcharts.chart('unreviewed-lifespan-container', {
                    chart: {
                        backgroundColor: 'transparent',
                        height: 160,
                        spacing: [10, 0, 0, 0],
                        style: {
                            fontFamily: 'Open Sans',
                        },
                        zoomType: 'x',
                    },
                    colors: ['#4fc4f6'],
                    title: null,
                    credits: {
                        enabled: false,
                    },
                    xAxis: [
                        {
                            type: 'datetime',
                            categories: insights.data('dates'),
                            lineWidth: 0,
                            labels: {
                                formatter: function () {
                                    return Highcharts.dateFormat(
                                        '%b',
                                        this.value
                                    );
                                },
                                style: {
                                    color: '#AAA',
                                    fontWeight: 100,
                                },
                            },
                        },
                    ],
                    yAxis: [
                        {
                            title: null,
                            labels: {
                                padding: 0,
                                style: {
                                    color: '#AAA',
                                    fontWeight: 100,
                                },
                                format: '{value} days',
                            },
                            gridLineWidth: 0,
                            opposite: true,
                        },
                    ],
                    tooltip: {
                        headerFormat: '<b>{point.key}</b><br/>',
                        xDateFormat: '%B %Y',
                        backgroundColor: '#272A2F',
                        shared: true,
                        style: {
                            color: '#FFF',
                        },
                        valueSuffix: ' days',
                    },
                    plotOptions: {
                        areaspline: {
                            fillColor: {
                                linearGradient: [0, 0, 0, 130],
                                stops: [
                                    [
                                        0,
                                        Highcharts.color('#4fc4f6')
                                            .setOpacity(0.4)
                                            .get('rgba'),
                                    ],
                                    [1, 'transparent'],
                                ],
                            },
                        },
                    },
                    series: [
                        {
                            name: 'Unreviewed suggestion lifespan',
                            type: 'areaspline',
                            data: unreviewed.data('lifespans'),
                            showInLegend: false,
                        },
                    ],
                });

                // Translation activity
                var translationActivity = $('#translation-activity-container');
                Highcharts.chart('translation-activity-container', {
                    chart: {
                        backgroundColor: 'transparent',
                        spacing: [10, 0, 0, 0],
                        style: {
                            fontFamily: 'Open Sans',
                        },
                        zoomType: 'x',
                    },
                    colors: ['#7BC876', '#7BC87666', '#7BC87633', '#5F7285'],
                    title: null,
                    credits: {
                        enabled: false,
                    },
                    xAxis: [
                        {
                            type: 'datetime',
                            categories: insights.data('dates'),
                            lineWidth: 0,
                            labels: {
                                formatter: function () {
                                    return Highcharts.dateFormat(
                                        '%b',
                                        this.value
                                    );
                                },
                                style: {
                                    color: '#AAA',
                                    fontWeight: 100,
                                },
                            },
                            crosshair: {
                                color: '#272A2F',
                            },
                        },
                    ],
                    yAxis: [
                        {
                            // Secondary yAxis
                            title: {
                                text: 'Completion',
                                style: {
                                    color: '#FFF',
                                    fontWeight: 100,
                                    textTransform: 'uppercase',
                                },
                            },
                            labels: {
                                format: '{value}%',
                                style: {
                                    color: '#AAA',
                                    fontWeight: 100,
                                },
                            },
                            max: 100,
                            opposite: true,
                            gridLineWidth: 0,
                        },
                        {
                            // Primary yAxis
                            title: {
                                text: 'Strings',
                                style: {
                                    color: '#FFF',
                                    fontWeight: 100,
                                    textTransform: 'uppercase',
                                },
                            },
                            labels: {
                                format: '{value}',
                                style: {
                                    color: '#AAA',
                                    fontWeight: 100,
                                },
                            },
                            gridLineWidth: 0,
                        },
                    ],
                    tooltip: {
                        backgroundColor: '#272A2F',
                        formatter: function () {
                            var formatter = new Intl.DateTimeFormat('en-GB', {
                                month: 'long',
                                year: 'numeric',
                            });

                            var s =
                                '<b>' +
                                formatter.format(new Date(this.x)) +
                                '</b>';
                            var points = this.points;

                            $.each(points, function (i, point) {
                                var percent = '';
                                var share = null;
                                var total = 0;

                                if (point.series.name === 'Completion') {
                                    percent = '%';
                                }
                                if (
                                    point.series.name === 'Human translations'
                                ) {
                                    share = 0;
                                    total = point.y + points[i + 1].y;
                                    if (total !== 0) {
                                        share = point.y / total;
                                    }
                                    percent =
                                        ' (' +
                                        Math.floor(share * 100) +
                                        '% of all translations)';
                                }
                                if (
                                    point.series.name ===
                                    'Machinery translations'
                                ) {
                                    share = 0;
                                    total = point.y + points[i - 1].y;
                                    if (total !== 0) {
                                        share = point.y / total;
                                    }
                                    percent =
                                        ' (' +
                                        Math.floor(share * 100) +
                                        '% of all translations)';
                                }

                                s +=
                                    '<br/><span style="color:' +
                                    point.color +
                                    '">\u25CF</span> ' +
                                    point.series.name +
                                    ': ' +
                                    point.y +
                                    percent;
                            });

                            return s;
                        },
                        shared: true,
                        style: {
                            color: '#FFF',
                        },
                    },
                    legend: {
                        align: 'center',
                        itemHiddenStyle: {
                            color: '#4d5967',
                        },
                        itemHoverStyle: {
                            color: '#FFF',
                        },
                        itemStyle: {
                            color: '#FFF',
                            fontWeight: 700,
                        },
                    },
                    plotOptions: {
                        areaspline: {
                            fillColor: {
                                linearGradient: [0, 0, 0, 250],
                                stops: [
                                    [
                                        0,
                                        Highcharts.color('#7BC876')
                                            .setOpacity(0.2)
                                            .get('rgba'),
                                    ],
                                    [1, 'transparent'],
                                ],
                            },
                        },
                        column: {
                            borderWidth: 0,
                            stacking: 'normal',
                        },
                    },
                    series: [
                        {
                            name: 'Completion',
                            type: 'areaspline',
                            data: translationActivity.data('completion'),
                            tooltip: {
                                valueSuffix: '%',
                            },
                        },
                        {
                            name: 'Human translations',
                            type: 'column',
                            yAxis: 1,
                            data: translationActivity.data(
                                'human-translations'
                            ),
                            stack: 'Translations',
                        },
                        {
                            name: 'Machinery translations',
                            type: 'column',
                            yAxis: 1,
                            data: translationActivity.data(
                                'machinery-translations'
                            ),
                            stack: 'Translations',
                        },
                        {
                            name: 'New source strings',
                            type: 'column',
                            yAxis: 1,
                            data: translationActivity.data(
                                'new-source-strings'
                            ),
                            visible: false,
                        },
                    ],
                });

                // Review activity
                var reviewActivity = $('#review-activity-container');
                Highcharts.chart('review-activity-container', {
                    chart: {
                        backgroundColor: 'transparent',
                        spacing: [10, 0, 0, 0],
                        style: {
                            fontFamily: 'Open Sans',
                        },
                        zoomType: 'x',
                    },
                    colors: [
                        '#4fc4f6',
                        '#4fc4f666',
                        '#4fc4f633',
                        '#F366',
                        '#5F7285',
                    ],
                    title: null,
                    credits: {
                        enabled: false,
                    },
                    xAxis: [
                        {
                            type: 'datetime',
                            categories: insights.data('dates'),
                            lineWidth: 0,
                            labels: {
                                formatter: function () {
                                    return Highcharts.dateFormat(
                                        '%b',
                                        this.value
                                    );
                                },
                                style: {
                                    color: '#AAA',
                                    fontWeight: 100,
                                },
                            },
                            crosshair: {
                                color: '#272A2F',
                            },
                        },
                    ],
                    yAxis: [
                        {
                            // Secondary yAxis
                            title: {
                                text: 'Unreviewed',
                                style: {
                                    color: '#FFF',
                                    fontWeight: 100,
                                    textTransform: 'uppercase',
                                },
                            },
                            labels: {
                                style: {
                                    color: '#AAA',
                                    fontWeight: 100,
                                },
                            },
                            opposite: true,
                            gridLineWidth: 0,
                        },
                        {
                            // Primary yAxis
                            title: {
                                text: 'Suggestions',
                                style: {
                                    color: '#FFF',
                                    fontWeight: 100,
                                    textTransform: 'uppercase',
                                },
                            },
                            labels: {
                                format: '{value}',
                                style: {
                                    color: '#AAA',
                                    fontWeight: 100,
                                },
                            },
                            gridLineWidth: 0,
                        },
                    ],
                    tooltip: {
                        backgroundColor: '#272A2F',
                        formatter: function () {
                            var formatter = new Intl.DateTimeFormat('en-GB', {
                                month: 'long',
                                year: 'numeric',
                            });

                            var s =
                                '<b>' +
                                formatter.format(new Date(this.x)) +
                                '</b>';
                            var points = this.points;

                            $.each(points, function (i, point) {
                                var percent = '';
                                var share = null;
                                var total = 0;

                                if (point.series.name === 'Peer-approved') {
                                    total = point.y + points[i + 2].y;
                                    if (total !== 0) {
                                        share = point.y / total;
                                    }
                                    percent =
                                        ' (' +
                                        Math.floor(share * 100) +
                                        '% of peer-reviews)';
                                }
                                if (point.series.name === 'Self-approved') {
                                    total = point.y + points[i - 1].y;
                                    if (total !== 0) {
                                        share = point.y / total;
                                    }
                                    percent =
                                        ' (' +
                                        Math.floor(share * 100) +
                                        '% of all approvals)';
                                }
                                if (point.series.name === 'Rejected') {
                                    total = point.y + points[i - 2].y;
                                    if (total !== 0) {
                                        share = point.y / total;
                                    }
                                    percent =
                                        ' (' +
                                        Math.floor(share * 100) +
                                        '% of peer-reviews)';
                                }

                                s +=
                                    '<br/><span style="color:' +
                                    point.color +
                                    '">\u25CF</span> ' +
                                    point.series.name +
                                    ': ' +
                                    point.y +
                                    percent;
                            });

                            return s;
                        },
                        shared: true,
                        style: {
                            color: '#FFF',
                        },
                    },
                    legend: {
                        align: 'center',
                        itemHiddenStyle: {
                            color: '#4d5967',
                        },
                        itemHoverStyle: {
                            color: '#FFF',
                        },
                        itemStyle: {
                            color: '#FFF',
                            fontWeight: 700,
                        },
                    },
                    plotOptions: {
                        areaspline: {
                            fillColor: {
                                linearGradient: [0, 0, 0, 250],
                                stops: [
                                    [
                                        0,
                                        Highcharts.color('#4fc4f6')
                                            .setOpacity(0.5)
                                            .get('rgba'),
                                    ],
                                    [1, 'transparent'],
                                ],
                            },
                        },
                        column: {
                            borderWidth: 0,
                            stacking: 'normal',
                        },
                    },
                    series: [
                        {
                            name: 'Unreviewed',
                            type: 'areaspline',
                            data: reviewActivity.data('unreviewed'),
                        },
                        {
                            name: 'Peer-approved',
                            type: 'column',
                            yAxis: 1,
                            data: reviewActivity.data('peer-approved'),
                            stack: 'Reviews',
                        },
                        {
                            name: 'Self-approved',
                            type: 'column',
                            yAxis: 1,
                            data: reviewActivity.data('self-approved'),
                            stack: 'Reviews',
                        },
                        {
                            name: 'Rejected',
                            type: 'column',
                            yAxis: 1,
                            data: reviewActivity.data('rejected'),
                            stack: 'Reviews',
                        },
                        {
                            name: 'New suggestions',
                            type: 'column',
                            yAxis: 1,
                            data: reviewActivity.data('new-suggestions'),
                            visible: false,
                        },
                    ],
                });
            },
        },
    });
})(Pontoon || {});
