/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
import onClickOutside from 'react-onclickoutside';

import './ResourceProgress.css';

import ProgressChart from './ProgressChart';

import { asLocaleString } from 'core/utils';

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
        // Do not show resource progress until stats are available
        else {
            return null;
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
                            <Localized id="resourceprogress-ResourceProgress--all-strings">
                                All strings
                            </Localized>
                            <span className="value">{ asLocaleString(total) }</span>
                        </h2>
                        <h2 className="small">
                            <Localized id="resourceprogress-ResourceProgress--unreviewed">
                                Unreviewed
                            </Localized>
                            <span className="value">{ asLocaleString(unreviewed) }</span>
                        </h2>
                    </header>
                    <ProgressChart stats={ this.props.stats } size={ 220 } />
                    <span className="percent">{ percent }</span>
                </div>
                <div className="details">
                    <div className="approved">
                        <span className="title">
                            <Localized id="resourceprogress-ResourceProgress--translated">
                                Translated
                            </Localized>
                        </span>
                        <p className="value">{ asLocaleString(approved) }</p>
                    </div>
                    <div className="fuzzy">
                        <span className="title">
                            <Localized id="resourceprogress-ResourceProgress--fuzzy">
                                Fuzzy
                            </Localized>
                        </span>
                        <p className="value">{ asLocaleString(fuzzy) }</p>
                    </div>
                    <div className="warnings">
                        <span className="title">
                            <Localized id="resourceprogress-ResourceProgress--warnings">
                                Warnings
                            </Localized>
                        </span>
                        <p className="value">{ asLocaleString(warnings) }</p>
                    </div>
                    <div className="errors">
                        <span className="title">
                            <Localized id="resourceprogress-ResourceProgress--errors">
                                Errors
                            </Localized>
                        </span>
                        <p className="value">{ asLocaleString(errors) }</p>
                    </div>
                    <div className="missing">
                        <span className="title">
                            <Localized id="resourceprogress-ResourceProgress--missing">
                                Missing
                            </Localized>
                        </span>
                        <p className="value">{ asLocaleString(missing) }</p>
                    </div>
                </div>
            </aside>
            }
        </div>;
    }
}


export default onClickOutside(ResourceProgressBase);
