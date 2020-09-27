/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';

import { Localized } from '@fluent/react';

import './FiltersPanel.css';

import { FILTERS_STATUS, FILTERS_EXTRA } from '..';
import TimeRangeFilter from './TimeRangeFilter';

import { asLocaleString } from 'core/utils';

import type { TimeRangeType } from '..';
import type { NavigationParams } from 'core/navigation';
import type { Tag } from 'core/project';
import type { Stats } from 'core/stats';
import type { Author } from 'modules/search';

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

/**
 * Shows a list of filters, used to filter the list of entities.
 *
 * Changes to the filters will be reflected in the URL.
 */
export class FiltersPanelBase extends React.Component<Props, State> {
    menu: { current: ?HTMLDivElement };

    constructor(props: Props) {
        super(props);

        this.state = {
            visible: false,
        };

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
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
        this.props.updateFiltersFromURLParams();
    };

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the search panel.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
        this.props.updateFiltersFromURLParams();
    };

    applyFilters = () => {
        this.setState({
            visible: false,
        });
        return this.props.update();
    };

    createToggleFilter = (filter: string, type: string) => {
        if (filter === 'all') {
            return null;
        }

        return (event: SyntheticMouseEvent<>) => {
            this.toggleFilter(filter, type, event);
        };
    };

    toggleFilter = (
        filter: string,
        type: string,
        event: SyntheticMouseEvent<>,
    ) => {
        event.stopPropagation();
        this.props.toggleFilter(filter, type);
    };

    createApplySingleFilter(filter: string, type: string) {
        return () => {
            this.applySingleFilter(filter, type);
        };
    }

    applySingleFilter = (filter: string, type: string) => {
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

    getSelectedFiltersCount = () => {
        const selected = this.getSelectedFilters();

        return (
            selected.statuses.length +
            selected.extras.length +
            selected.tags.length +
            (selected.timeRange ? 1 : 0) +
            selected.authors.length
        );
    };

    getFilterIcon = () => {
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

    // Check if the filter toolbar is hidden
    isToolbarHidden = () => {
        const menu = this.menu.current;
        const selectedFiltersCount = this.getSelectedFiltersCount();

        let isScrollbarVisible = false;
        if (menu) {
            isScrollbarVisible = menu.scrollHeight > menu.clientHeight;
        }

        if (selectedFiltersCount > 0 && isScrollbarVisible) {
            return true;
        }

        return false;
    };

    render() {
        const props = this.props;
        const { project, resource } = this.props.parameters;

        const selectedFiltersCount = this.getSelectedFiltersCount();
        const filterIcon = this.getFilterIcon();
        const fixedClass = this.isToolbarHidden() ? 'fixed' : '';

        return (
            <div className={`filters-panel ${fixedClass}`}>
                <div
                    className={`visibility-switch ${filterIcon}`}
                    onClick={this.toggleVisibility}
                >
                    <span className='status fa'></span>
                </div>
                {!this.state.visible ? null : (
                    <div className='menu' ref={this.menu}>
                        <ul>
                            <Localized id='search-FiltersPanel--heading-status'>
                                <li className='horizontal-separator'>
                                    Translation Status
                                </li>
                            </Localized>

                            {FILTERS_STATUS.map((status, i) => {
                                const count = status.stat
                                    ? props.stats[status.stat]
                                    : props.stats[status.slug];
                                const selected = props.statuses[status.slug];

                                let className = status.slug;
                                if (selected && status.slug !== 'all') {
                                    className += ' selected';
                                }

                                return (
                                    <li
                                        className={className}
                                        key={i}
                                        onClick={this.createApplySingleFilter(
                                            status.slug,
                                            'statuses',
                                        )}
                                    >
                                        <span
                                            className='status fa'
                                            onClick={this.createToggleFilter(
                                                status.slug,
                                                'statuses',
                                            )}
                                        ></span>
                                        <Localized
                                            id={`search-FiltersPanel--status-name-${status.slug}`}
                                        >
                                            <span className='title'>
                                                {status.name}
                                            </span>
                                        </Localized>
                                        <span className='count'>
                                            {asLocaleString(count)}
                                        </span>
                                    </li>
                                );
                            })}

                            {props.tagsData.length === 0 ||
                            resource !== 'all-resources' ? null : (
                                <>
                                    <Localized id='search-FiltersPanel--heading-tags'>
                                        <li className='horizontal-separator'>
                                            Tags
                                        </li>
                                    </Localized>

                                    {props.tagsData.map((tag, i) => {
                                        const selected = props.tags[tag.slug];

                                        let className = tag.slug;
                                        if (selected) {
                                            className += ' selected';
                                        }

                                        return (
                                            <li
                                                className={`tag ${className}`}
                                                key={i}
                                                onClick={this.createApplySingleFilter(
                                                    tag.slug,
                                                    'tags',
                                                )}
                                            >
                                                <span
                                                    className='status fa'
                                                    onClick={this.createToggleFilter(
                                                        tag.slug,
                                                        'tags',
                                                    )}
                                                ></span>
                                                <span className='title'>
                                                    {tag.name}
                                                </span>
                                                <span className='priority'>
                                                    {[1, 2, 3, 4, 5].map(
                                                        (index) => {
                                                            const active =
                                                                index <=
                                                                tag.priority
                                                                    ? 'active'
                                                                    : '';
                                                            return (
                                                                <span
                                                                    className={`fa fa-star ${active}`}
                                                                    key={index}
                                                                ></span>
                                                            );
                                                        },
                                                    )}
                                                </span>
                                            </li>
                                        );
                                    })}
                                </>
                            )}

                            <Localized id='search-FiltersPanel--heading-extra'>
                                <li className='horizontal-separator'>
                                    Extra Filters
                                </li>
                            </Localized>

                            {FILTERS_EXTRA.map((extra, i) => {
                                const selected = props.extras[extra.slug];

                                let className = extra.slug;
                                if (selected) {
                                    className += ' selected';
                                }

                                return (
                                    <li
                                        className={className}
                                        key={i}
                                        onClick={this.createApplySingleFilter(
                                            extra.slug,
                                            'extras',
                                        )}
                                    >
                                        <span
                                            className='status fa'
                                            onClick={this.createToggleFilter(
                                                extra.slug,
                                                'extras',
                                            )}
                                        ></span>
                                        <Localized
                                            id={`search-FiltersPanel--extra-name-${extra.slug}`}
                                        >
                                            <span className='title'>
                                                {extra.name}
                                            </span>
                                        </Localized>
                                    </li>
                                );
                            })}

                            <TimeRangeFilter
                                project={project}
                                timeRange={props.timeRange}
                                timeRangeData={props.timeRangeData}
                                applySingleFilter={this.applySingleFilter}
                                toggleFilter={this.toggleFilter}
                                updateTimeRange={props.updateTimeRange}
                            />

                            {props.authorsData.length === 0 ||
                            project === 'all-projects' ? null : (
                                <>
                                    <Localized id='search-FiltersPanel--heading-authors'>
                                        <li className='horizontal-separator'>
                                            Translation Authors
                                        </li>
                                    </Localized>

                                    {props.authorsData.map((author, i) => {
                                        const selected =
                                            props.authors[author.email];

                                        let className = 'author';
                                        if (selected) {
                                            className += ' selected';
                                        }

                                        return (
                                            <li
                                                className={`${className}`}
                                                key={i}
                                                onClick={this.createApplySingleFilter(
                                                    author.email,
                                                    'authors',
                                                )}
                                            >
                                                <figure>
                                                    <span className='sel'>
                                                        <span
                                                            className='status fa'
                                                            onClick={this.createToggleFilter(
                                                                author.email,
                                                                'authors',
                                                            )}
                                                        ></span>
                                                        <img
                                                            alt=''
                                                            className='rounded'
                                                            src={
                                                                author.gravatar_url
                                                            }
                                                            width='44'
                                                            height='44'
                                                        />
                                                    </span>
                                                    <figcaption>
                                                        <p className='name'>
                                                            {
                                                                author.display_name
                                                            }
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
                                        glyph: (
                                            <i className='fa fa-times fa-lg' />
                                        ),
                                    }}
                                >
                                    <button
                                        title='Uncheck selected filters'
                                        onClick={this.props.resetFilters}
                                        className='clear-selection'
                                    >
                                        {'<glyph></glyph>Clear'}
                                    </button>
                                </Localized>
                                <Localized
                                    id='search-FiltersPanel--apply-filters'
                                    attrs={{ title: true }}
                                    elems={{
                                        glyph: (
                                            <i className='fa fa-check fa-lg' />
                                        ),
                                        stress: (
                                            <span className='applied-count' />
                                        ),
                                    }}
                                    vars={{ count: selectedFiltersCount }}
                                >
                                    <button
                                        title='Apply Selected Filters'
                                        onClick={this.applyFilters}
                                        className='apply-selected'
                                    >
                                        {
                                            '<glyph></glyph>Apply <stress>{ $count }</stress> filters'
                                        }
                                    </button>
                                </Localized>
                            </div>
                        )}
                    </div>
                )}
            </div>
        );
    }
}

export default onClickOutside(FiltersPanelBase);
