/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';
import { Localized } from 'fluent-react';

import './FiltersPanel.css';

import { FILTERS_STATUS, FILTERS_EXTRA } from '..';

import { asLocaleString } from 'core/utils';

import type { Stats } from 'core/stats';


type Props = {|
    statuses: { [string]: boolean },
    extras: { [string]: boolean },
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
        const { statuses, extras, stats } = this.props;

        const selectedStatuses = Object.keys(statuses).filter(s => statuses[s]);
        const selectedExtras = Object.keys(extras).filter(e => extras[e]);
        const selectedFiltersCount = selectedExtras.length + selectedStatuses.length;

        // If there are zero or several selected statuses, show the "All" icon.
        let reducedStatus = { slug: 'all' };

        // Otherwise show the approriate status icon.
        if (selectedFiltersCount === 1) {
            const selectedStatus = FILTERS_STATUS.find(s => s.slug === selectedStatuses[0]);
            if (selectedStatus) {
                reducedStatus = selectedStatus;
            }
        }

        return <div className="filters-panel">
            <div
                className={ `visibility-switch ${reducedStatus.slug}` }
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
