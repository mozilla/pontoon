/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';

import './ResourceProgress.css';

import ProgressChart from './ProgressChart';

import type { Stats } from 'core/stats';


type Props = {|
    stats: Stats,
|};

type State = {|
    visible: boolean,
|};


/**
 * Show a panel with progress chart and stats for the current resource.
 */
export class ResourceProgressBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            visible: false,
        };
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    }

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the search panel.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    }

    render() {
        const { approved, fuzzy, warnings, errors, missing, unreviewed, total } = this.props.stats;
        const complete = approved + warnings;

        let percent = 0;
        if (total) {
            percent = Math.floor(complete / total * 100);
        }

        return <div className="progress-chart">
            <div className="selector" onClick={ this.toggleVisibility }>
                <ProgressChart stats={ this.props.stats } size={ 44 } />
                <span className="percent unselectable">{ percent }</span>
            </div>
            { !this.state.visible ? null :
            <aside className="menu">
                <div className="main">
                    <header>
                        <h2>
                            All strings
                            <span className="value">{ Number(total).toLocaleString('en-US') }</span>
                        </h2>
                        <h2 className="small">
                            Unreviewed
                            <span className="value">{ Number(unreviewed).toLocaleString('en-US') }</span>
                        </h2>
                    </header>
                    <ProgressChart stats={ this.props.stats } size={ 220 } />
                    <span className="percent">{ percent }</span>
                </div>
                <div className="details">
                    <div className="approved">
                        <span className="title">Translated</span>
                        <p className="value">{ Number(approved).toLocaleString('en-US') }</p>
                    </div>
                    <div className="fuzzy">
                        <span className="title">Fuzzy</span>
                        <p className="value">{ Number(fuzzy).toLocaleString('en-US') }</p>
                    </div>
                    <div className="warnings">
                        <span className="title">Warnings</span>
                        <p className="value">{ Number(warnings).toLocaleString('en-US') }</p>
                    </div>
                    <div className="errors">
                        <span className="title">Errors</span>
                        <p className="value">{ Number(errors).toLocaleString('en-US') }</p>
                    </div>
                    <div className="missing">
                        <span className="title">Missing</span>
                        <p className="value">{ Number(missing).toLocaleString('en-US') }</p>
                    </div>
                </div>
            </aside>
            }
        </div>;
    }
}


export default onClickOutside(ResourceProgressBase);
