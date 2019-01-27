/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './WaveLoader.css';

import type { LocaleState } from 'modules/core/locales/reducer';
import type { L10nState } from 'modules/core/l10n/reducer';

type Props = {
    isLoading: boolean,
    children?: React.Node,
};

const WaveLoadingBar = (): React.Node => (
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

const WaveLoader = (props: Props): React.Node => (
    // Render children components, because some of fetches happen after components are rendered.
    <React.Fragment>
        { props.isLoading ? <WaveLoadingBar /> : '' }
        { props.children }
    </React.Fragment>
);

export default WaveLoader;
