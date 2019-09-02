/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';

import date from 'date-and-time';
import { Localized } from 'fluent-react';
import cloneDeep from 'lodash.clonedeep';

import Highcharts from 'highcharts/highstock'
import highchartsStock from "highcharts/modules/stock";
import HighchartsReact from 'highcharts-react-official'

import './FiltersPanel.css';

import { FILTERS_STATUS, FILTERS_EXTRA } from '..';
import { CHART_OPTIONS } from './chart-options.js';

import { asLocaleString } from 'core/utils';

import type { TimeRangeType } from '..';
import type { NavigationParams } from 'core/navigation';
import type { Tag } from 'core/project';
import type { Stats } from 'core/stats';
import type { Author } from 'modules/search';


const INPUT_FORMAT = 'DD/MM/YYYY HH:mm';
const URL_FORMAT = 'YYYYMMDDHHmm';


type Props = {|
    statuses: { [string]: boolean },
    extras: { [string]: boolean },
    tags: { [string]: boolean },
    timeRange: ?TimeRangeType,
    authors: { [string]: boolean },
    tagsData: Array<Tag>,
    timeRangeData: Array<Array<number>>,
    authorsData: Array<Author>,
    stats: Stats,
    parameters: NavigationParams,
    applySingleFilter: (filter: string, type: string, callback?: () => void) => void,
    getAuthorsAndTimeRangeData: () => void,
    resetFilters: () => void,
    toggleFilter: (string, string) => void,
    update: () => void,
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
                setExtremes: ?({min: number, max: number}) => void,
            },
        }>,
    },
    isChartVisible: boolean,
    visible: boolean,
|};


/**
 * Shows a list of filters used to filter the list of entities.
 *
 * Changes to the filters will be reflected in the URL.
 */
export class FiltersPanelBase extends React.Component<Props, State> {
    chart: { current: any };
    menu: { current: ?HTMLDivElement };

    constructor(props: Props) {
        super(props);

        this.state = {
            chartFrom: null,
            chartTo: null,
            chartOptions: CHART_OPTIONS,
            isChartVisible: false,
            visible: false,
        };

        this.initializeChart();

        this.chart = React.createRef();
        this.menu = React.createRef();
    }

    componentDidUpdate(prevProps: Props, prevState: State) {
        const props = this.props;
        const state = this.state;

        if (
            state.visible &&
            !prevState.visible &&
            props.parameters.project !== 'all-projects'
        ) {
            props.getAuthorsAndTimeRangeData();
        }

        if (props.timeRangeData !== prevProps.timeRangeData) {
            this.plotChart();
        }

        if (state.isChartVisible !== prevState.isChartVisible) {
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
            ((chartFrom !== prevState.chartFrom) ||
            (chartTo !== prevState.chartTo))
        ) {
            props.updateTimeRange([chartFrom, chartTo].join('-'));
        }
    }

    initializeChart = () => {
        // Initialize the highchartsStock module
        highchartsStock(Highcharts);

        // Set global options
        Highcharts.setOptions({
            lang:{
                rangeSelectorZoom: '',
            }
        });
    }

    updateChartExtremes = (key: ?string, value: ?number) => {
        const { chartFrom, chartTo } = this.state;

        if (!chartFrom || !chartTo) {
            return;
        }

        if (!this.chart.current) {
            return;
        }

        let extremes = {
            chartFrom: date.parse(chartFrom.toString(), URL_FORMAT, true).getTime(),
            chartTo: date.parse(chartTo.toString(), URL_FORMAT, true).getTime(),
        };

        if (key && value) {
            extremes[key] = value;
        }

        this.chart.current.chart.xAxis[0].setExtremes(
            extremes.chartFrom,
            extremes.chartTo,
        );
    }

    plotChart = () => {
        const { timeRange, timeRangeData } = this.props;

        // Set chart boundaries
        let chartFrom = this.getTimeForURL(timeRangeData[0][0]);
        let chartTo = this.getTimeForURL(timeRangeData[timeRangeData.length - 1][0]);

        if (timeRange) {
            chartFrom = timeRange.from;
            chartTo = timeRange.to;
        }

        // Set chart data
        const chartOptions = cloneDeep(this.state.chartOptions);
        chartOptions.series[0].data = timeRangeData;

        // Set chart update function
        chartOptions.xAxis[0].events.setExtremes = event => {
            this.setState({
                chartFrom: this.getTimeForURL(event.min),
                chartTo: this.getTimeForURL(event.max),
            });
        };

        this.setState({
            chartFrom,
            chartTo,
            chartOptions,
        });
    }

    getTimeForURL = (unixTime: number) => {
        const d = new Date(unixTime);

        return parseInt(date.format(d, URL_FORMAT, true));
    }

    getTimeForInput = (urlTime: ?number) => {
        if (!urlTime) {
            return '';
        }

        const d = date.parse(urlTime.toString(), URL_FORMAT, true);

        if (isNaN(d)) {
            return urlTime;
        }

        return date.format(d, INPUT_FORMAT);
    }

    handleInputChange = (event: SyntheticInputEvent<HTMLInputElement>) => {
        const d = date.parse(event.target.value, INPUT_FORMAT);

        // If valid date, update chart extremes
        if (!isNaN(d)) {
            this.updateChartExtremes(event.target.name, d.getTime());
            event.target.classList.remove('error');
        }
        else {
            event.target.classList.add('error');
        }
    }

    toggleEditingTimeRange = () => {
        this.setState(state => {
            return { isChartVisible: !state.isChartVisible };
        });
    }

    toggleVisibility = () => {
        this.setState(state => {
            return { visible: !state.visible };
        });
    }

    applyFilters = () => {
        this.toggleVisibility();
        return this.props.update();
    }

    toggleTimeRangeFilter = (event: SyntheticMouseEvent<>) => {
        const { chartFrom, chartTo, isChartVisible } = this.state;

        if (isChartVisible) {
            return;
        }

        this.toggleFilter([chartFrom, chartTo].join('-'), 'timeRange', event);
    }

    createToggleFilter = (filter: string, type: string) => {
        if (filter === 'all') {
            return null;
        }

        return (event: SyntheticMouseEvent<>) => {
            event.stopPropagation();
            this.toggleFilter(filter, type, event);
        };
    }

    toggleFilter(filter: string, type: string, event: SyntheticMouseEvent<>) {
        event.stopPropagation();
        this.props.toggleFilter(filter, type);
    }

    applyTimeRangeFilter = () => {
        const { chartFrom, chartTo, isChartVisible } = this.state;

        if (isChartVisible) {
            return;
        }

        this.applySingleFilter([chartFrom, chartTo].join('-'), 'timeRange');
    }

    createApplySingleFilter(filter: string, type: string) {
        return () => {
            this.applySingleFilter(filter, type);
        };
    }

    applySingleFilter(filter: string, type: string) {
        this.toggleVisibility();
        this.props.applySingleFilter(filter, type, this.props.update);
    }

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the search panel.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    }

    render() {
        const props = this.props;
        const { project, resource } = this.props.parameters;

        const selectedStatuses = Object.keys(props.statuses).filter(s => props.statuses[s]);
        const selectedExtras = Object.keys(props.extras).filter(e => props.extras[e]);
        const selectedTags = Object.keys(props.tags).filter(t => props.tags[t]);
        const selectedTimeRangeCount = props.timeRange ? 1 : 0;
        const selectedAuthors = Object.keys(props.authors).filter(a => props.authors[a]);

        const selectedFiltersCount = (
            selectedExtras.length +
            selectedStatuses.length +
            selectedTags.length +
            selectedTimeRangeCount +
            selectedAuthors.length
        );

        // If there are zero or several selected statuses, show the "All" icon.
        let filterIcon = 'all';

        // Otherwise show the approriate status icon.
        if (selectedFiltersCount === 1) {
            const selectedStatus = FILTERS_STATUS.find(f => f.slug === selectedStatuses[0]);
            if (selectedStatus) {
                filterIcon = selectedStatus.slug;
            }

            const selectedExtra = FILTERS_EXTRA.find(f => f.slug === selectedExtras[0]);
            if (selectedExtra) {
                filterIcon = selectedExtra.slug;
            }

            const selectedTag = props.tagsData.find(f => f.slug === selectedTags[0]);
            if (selectedTag) {
                filterIcon = 'tag';
            }

            if (selectedTimeRangeCount) {
                filterIcon = 'time-range';
            }

            const selectedAuthor = props.authorsData.find(f => f.email === selectedAuthors[0]);
            if (selectedAuthor) {
                filterIcon = 'author';
            }
        }

        let timeRangeClass = 'time-range clearfix';
        if (this.state.isChartVisible) {
            timeRangeClass += ' editing';
        }
        if (props.timeRange) {
            timeRangeClass += ' selected';
        }

        const menu = this.menu.current;
        let isScrollbarVisible = false;
        if (menu) {
            isScrollbarVisible = menu.scrollHeight > menu.clientHeight;
        }

        let isFixed = '';
        if (selectedFiltersCount > 0 && isScrollbarVisible) {
            isFixed = 'fixed';
        }

         return <div className={ `filters-panel ${isFixed}` }>
            <div
                className={ `visibility-switch ${filterIcon}` }
                onClick={ this.toggleVisibility }
            >
                <span className="status fa"></span>
            </div>
            { !this.state.visible ? null : <div className="menu" ref={ this.menu }>
                <ul>
                    <Localized id="search-FiltersPanel--heading-status">
                        <li className="horizontal-separator">Translation Status</li>
                    </Localized>

                    { FILTERS_STATUS.map((status, i) => {
                        const count = status.stat ? props.stats[status.stat] : props.stats[status.slug];
                        const selected = props.statuses[status.slug];

                        let className = status.slug;
                        if (selected && status.slug !== 'all') {
                            className += ' selected';
                        }

                        return <li
                            className={ className }
                            key={ i }
                            onClick={ this.createApplySingleFilter(status.slug, 'statuses') }
                        >
                            <span
                                className="status fa"
                                onClick={ this.createToggleFilter(status.slug, 'statuses') }
                            ></span>
                            <span className="title">{ status.name }</span>
                            <span className="count">
                                { asLocaleString(count) }
                            </span>
                        </li>
                    }) }

                    { (props.tagsData.length === 0 || resource !== 'all-resources') ? null : <>
                        <Localized id="search-FiltersPanel--heading-tags">
                            <li className="horizontal-separator">Tags</li>
                        </Localized>

                        { props.tagsData.map((tag, i) => {
                            const selected = props.tags[tag.slug];

                            let className = tag.slug;
                            if (selected) {
                                className += ' selected';
                            }

                            return <li
                                className={ `tag ${className}` }
                                key={ i }
                                onClick={ this.createApplySingleFilter(tag.slug, 'tags') }
                            >
                                <span
                                    className="status fa"
                                    onClick={ this.createToggleFilter(tag.slug, 'tags') }
                                ></span>
                                <span className="title">{ tag.name }</span>
                                <span className="priority">
                                    { [1, 2, 3, 4, 5].map((index) => {
                                        const active = index < tag.priority ? 'active' : '';
                                        return <span
                                            className={ `fa fa-star ${active}` }
                                            key={ index }
                                        ></span>;
                                    }) }
                                </span>
                            </li>
                        }) }
                    </>}

                    <Localized id="search-FiltersPanel--heading-extra">
                        <li className="horizontal-separator">Extra Filters</li>
                    </Localized>

                    { FILTERS_EXTRA.map((extra, i) => {
                        const selected = props.extras[extra.slug];

                        let className = extra.slug;
                        if (selected) {
                            className += ' selected';
                        }

                        return <li
                            className={ className }
                            key={ i }
                            onClick={ this.createApplySingleFilter(extra.slug, 'extras') }
                        >
                            <span
                                className="status fa"
                                onClick={ this.createToggleFilter(extra.slug, 'extras') }
                            ></span>
                            <span className="title">{ extra.name }</span>
                        </li>
                    }) }

                    { (props.timeRangeData.length === 0 || project === 'all-projects') ? null : <>
                        <li className="horizontal-separator for-time-range">
                            <Localized id="search-FiltersPanel--heading-time">
                                <span>Translation Time</span>
                            </Localized>

                            { !this.state.isChartVisible ?
                                <Localized
                                    id="search-FiltersPanel--edit-range"
                                    glyph={ <i className="fa fa-chart-area"></i> }
                                >
                                    <button
                                        onClick={ this.toggleEditingTimeRange }
                                        className="edit-range"
                                    >
                                        { '<glyph></glyph>Edit Range' }
                                    </button>
                                </Localized>
                                :
                                <Localized
                                    id="search-FiltersPanel--save-range"
                                >
                                    <button
                                        onClick={ this.toggleEditingTimeRange }
                                        className="save-range"
                                    >
                                        Save Range
                                    </button>
                                </Localized>
                            }
                        </li>

                        <li
                            className={ `${timeRangeClass}` }
                            onClick={ this.applyTimeRangeFilter }
                        >
                            <span
                                className="status fa"
                                onClick={ this.toggleTimeRangeFilter }
                            ></span>

                            <span className="clearfix">
                                <label className="from">
                                    From
                                    <input
                                        type="datetime"
                                        name="chartFrom"
                                        disabled={ !this.state.isChartVisible }
                                        onChange={ this.handleInputChange }
                                        value={ this.getTimeForInput(this.state.chartFrom) }
                                    />
                                </label>
                                <label className="to">
                                    To
                                    <input
                                        type="datetime"
                                        name="chartTo"
                                        disabled={ !this.state.isChartVisible }
                                        onChange={ this.handleInputChange }
                                        value={ this.getTimeForInput(this.state.chartTo) }
                                    />
                                </label>
                            </span>

                            { !this.state.isChartVisible ? null :
                                <HighchartsReact
                                    highcharts={ Highcharts }
                                    options={ this.state.chartOptions }
                                    constructorType = { 'stockChart' }
                                    allowChartUpdate = { false }
                                    containerProps = {{ className: 'chart' }}
                                    ref={ this.chart }
                                />
                            }
                        </li>
                    </>}

                    { (props.authorsData.length === 0 || project === 'all-projects') ? null : <>
                        <Localized id="search-FiltersPanel--heading-authors">
                            <li className="horizontal-separator">Translation Authors</li>
                        </Localized>

                        { props.authorsData.map((author, i) => {
                            const selected = props.authors[author.email];

                            let className = 'author';
                            if (selected) {
                                className += ' selected';
                            }

                            return <li
                                className={ `${className}` }
                                key={ i }
                                onClick={ this.createApplySingleFilter(author.email, 'authors') }
                            >
                                <figure>
                                    <span className="sel">
                                        <span
                                            className="status fa"
                                            onClick={ this.createToggleFilter(author.email, 'authors') }
                                        ></span>
                                        <img
                                            alt=""
                                            className="rounded"
                                            src={ author.gravatar_url }
                                        />
                                    </span>
                                    <figcaption>
                                        <p className="name">{ author.display_name }</p>
                                        <p className="role">{ author.role }</p>
                                    </figcaption>
                                    <span className="count">
                                        { asLocaleString(author.translation_count) }
                                    </span>
                                </figure>
                            </li>
                        }) }
                    </>}
                </ul>

                { selectedFiltersCount === 0 ? null :
                <div className="toolbar clearfix">
                    <Localized
                        id="search-FiltersPanel--clear-selection"
                        attrs={ { title: true } }
                        glyph={ <i className="fa fa-times fa-lg"></i> }
                    >
                        <button
                            title="Uncheck selected filters"
                            onClick={ this.props.resetFilters }
                            className="clear-selection"
                        >
                            { '<glyph></glyph>Clear' }
                        </button>
                    </Localized>
                    <Localized
                        id="search-FiltersPanel--apply-filters"
                        attrs={ { title: true } }
                        glyph={ <i className="fa fa-check fa-lg"></i> }
                        stress={ <span className="applied-count"></span> }
                        $count={ selectedFiltersCount }
                    >
                        <button
                            title="Apply Selected Filters"
                            onClick={ this.applyFilters }
                            className="apply-selected"
                        >
                            { '<glyph></glyph>Apply <stress>{ $count }</stress> filters' }
                        </button>
                    </Localized>
                </div> }
            </div> }
        </div>;
    }
}


export default onClickOutside(FiltersPanelBase);
