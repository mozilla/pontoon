/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';
import { Localized } from 'fluent-react';

import './FiltersPanel.css';

import { FILTERS_STATUS } from '..';

import { asLocaleString } from 'core/utils';

import type { Stats } from 'core/stats';


type Props = {|
    statuses: { [string]: boolean },
    stats: Stats,
    resetStatuses: () => void,
    setSingleStatus: (status: ?string, callback?: () => void) => void,
    toggleStatus: (string) => void,
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

    resetFilters = () => {
        this.props.resetStatuses();
    }

    createHandleSelectStatus = (status: string) => {
        if (status === 'all') {
            return null;
        }

        return (event: SyntheticInputEvent<>) => {
            event.stopPropagation();
            this.props.toggleStatus(status);
        };
    }

    createSetStatus(status: string) {
        return () => {
            this.toggleVisibility();
            this.props.setSingleStatus(status, this.props.update);
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
        const { statuses, stats } = this.props;

        const selectedStatuses = Object.keys(statuses).filter(s => statuses[s]);
        const selectedStatusesCount = selectedStatuses.length;

        // If there are zero or several selected statuses, show the "All" icon.
        let reducedStatus = { tag: 'all' };

        // Otherwise show the approriate status icon.
        if (selectedStatusesCount === 1) {
            const selectedStatus = FILTERS_STATUS.find(s => s.tag === selectedStatuses[0]);
            if (selectedStatus) {
                reducedStatus = selectedStatus;
            }
        }

        return <div className="filters-panel">
            <div
                className={ `visibility-switch ${reducedStatus.tag}` }
                onClick={ this.toggleVisibility }
            >
                <span className="status fa"></span>
            </div>
            { !this.state.visible ? null : <div className="menu">
                <ul>
                    <li className="horizontal-separator">Translation Status</li>
                    { FILTERS_STATUS.map((status, i) => {
                        const count = status.stat ? stats[status.stat] : stats[status.tag];
                        const selected = statuses[status.tag];

                        let className = status.tag;
                        if (selected && status.tag !== 'all') {
                            className += ' selected';
                        }

                        return <li
                            className={ className }
                            key={ i }
                            onClick={ this.createSetStatus(status.tag) }
                        >
                            <span
                                className="status fa"
                                onClick={ this.createHandleSelectStatus(status.tag) }
                            ></span>
                            <span className="title">{ status.title }</span>
                            <span className="count">
                                { asLocaleString(count) }
                            </span>
                        </li>
                    }) }
                </ul>
                { selectedStatusesCount === 0 ? null :
                <div className="toolbar clearfix">
                    <Localized
                        id="search-FiltersPanel--clear-selection"
                        attrs={ { title: true } }
                        glyph={ <i className="fa fa-times fa-lg"></i> }
                    >
                        <button
                            title="Uncheck selected filters"
                            onClick={ this.resetFilters }
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
                        $count={ selectedStatusesCount }
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
