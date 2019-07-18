/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';

import './FiltersPanel.css';

import { FILTERS_STATUS } from '..';

import { asLocaleString } from 'core/utils';

import type { NavigationParams } from 'core/navigation';
import type { Stats } from 'core/stats';


type Props = {|
    parameters: NavigationParams,
    stats: Stats,
    selectStatus: Function,
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
            filters: this.getInitialFilters(),
        };
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    }

    createHandleSelectFilter = (filter: string) => {
        if (filter === 'all') {
            return null;
        }

        return (event) => {
            event.stopPropagation();
            this.setState(state => {
                return {
                    filters: {
                        ...state.filters,
                        [filter]: !state.filters[filter],
                    },
                };
            })
        };
    }

    getInitialFilters() {
        const initialFilters = {};
        FILTERS_STATUS.forEach(f => initialFilters[f.tag] = false);
        return initialFilters;
    }

    createSetFilter(filter: string) {
        const newFilter = filter === 'all' ? null : filter;

        return () => {
            this.toggleVisibility();

            const filters = this.getInitialFilters();
            filters[filter] = true;
            this.setState({ filters });

            return this.props.selectStatus(newFilter);
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
        const { parameters, stats } = this.props;

        let selectedStatus = FILTERS_STATUS.find(
            item => item.tag === parameters.status
        );
        if (!selectedStatus) {
            selectedStatus = { tag: 'all' };
        }

        const className = `visibility-switch ${selectedStatus.tag}`;

        return <div className="filters-panel">
            <div className={ className } onClick={ this.toggleVisibility }>
                <span className="status fa"></span>
            </div>
            { !this.state.visible ? null : <div className="menu">
                <ul>
                    <li className="horizontal-separator">Translation Status</li>
                    { FILTERS_STATUS.map((filter, i) => {
                        const count = filter.stat ? stats[filter.stat] : stats[filter.tag];
                        const selected = this.state.filters[filter.tag];

                        let className = filter.tag;
                        if (selected) {
                            className += ' selected';
                        }

                        return <li
                            className={ className }
                            key={ i }
                            onClick={ this.createSetFilter(filter.tag) }
                        >
                            <span
                                className="status fa"
                                onClick={ this.createHandleSelectFilter(filter.tag) }
                            ></span>
                            <span className="title">{ filter.title }</span>
                            <span className="count">
                                { asLocaleString(count) }
                            </span>
                        </li>
                    }) }
                </ul>
            </div> }
        </div>;
    }
}


export default onClickOutside(FiltersPanelBase);
