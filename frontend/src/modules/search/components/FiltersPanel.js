/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';

import './FiltersPanel.css';

import type { Stats } from 'core/stats';


type Props = {|
    stats: Stats,
    selectStatus: Function,
|};

type State = {|
    visible: boolean,
|};


const FILTERS_STATUS = [
    { title: 'All', tag: 'all', stat: 'total' },
    { title: 'Approved', tag: 'approved' },
    { title: 'Fuzzy', tag: 'fuzzy' },
    { title: 'Warnings', tag: 'warnings' },
    { title: 'Errors', tag: 'errors' },
    { title: 'Missing', tag: 'missing' },
    { title: 'Unreviewed', tag: 'unreviewed' },
];


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
        const { stats } = this.props;

        return <div className="filters-panel">
            <div className="visibility-switch all" onClick={ this.toggleVisibility }>
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
