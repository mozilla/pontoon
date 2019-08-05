/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';
import { Localized } from 'fluent-react';

import './FiltersPanel.css';

import { FILTERS_STATUS, FILTERS_EXTRA } from '..';

import { asLocaleString } from 'core/utils';

import type { Tag } from 'core/project';
import type { Stats } from 'core/stats';


type Props = {|
    statuses: { [string]: boolean },
    extras: { [string]: boolean },
    tags: { [string]: boolean },
    tagsData: Array<Tag>,
    stats: Stats,
    applySingleFilter: (filter: ?string, callback?: () => void) => void,
    resetFilters: () => void,
    toggleFilter: (string) => void,
    update: () => void,
|};

type State = {|
    visible: boolean,
|};


/**
 * Shows a list of filters (status, author, extras), used to filter the list
 * of entities.
 *
 * Changes to the filters will be reflected in the URL.
 */
export class FiltersPanelBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);

        this.state = {
            visible: false,
        };
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

    createToggleFilter = (filter: string) => {
        if (filter === 'all') {
            return null;
        }

        return (event: SyntheticInputEvent<>) => {
            event.stopPropagation();
            this.props.toggleFilter(filter);
        };
    }

    createApplySingleFilter(filter: string) {
        return () => {
            this.toggleVisibility();
            this.props.applySingleFilter(filter, this.props.update);
        };
    }

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the search panel.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    }

    render() {
        const { statuses, extras, tags, tagsData, stats } = this.props;

        const selectedStatuses = Object.keys(statuses).filter(s => statuses[s]);
        const selectedExtras = Object.keys(extras).filter(e => extras[e]);
        const selectedTags = Object.keys(tags).filter(e => tags[e]);
        const selectedFiltersCount = (
            selectedExtras.length +
            selectedStatuses.length +
            selectedTags.length
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

            const selectedTag = tagsData.find(f => f.slug === selectedTags[0]);
            if (selectedTag) {
                filterIcon = 'tag';
            }
        }

        return <div className="filters-panel">
            <div
                className={ `visibility-switch ${filterIcon}` }
                onClick={ this.toggleVisibility }
            >
                <span className="status fa"></span>
            </div>
            { !this.state.visible ? null : <div className="menu">
                <ul>
                    <Localized id="search-FiltersPanel--heading-status">
                        <li className="horizontal-separator">Translation Status</li>
                    </Localized>

                    { FILTERS_STATUS.map((status, i) => {
                        const count = status.stat ? stats[status.stat] : stats[status.slug];
                        const selected = statuses[status.slug];

                        let className = status.slug;
                        if (selected && status.slug !== 'all') {
                            className += ' selected';
                        }

                        return <li
                            className={ className }
                            key={ i }
                            onClick={ this.createApplySingleFilter(status.slug) }
                        >
                            <span
                                className="status fa"
                                onClick={ this.createToggleFilter(status.slug) }
                            ></span>
                            <span className="title">{ status.title }</span>
                            <span className="count">
                                { asLocaleString(count) }
                            </span>
                        </li>
                    }) }

                    { tagsData.length === 0 ? null : <>
                        <Localized id="search-FiltersPanel--heading-tags">
                            <li className="horizontal-separator">Tags</li>
                        </Localized>

                        { tagsData.map((tag, i) => {
                            const selected = tags[tag.slug];

                            let className = tag.slug;
                            if (selected) {
                                className += ' selected';
                            }

                            return <li
                                className={ `tag ${className}` }
                                key={ i }
                                onClick={ this.createApplySingleFilter(tag.slug) }
                            >
                                <span
                                    className="status fa"
                                    onClick={ this.createToggleFilter(tag.slug) }
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
                        const selected = extras[extra.slug];

                        let className = extra.slug;
                        if (selected) {
                            className += ' selected';
                        }

                        return <li
                            className={ className }
                            key={ i }
                            onClick={ this.createApplySingleFilter(extra.slug) }
                        >
                            <span
                                className="status fa"
                                onClick={ this.createToggleFilter(extra.slug) }
                            ></span>
                            <span className="title">{ extra.title }</span>
                        </li>
                    }) }
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
                            <i className="fa fa-times fa-lg"></i>
                            Clear
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
                            <i className="fa fa-check fa-lg"></i>
                            { 'Apply <stress>{ $count }</stress> filters' }
                        </button>
                    </Localized>
                </div> }
            </div> }
        </div>;
    }
}


export default onClickOutside(FiltersPanelBase);
