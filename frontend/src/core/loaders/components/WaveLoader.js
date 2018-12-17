/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './WaveLoader.css';

import type { LocaleState } from 'modules/core/locales/reducer';
import type { L10nState } from 'modules/core/l10n/reducer';

type Props = {|
    l10n: L10nState,
    locales: LocaleState,
|};

const WaveLoadingBar = () => (
    <div id="project-load" className="overlay">
        <div className="inner">
            <div className="animation">
                <div></div>
                &nbsp;
                <div></div>
                &nbsp;
                <div></div>
                &nbsp;
                <div></div>
                &nbsp;
                <div></div>
            </div>
            <div className="text">&quot;640K ought to be enough for anybody.&quot;</div>
        </div>
    </div>
);

export class WaveLoader extends React.Component<Props> {
    render() {
        const { l10n, locales, children } = this.props;
        const isLoading = l10n.fetching || locales.fetching;

        // Render children components, because some of fetches happenen after components are rendered.
        return (
            <React.Fragment>
                { isLoading ? <WaveLoadingBar /> : '' }
                { children }
            </React.Fragment>
        );
    }
}

const mapStateToProps = (state: Object): Props => {
    const { l10n, locales } = state;

    return {
        l10n,
        locales,
    };
};


export default connect(mapStateToProps)(WaveLoader);
