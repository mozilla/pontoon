/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';

import './FiltersPanel.css';

import type { Navigation } from 'core/navigation';
import type { Stats } from 'core/stats';

import { FILTERS_STATUS } from '..';


type Props = {|
    parameters: Navigation,
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
        };
    }

    toggleVisibility = () => {
        this.setState({
            visible: !this.state.visible,
        });
    }

    selectStatus(status: string) {
        const newStatus = status === 'all' ? null : status;

        return () => {
            this.toggleVisibility();
            return this.props.selectStatus(newStatus);
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
                        return <li
                            className={ filter.tag }
                            key={ i }
                            onClick={ this.selectStatus(filter.tag) }
                        >
                            <span className="status fa"></span>
                            <span className="title">{ filter.title }</span>
                            <span className="count">
                                { filter.stat ? stats[filter.stat] : stats[filter.tag] }
                            </span>
                        </li>
                    }) }
                </ul>
            </div> }
        </div>;
    }
}


export default onClickOutside(FiltersPanelBase);
