/* @flow */

import * as React from 'react';

import { Localized } from '@fluent/react';

import './FiltersPanel.css';

import { FILTERS_STATUS, FILTERS_EXTRA } from '../constants';
import TimeRangeFilter from './TimeRangeFilter';

import { asLocaleString, useOnDiscard } from 'core/utils';

import type { Author, TimeRangeType } from '..';
import type { NavigationParams } from 'core/navigation';
import type { Tag } from 'core/project';
import type { Stats } from 'core/stats';

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
    applySingleFilter: (
        filter: string,
        type: string,
        callback?: () => void,
    ) => void,
    getAuthorsAndTimeRangeData: () => void,
    resetFilters: () => void,
    toggleFilter: (string, string) => void,
    update: () => void,
    updateTimeRange: (filter: string) => void,
    updateFiltersFromURLParams: () => void,
|};

type State = {|
    visible: boolean,
|};

type FiltersPanelProps = {|
    authors: { [string]: boolean },
    authorsData: Array<Author>,
    extras: { [string]: boolean },
    project: string,
    resource: string,
    selectedFiltersCount: number,
    stats: Stats,
    statuses: { [string]: boolean },
    tags: { [string]: boolean },
    tagsData: Array<Tag>,
    timeRange: ?TimeRangeType,
    timeRangeData: Array<Array<number>>,
    updateTimeRange: (filter: string) => void,
    onApplyFilter: (string, string) => void,
    onApplyFilters: () => void,
    onResetFilters: () => void,
    onToggleFilter: (string, string, SyntheticMouseEvent<any>) => void,
    onDiscard: (e: MouseEvent) => void,
|};

export function FiltersPanel({
    authors,
    authorsData,
    extras,
    project,
    resource,
    selectedFiltersCount,
    stats,
    statuses,
    tags,
    tagsData,
    timeRange,
    timeRangeData,
    updateTimeRange,
    onApplyFilter,
    onApplyFilters,
    onResetFilters,
    onToggleFilter,
    onDiscard,
}: FiltersPanelProps): React.Element<'div'> {
    const ref = React.useRef(null);
    useOnDiscard(ref, onDiscard);

    return (
        <div className='menu' ref={ref}>
            <ul>
                <Localized id='search-FiltersPanel--heading-status'>
                    <li className='horizontal-separator'>TRANSLATION STATUS</li>
                </Localized>

                {FILTERS_STATUS.map((status, i) => {
                    const count = status.stat
                        ? stats[status.stat]
                        : stats[status.slug];
                    const selected = statuses[status.slug];

                    let className = status.slug;
                    if (selected && status.slug !== 'all') {
                        className += ' selected';
                    }

                    return (
                        <li
                            className={className}
                            key={i}
                            onClick={() =>
                                onApplyFilter(status.slug, 'statuses')
                            }
                        >
                            <span
                                className='status fa'
                                onClick={(e) =>
                                    onToggleFilter(status.slug, 'statuses', e)
                                }
                            ></span>
                            <Localized
                                id={`search-FiltersPanel--status-name-${status.slug}`}
                            >
                                <span className='title'>{status.name}</span>
                            </Localized>
                            <span className='count'>
                                {asLocaleString(count)}
                            </span>
                        </li>
                    );
                })}

                {tagsData.length === 0 ||
                resource !== 'all-resources' ? null : (
                    <>
                        <Localized id='search-FiltersPanel--heading-tags'>
                            <li className='horizontal-separator'>TAGS</li>
                        </Localized>

                        {tagsData
                            .sort((a, b) => {
                                return b.priority - a.priority;
                            })
                            .map((tag, i) => {
                                const selected = tags[tag.slug];

                                let className = tag.slug;
                                if (selected) {
                                    className += ' selected';
                                }

                                return (
                                    <li
                                        className={`tag ${className}`}
                                        key={i}
                                        onClick={() =>
                                            onApplyFilter(tag.slug, 'tags')
                                        }
                                    >
                                        <span
                                            className='status fa'
                                            onClick={() =>
                                                onApplyFilter(tag.slug, 'tags')
                                            }
                                        ></span>
                                        <span className='title'>
                                            {tag.name}
                                        </span>
                                        <span className='priority'>
                                            {[1, 2, 3, 4, 5].map((index) => {
                                                const active =
                                                    index <= tag.priority
                                                        ? 'active'
                                                        : '';
                                                return (
                                                    <span
                                                        className={`fa fa-star ${active}`}
                                                        key={index}
                                                    ></span>
                                                );
                                            })}
                                        </span>
                                    </li>
                                );
                            })}
                    </>
                )}

                <Localized id='search-FiltersPanel--heading-extra'>
                    <li className='horizontal-separator'>EXTRA FILTERS</li>
                </Localized>

                {FILTERS_EXTRA.map((extra, i) => {
                    const selected = extras[extra.slug];

                    let className = extra.slug;
                    if (selected) {
                        className += ' selected';
                    }

                    return (
                        <li
                            className={className}
                            key={i}
                            onClick={() => onApplyFilter(extra.slug, 'extras')}
                        >
                            <span
                                className='status fa'
                                onClick={(e) =>
                                    onToggleFilter(extra.slug, 'extras', e)
                                }
                            ></span>
                            <Localized
                                id={`search-FiltersPanel--extra-name-${extra.slug}`}
                            >
                                <span className='title'>{extra.name}</span>
                            </Localized>
                        </li>
                    );
                })}

                <TimeRangeFilter
                    project={project}
                    timeRange={timeRange}
                    timeRangeData={timeRangeData}
                    applySingleFilter={onApplyFilter}
                    toggleFilter={onToggleFilter}
                    updateTimeRange={updateTimeRange}
                />

                {authorsData.length === 0 ||
                project === 'all-projects' ? null : (
                    <>
                        <Localized id='search-FiltersPanel--heading-authors'>
                            <li className='horizontal-separator'>
                                TRANSLATION AUTHORS
                            </li>
                        </Localized>

                        {authorsData.map((author, i) => {
                            const selected = authors[author.email];

                            let className = 'author';
                            if (selected) {
                                className += ' selected';
                            }

                            return (
                                <li
                                    className={`${className}`}
                                    key={i}
                                    onClick={() =>
                                        onApplyFilter(author.email, 'authors')
                                    }
                                >
                                    <figure>
                                        <span className='sel'>
                                            <span
                                                className='status fa'
                                                onClick={(e) =>
                                                    onToggleFilter(
                                                        author.email,
                                                        'authors',
                                                        e,
                                                    )
                                                }
                                            ></span>
                                            <img
                                                alt=''
                                                className='rounded'
                                                src={author.gravatar_url}
                                                width='44'
                                                height='44'
                                            />
                                        </span>
                                        <figcaption>
                                            <p className='name'>
                                                {author.display_name}
                                            </p>
                                            <p className='role'>
                                                {author.role}
                                            </p>
                                        </figcaption>
                                        <span className='count'>
                                            {asLocaleString(
                                                author.translation_count,
                                            )}
                                        </span>
                                    </figure>
                                </li>
                            );
                        })}
                    </>
                )}
            </ul>

            {selectedFiltersCount === 0 ? null : (
                <div className='toolbar clearfix'>
                    <Localized
                        id='search-FiltersPanel--clear-selection'
                        attrs={{ title: true }}
                        elems={{
                            glyph: <i className='fa fa-times fa-lg' />,
                        }}
                    >
                        <button
                            title='Uncheck selected filters'
                            onClick={onResetFilters}
                            className='clear-selection'
                        >
                            {'<glyph></glyph> CLEAR'}
                        </button>
                    </Localized>
                    <Localized
                        id='search-FiltersPanel--apply-filters'
                        attrs={{ title: true }}
                        elems={{
                            glyph: <i className='fa fa-check fa-lg' />,
                            stress: <span className='applied-count' />,
                        }}
                        vars={{ count: selectedFiltersCount }}
                    >
                        <button
                            title='Apply Selected Filters'
                            onClick={onApplyFilters}
                            className='apply-selected'
                        >
                            {
                                '<glyph></glyph>APPLY <stress>{ $count }</stress> FILTERS'
                            }
                        </button>
                    </Localized>
                </div>
            )}
        </div>
    );
}

/**
 * Shows a list of filters, used to filter the list of entities.
 *
 * Changes to the filters will be reflected in the URL.
 */
export default class FiltersPanelBase extends React.Component<Props, State> {
    menu: { current: ?HTMLDivElement };

    constructor(props: Props) {
        super(props);

        this.state = {
            visible: false,
        };
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
    }

    toggleVisibility: () => void = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
        this.props.updateFiltersFromURLParams();
    };

    handleDiscard: () => void = () => {
        this.setState({
            visible: false,
        });
        this.props.updateFiltersFromURLParams();
    };

    applyFilters: () => void = () => {
        this.setState({
            visible: false,
        });
        return this.props.update();
    };

    toggleFilter: (
        filter: string,
        type: string,
        event: SyntheticMouseEvent<>,
    ) => void = (
        filter: string,
        type: string,
        event: SyntheticMouseEvent<>,
    ) => {
        if (filter === 'all') {
            return;
        }

        event.stopPropagation();
        this.props.toggleFilter(filter, type);
    };

    applySingleFilter: (filter: string, type: string) => void = (
        filter: string,
        type: string,
    ) => {
        this.toggleVisibility();
        this.props.applySingleFilter(filter, type, this.props.update);
    };

    getSelectedFilters(): {
        statuses: Array<string>,
        extras: Array<string>,
        tags: Array<string>,
        timeRange: ?TimeRangeType,
        authors: Array<string>,
    } {
        const { statuses, extras, tags, timeRange, authors } = this.props;

        return {
            statuses: Object.keys(statuses).filter((s) => statuses[s]),
            extras: Object.keys(extras).filter((e) => extras[e]),
            tags: Object.keys(tags).filter((t) => tags[t]),
            timeRange,
            authors: Object.keys(authors).filter((a) => authors[a]),
        };
    }

    getSelectedFiltersCount: () => number = () => {
        const selected = this.getSelectedFilters();

        return (
            selected.statuses.length +
            selected.extras.length +
            selected.tags.length +
            (selected.timeRange ? 1 : 0) +
            selected.authors.length
        );
    };

    getFilterIcon: () => any | string = () => {
        const { authorsData, tagsData, timeRange } = this.props;
        const selected = this.getSelectedFilters();
        const selectedFiltersCount = this.getSelectedFiltersCount();

        // If there are zero or several selected statuses, show the "All" icon.
        let filterIcon = 'all';

        // Otherwise show the approriate status icon.
        if (selectedFiltersCount === 1) {
            const selectedStatus = FILTERS_STATUS.find(
                (f) => f.slug === selected.statuses[0],
            );
            if (selectedStatus) {
                filterIcon = selectedStatus.slug;
            }

            const selectedExtra = FILTERS_EXTRA.find(
                (f) => f.slug === selected.extras[0],
            );
            if (selectedExtra) {
                filterIcon = selectedExtra.slug;
            }

            const selectedTag = tagsData.find(
                (f) => f.slug === selected.tags[0],
            );
            if (selectedTag) {
                filterIcon = 'tag';
            }

            if (timeRange) {
                filterIcon = 'time-range';
            }

            const selectedAuthor = authorsData.find(
                (f) => f.email === selected.authors[0],
            );
            if (selectedAuthor) {
                filterIcon = 'author';
            }
        }

        return filterIcon;
    };

    render(): React.Element<'div'> {
        const props = this.props;
        const { project, resource } = this.props.parameters;

        const selectedFiltersCount = this.getSelectedFiltersCount();
        const filterIcon = this.getFilterIcon();

        return (
            <div className='filters-panel'>
                <div
                    className={`visibility-switch ${filterIcon}`}
                    onClick={this.toggleVisibility}
                >
                    <span className='status fa'></span>
                </div>
                {this.state.visible && (
                    <FiltersPanel
                        authors={props.authors}
                        authorsData={props.authorsData}
                        extras={props.extras}
                        project={project}
                        resource={resource}
                        selectedFiltersCount={selectedFiltersCount}
                        stats={props.stats}
                        statuses={props.statuses}
                        tags={props.tags}
                        tagsData={props.tagsData}
                        timeRange={props.timeRange}
                        timeRangeData={props.timeRangeData}
                        updateTimeRange={props.updateTimeRange}
                        onApplyFilter={this.applySingleFilter}
                        onApplyFilters={this.applyFilters}
                        onDiscard={this.handleDiscard}
                        onResetFilters={props.resetFilters}
                        onToggleFilter={this.toggleFilter}
                    />
                )}
            </div>
        );
    }
}
