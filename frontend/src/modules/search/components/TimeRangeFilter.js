/* @flow */

import * as React from 'react';

import date from 'date-and-time';
import { Localized } from '@fluent/react';
import cloneDeep from 'lodash.clonedeep';

import Highcharts from 'highcharts/highstock';
import highchartsStock from 'highcharts/modules/stock';
import HighchartsReact from 'highcharts-react-official';

import './TimeRangeFilter.css';

import { CHART_OPTIONS } from './chart-options.js';

import type { TimeRangeType } from '..';

const INPUT_FORMAT = 'DD/MM/YYYY HH:mm';
const URL_FORMAT = 'YYYYMMDDHHmm';

type Props = {|
    project: string,
    timeRange: ?TimeRangeType,
    timeRangeData: Array<Array<number>>,
    applySingleFilter: (filter: string, type: string) => void,
    toggleFilter: (
        filter: string,
        type: string,
        event: SyntheticMouseEvent<>,
    ) => void,
    updateTimeRange: (filter: string) => void,
|};

type State = {|
    chartFrom: ?number,
    chartTo: ?number,
    chartOptions: {
        series: Array<{
            data: Array<any>,
        }>,
        xAxis: Array<{
            events: {
                setExtremes: ?({ min: number, max: number }) => void,
            },
        }>,
    },
    inputFrom: string,
    inputTo: string,
    visible: boolean,
|};

/**
 * Shows a Time Range filter panel.
 */
export default class TimeRangeFilterBase extends React.Component<Props, State> {
    chart: { current: any };

    constructor(props: Props) {
        super(props);

        this.state = {
            chartFrom: null,
            chartTo: null,
            chartOptions: CHART_OPTIONS,
            inputFrom: '',
            inputTo: '',
            visible: false,
        };

        this.initializeChart();

        this.chart = React.createRef();
    }

    componentDidUpdate(prevProps: Props, prevState: State) {
        const props = this.props;
        const state = this.state;

        if (props.timeRangeData !== prevProps.timeRangeData) {
            this.plotChart();
        }

        if (state.visible !== prevState.visible) {
            this.updateChartExtremes();
        }

        // When filters are toggled or applied, we update the filters state in the SearchBox
        // component, so that we can request entities accordingly. But the Time Range filter
        // state also changes when chartFrom and chartTo values change, so when that happens,
        // we also need to propagate changes to the SearchBox state.
        // Without this code, if you have Time Range filter applied and then change range and
        // click the Apply Filter button, nothing happens. As described in bug 1469611.
        const { chartFrom, chartTo } = state;
        if (
            props.timeRange &&
            (chartFrom !== prevState.chartFrom || chartTo !== prevState.chartTo)
        ) {
            props.updateTimeRange([chartFrom, chartTo].join('-'));
        }
    }

    initializeChart = () => {
        // Initialize the highchartsStock module
        highchartsStock(Highcharts);

        // Set global options
        Highcharts.setOptions({
            lang: {
                rangeSelectorZoom: '',
            },
        });
    };

    updateChartExtremes = (key: ?string, value: ?number) => {
        const { chartFrom, chartTo } = this.state;

        if (!chartFrom || !chartTo) {
            return;
        }

        if (!this.chart.current) {
            return;
        }

        let extremes = {
            chartFrom: date
                .parse(chartFrom.toString(), URL_FORMAT, true)
                .getTime(),
            chartTo: date.parse(chartTo.toString(), URL_FORMAT, true).getTime(),
        };

        if (key && value) {
            extremes[key] = value;
        }

        this.chart.current.chart.xAxis[0].setExtremes(
            extremes.chartFrom,
            extremes.chartTo,
        );
    };

    plotChart = () => {
        const { timeRange, timeRangeData } = this.props;

        // In case of no translations
        if (timeRangeData.length === 0) {
            return null;
        }

        // Set default chart boundaries (full chart)
        let chartFrom = this.getTimeForURL(timeRangeData[0][0]);
        let chartTo = this.getTimeForURL(
            timeRangeData[timeRangeData.length - 1][0],
        );

        // Set chart boundaries from the URL parameter if given
        if (timeRange) {
            chartFrom = timeRange.from;
            chartTo = timeRange.to;
        }

        // Set chart data
        const chartOptions = cloneDeep(this.state.chartOptions);
        chartOptions.series[0].data = timeRangeData;

        // Set the callback function that fires when the minimum and maximum is set for the axis,
        // either by calling the .setExtremes() method or by selecting an area in the chart.
        chartOptions.xAxis[0].events.setExtremes = (event) => {
            const chartFrom = this.getTimeForURL(event.min);
            const chartTo = this.getTimeForURL(event.max);

            this.setState({
                chartFrom,
                chartTo,
                inputFrom: this.getTimeForInput(chartFrom),
                inputTo: this.getTimeForInput(chartTo),
            });
        };

        this.setState({
            chartFrom,
            chartTo,
            chartOptions,
            inputFrom: this.getTimeForInput(chartFrom),
            inputTo: this.getTimeForInput(chartTo),
        });
    };

    getTimeForURL = (unixTime: number) => {
        const d = new Date(unixTime);

        return parseInt(date.format(d, URL_FORMAT, true));
    };

    getTimeForInput = (urlTime: ?number) => {
        if (!urlTime) {
            return '';
        }

        const d = date.parse(urlTime.toString(), URL_FORMAT, true);

        if (isNaN(d)) {
            return urlTime.toString();
        }

        return date.format(d, INPUT_FORMAT);
    };

    isValidInput = (value: string) => {
        return date.isValid(value, INPUT_FORMAT);
    };

    handleInputChange = (event: SyntheticInputEvent<HTMLInputElement>) => {
        const name = event.target.name;
        const value = event.target.value;

        if (this.isValidInput(value)) {
            const d = date.parse(value, INPUT_FORMAT);
            this.updateChartExtremes('chart' + name, d.getTime());
        }

        this.setState({
            ['input' + name]: value,
        });
    };

    toggleEditingTimeRange = (event: SyntheticMouseEvent<>) => {
        const { chartFrom, chartTo, visible } = this.state;

        // After Save Range is clicked...
        if (visible) {
            // Make sure Time Range filter is selected
            if (!this.props.timeRange) {
                this.props.toggleFilter(
                    [chartFrom, chartTo].join('-'),
                    'timeRange',
                    event,
                );
            }

            // Make sure inputs are in sync with chart
            this.setState((state) => {
                return {
                    inputFrom: this.getTimeForInput(state.chartFrom),
                    inputTo: this.getTimeForInput(state.chartTo),
                };
            });
        }

        this.setState((state) => {
            return { visible: !state.visible };
        });
    };

    toggleTimeRangeFilter = (event: SyntheticMouseEvent<>) => {
        const { chartFrom, chartTo, visible } = this.state;

        if (visible) {
            return;
        }

        this.props.toggleFilter(
            [chartFrom, chartTo].join('-'),
            'timeRange',
            event,
        );
    };

    applyTimeRangeFilter = () => {
        const { chartFrom, chartTo, visible } = this.state;

        if (visible) {
            return;
        }

        this.props.applySingleFilter(
            [chartFrom, chartTo].join('-'),
            'timeRange',
        );
    };

    render() {
        const props = this.props;

        // In case of no translations or the All Projects view
        if (
            props.timeRangeData.length === 0 ||
            props.project === 'all-projects'
        ) {
            return null;
        }

        let timeRangeClass = 'time-range clearfix';
        if (this.state.visible) {
            timeRangeClass += ' editing';
        }
        if (props.timeRange) {
            timeRangeClass += ' selected';
        }

        return (
            <>
                <li className='horizontal-separator for-time-range'>
                    <Localized id='search-TimeRangeFilter--heading-time'>
                        <span>TRANSLATION TIME</span>
                    </Localized>

                    {!this.state.visible ? (
                        <Localized
                            id='search-TimeRangeFilter--edit-range'
                            elems={{
                                glyph: <i className='fa fa-chart-area' />,
                            }}
                        >
                            <button
                                onClick={this.toggleEditingTimeRange}
                                className='edit-range'
                            >
                                {'<glyph></glyph>EDIT RANGE'}
                            </button>
                        </Localized>
                    ) : (
                        <Localized id='search-TimeRangeFilter--save-range'>
                            <button
                                onClick={this.toggleEditingTimeRange}
                                className='save-range'
                            >
                                SAVE RANGE
                            </button>
                        </Localized>
                    )}
                </li>
                <li
                    className={`${timeRangeClass}`}
                    onClick={this.applyTimeRangeFilter}
                >
                    <span
                        className='status fa'
                        onClick={this.toggleTimeRangeFilter}
                    ></span>

                    <span className='clearfix'>
                        <label className='from'>
                            From
                            <input
                                type='datetime'
                                name='From'
                                className={
                                    this.isValidInput(this.state.inputFrom)
                                        ? ''
                                        : 'error'
                                }
                                disabled={!this.state.visible}
                                onChange={this.handleInputChange}
                                value={this.state.inputFrom}
                            />
                        </label>
                        <label className='to'>
                            To
                            <input
                                type='datetime'
                                name='To'
                                className={
                                    this.isValidInput(this.state.inputTo)
                                        ? ''
                                        : 'error'
                                }
                                disabled={!this.state.visible}
                                onChange={this.handleInputChange}
                                value={this.state.inputTo}
                            />
                        </label>
                    </span>

                    {!this.state.visible ? null : (
                        <HighchartsReact
                            highcharts={Highcharts}
                            options={this.state.chartOptions}
                            constructorType={'stockChart'}
                            allowChartUpdate={false}
                            containerProps={{ className: 'chart' }}
                            ref={this.chart}
                        />
                    )}
                </li>
            </>
        );
    }
}
