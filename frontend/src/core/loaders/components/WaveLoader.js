/* @flow */

import React from 'react';

import './WaveLoader.css';

type Props = {
    isLoading: boolean,
    children?: React.Node,
};

export const WaveLoadingBar = (): React.Node => (
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
     props.isLoading ? <WaveLoadingBar /> : props.children
);

export default WaveLoader;
