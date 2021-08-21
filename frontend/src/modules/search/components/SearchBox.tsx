import * as React from 'react';
import { useStore } from 'react-redux';
import isEqual from 'lodash.isequal';

import './SearchBox.css';

import { useAppDispatch, useAppSelector } from 'hooks';
import * as editor from 'core/editor';
import * as navigation from 'core/navigation';
import { NAME as PROJECT_NAME } from 'core/project';
import { NAME as STATS_NAME } from 'core/stats';
import * as search from 'modules/search';
import * as unsavedchanges from 'modules/unsavedchanges';

import { FILTERS_STATUS, FILTERS_EXTRA } from '../constants';
import FiltersPanel from './FiltersPanel';

import type { NavigationParams } from 'core/navigation';
import type { ProjectState } from 'core/project';
import type { Stats } from 'core/stats';
import type { SearchAndFilters } from 'modules/search';

export type TimeRangeType = {
    from: number;
    to: number;
};

type Props = {
    searchAndFilters: SearchAndFilters;
    parameters: NavigationParams;
    project: ProjectState;
    stats: Stats;
    router: Record<string, any>;
};

type InternalProps = Props & {
    store: Record<string, any>;
    dispatch: (...args: Array<any>) => any;
};

type State = {
    search: string;
    statuses: Record<string, boolean>;
    extras: Record<string, boolean>;
    tags: Record<string, boolean>;
    timeRange: TimeRangeType | null | undefined;
    authors: Record<string, boolean>;
};

/**
 * Shows and controls a search box, used to filter the list of entities.
 *
 * Changes to the search input will be reflected in the URL.
 */
export class SearchBoxBase extends React.Component<InternalProps, State> {
    searchInput: React.RefObject<HTMLInputElement>;

    constructor(props: InternalProps) {
        super(props);

        this.state = {
            search: '',
            statuses: {},
            extras: {},
            tags: {},
            timeRange: null,
            authors: {},
        };

        this.searchInput = React.createRef();
    }

    updateFiltersFromURLParams: () => void = () => {
        const props = this.props;

        const statuses = this.getInitialStatuses();
        if (props.parameters.status) {
            props.parameters.status.split(',').forEach((f) => {
                statuses[f] = true;
            });
        }

        const extras = this.getInitialExtras();
        if (props.parameters.extra) {
            props.parameters.extra.split(',').forEach((f) => {
                extras[f] = true;
            });
        }

        const tags = this.getInitialTags();
        if (props.parameters.tag) {
            props.parameters.tag.split(',').forEach((f) => {
                tags[f] = true;
            });
        }

        let timeRange = null;
        if (props.parameters.time) {
            timeRange = this.getTimeRangeFromURLParameter(
                props.parameters.time,
            );
        }

        const authors = this.getInitialAuthors();
        if (props.parameters.author) {
            props.parameters.author.split(',').forEach((f) => {
                authors[f] = true;
            });
        }

        this.setState({
            statuses,
            extras,
            tags,
            timeRange,
            authors,
        });
    };

    componentDidMount() {
        document.addEventListener('keydown', this.handleShortcuts);
        this.updateFiltersFromURLParams();

        // On mount, update the search input content based on URL.
        // This is not in the `updateFiltersFromURLParams` method because we want to
        // do this *only* on mount. The behavior is slightly different on update.
        const searchParam = this.props.parameters.search;
        this.setState({
            search: searchParam ? searchParam.toString() : '',
        });
    }

    componentDidUpdate(prevProps: InternalProps) {
        // Clear search field when navigating to a new file
        if (
            this.props.parameters.search === null &&
            prevProps.parameters.search !== null
        ) {
            this.setState({
                search: '',
            });
        }

        // When the URL changes, for example from links in the ResourceProgress
        // component, reload the filters from the URL parameters.
        if (this.props.parameters !== prevProps.parameters) {
            this.updateFiltersFromURLParams();
        }
    }

    componentWillUnmount() {
        document.removeEventListener('keydown', this.handleShortcuts);
    }

    getTimeRangeFromURLParameter(timeParameter: string): TimeRangeType {
        const boundaries = timeParameter.split('-');

        return {
            from: parseInt(boundaries[0]),
            to: parseInt(boundaries[1]),
        };
    }

    getInitialStatuses(): Record<string, boolean> {
        const statuses = {};
        FILTERS_STATUS.forEach((s) => (statuses[s.slug] = false));
        return statuses;
    }

    getInitialExtras(): Record<string, boolean> {
        const extras = {};
        FILTERS_EXTRA.forEach((e) => (extras[e.slug] = false));
        return extras;
    }

    getInitialTags(): Record<string, boolean> {
        const tags = {};
        this.props.project.tags.forEach((t) => (tags[t.slug] = false));
        return tags;
    }

    getInitialAuthors(): Record<string, boolean> {
        const authors = {};
        this.props.searchAndFilters.authors.forEach(
            (a) => (authors[a.email] = false),
        );
        return authors;
    }

    getSelectedStatuses(): Array<string> {
        return Object.keys(this.state.statuses).filter(
            (s) => this.state.statuses[s],
        );
    }

    getSelectedExtras(): Array<string> {
        return Object.keys(this.state.extras).filter(
            (e) => this.state.extras[e],
        );
    }

    getSelectedTags(): Array<string> {
        return Object.keys(this.state.tags).filter((t) => this.state.tags[t]);
    }

    getSelectedTimeRange(): TimeRangeType | null | undefined {
        return this.state.timeRange;
    }

    getSelectedAuthors(): Array<string> {
        return Object.keys(this.state.authors).filter(
            (a) => this.state.authors[a],
        );
    }

    updateTimeRange: (filter: string) => void = (filter: string) => {
        let timeRange = this.getTimeRangeFromURLParameter(filter);

        this.setState({
            timeRange,
        });
    };

    toggleFilter: (filter: string, type: string) => void = (
        filter: string,
        type: string,
    ) => {
        if (type === 'timeRange') {
            let timeRange = this.getTimeRangeFromURLParameter(filter);

            if (isEqual(timeRange, this.state.timeRange)) {
                timeRange = null;
            }

            return this.setState({ timeRange });
        }

        // @ts-expect-error
        this.setState((state) => {
            return {
                [type]: {
                    ...state[type],
                    [filter]: !state[type][filter],
                },
            };
        });
    };

    applySingleFilter: (
        filter: string,
        type: string,
        callback?: () => void,
    ) => void = (filter: string, type: string, callback?: () => void) => {
        const statuses = this.getInitialStatuses();
        const extras = this.getInitialExtras();
        const tags = this.getInitialTags();
        let timeRange = null;
        const authors = this.getInitialAuthors();

        if (filter !== 'all') {
            switch (type) {
                case 'statuses':
                    statuses[filter] = true;
                    break;
                case 'extras':
                    extras[filter] = true;
                    break;
                case 'tags':
                    tags[filter] = true;
                    break;
                case 'timeRange':
                    timeRange = this.getTimeRangeFromURLParameter(filter);
                    break;
                case 'authors':
                    authors[filter] = true;
                    break;
                default:
            }
        }

        if (callback) {
            this.setState(
                {
                    statuses,
                    extras,
                    tags,
                    timeRange,
                    authors,
                },
                callback,
            );
        } else {
            this.setState({
                statuses,
                extras,
                tags,
                timeRange,
                authors,
            });
        }
    };

    resetFilters: () => void = () => {
        this.setState({
            statuses: this.getInitialStatuses(),
            extras: this.getInitialExtras(),
            tags: this.getInitialTags(),
            timeRange: null,
            authors: this.getInitialAuthors(),
        });
    };

    getAuthorsAndTimeRangeData: () => void = () => {
        const { locale, project, resource } = this.props.parameters;

        this.props.dispatch(
            search.actions.getAuthorsAndTimeRangeData(
                locale,
                project,
                resource,
            ),
        );
    };

    handleShortcuts: (event: KeyboardEvent) => void = (
        event: KeyboardEvent,
    ) => {
        const key = event.keyCode;

        // On Ctrl + Shift + F, set focus on the search input.
        if (key === 70 && !event.altKey && event.ctrlKey && event.shiftKey) {
            event.preventDefault();
            if (this.searchInput.current) {
                this.searchInput.current.focus();
            }
        }
    };

    unsetFocus: () => void = () => {
        this.props.dispatch(search.actions.setFocus(false));
    };

    setFocus: () => void = () => {
        this.props.dispatch(search.actions.setFocus(true));
    };

    updateSearchInput: (
        event: React.SyntheticEvent<HTMLInputElement>,
    ) => void = (event: React.SyntheticEvent<HTMLInputElement>) => {
        this.setState({
            search: event.currentTarget.value,
        });
    };

    handleKeyDown: (event: React.KeyboardEvent<HTMLInputElement>) => void = (
        event: React.KeyboardEvent<HTMLInputElement>,
    ) => {
        // Perform search on Enter
        if (event.keyCode === 13) {
            this.update();
        }
    };

    _update: () => void = () => {
        const statuses = this.getSelectedStatuses();
        let status = statuses.join(',');

        if (status === 'all') {
            status = null;
        }

        const extras = this.getSelectedExtras();
        const extra = extras.join(',');

        const tags = this.getSelectedTags();
        const tag = tags.join(',');

        const timeRange = this.getSelectedTimeRange();
        const time = timeRange ? [timeRange.from, timeRange.to].join('-') : '';

        const authors = this.getSelectedAuthors();
        const author = authors.join(',');

        this.props.dispatch(editor.actions.reset());
        this.props.dispatch(
            navigation.actions.update(this.props.router, {
                search: this.state.search,
                status,
                extra,
                tag,
                time,
                author,
            }),
        );
    };

    update: () => void = () => {
        const state = this.props.store.getState();
        const unsavedChangesExist = state[unsavedchanges.NAME].exist;
        const unsavedChangesIgnored = state[unsavedchanges.NAME].ignored;

        this.props.dispatch(
            unsavedchanges.actions.check(
                unsavedChangesExist,
                unsavedChangesIgnored,
                this._update,
            ),
        );
    };

    composePlaceholder(): string {
        const statuses = this.getSelectedStatuses();
        const selectedStatuses = FILTERS_STATUS.filter((f) =>
            statuses.includes(f.slug),
        );

        const extras = this.getSelectedExtras();
        const selectedExtras = FILTERS_EXTRA.filter((f) =>
            extras.includes(f.slug),
        );

        const tags = this.getSelectedTags();
        const selectedTags = this.props.project.tags.filter((f) =>
            tags.includes(f.slug),
        );

        const authors = this.getSelectedAuthors();
        const selectedAuthors = this.props.searchAndFilters.authors.filter(
            (f) => authors.includes(f.email),
        );

        const selectedFilters = [].concat(
            selectedStatuses,
            selectedExtras,
            selectedTags,
        );

        let selectedFiltersNames = selectedFilters.map((item) => item.name);

        // Special case for Translation Time filter
        if (this.getSelectedTimeRange()) {
            selectedFiltersNames = selectedFiltersNames.concat(['Time Range']);
        }

        // Special case for Translation Authors filters
        if (selectedAuthors.length) {
            selectedFiltersNames = selectedFiltersNames.concat(
                selectedAuthors.map(
                    (item) => item.display_name + "'s translations",
                ),
            );
        }

        let selectedFiltersString = 'All';
        if (selectedFiltersNames.length) {
            selectedFiltersString = selectedFiltersNames.join(', ');
        }

        return `Search in ${selectedFiltersString}`;
    }

    render(): React.ReactElement<'div'> {
        const { searchAndFilters, parameters, project, stats } = this.props;

        return (
            <div className='search-box clearfix'>
                <label htmlFor='search'>
                    <div className='fa fa-search'></div>
                </label>
                <input
                    id='search'
                    ref={this.searchInput}
                    autoComplete='off'
                    placeholder={this.composePlaceholder()}
                    title='Search Strings (Ctrl + Shift + F)'
                    type='search'
                    value={this.state.search}
                    onBlur={this.unsetFocus}
                    onChange={this.updateSearchInput}
                    onFocus={this.setFocus}
                    onKeyDown={this.handleKeyDown}
                />
                <FiltersPanel
                    statuses={this.state.statuses}
                    extras={this.state.extras}
                    tags={this.state.tags}
                    timeRange={this.state.timeRange}
                    authors={this.state.authors}
                    tagsData={project.tags}
                    timeRangeData={searchAndFilters.countsPerMinute}
                    authorsData={searchAndFilters.authors}
                    stats={stats}
                    parameters={parameters}
                    applySingleFilter={this.applySingleFilter}
                    getAuthorsAndTimeRangeData={this.getAuthorsAndTimeRangeData}
                    resetFilters={this.resetFilters}
                    toggleFilter={this.toggleFilter}
                    update={this.update}
                    updateTimeRange={this.updateTimeRange}
                    updateFiltersFromURLParams={this.updateFiltersFromURLParams}
                />
            </div>
        );
    }
}

export default function SearchBox(): React.ReactElement<typeof SearchBoxBase> {
    const state = {
        searchAndFilters: useAppSelector((state) => state[search.NAME]),
        parameters: useAppSelector((state) =>
            navigation.selectors.getNavigationParams(state),
        ),
        project: useAppSelector((state) => state[PROJECT_NAME]),
        stats: useAppSelector((state) => state[STATS_NAME]),
        router: useAppSelector((state) => state.router),
    };

    return (
        <SearchBoxBase
            {...state}
            dispatch={useAppDispatch()}
            store={useStore()}
        />
    );
}
