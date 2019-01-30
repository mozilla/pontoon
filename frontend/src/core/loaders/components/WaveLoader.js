/* @flow */

import React from 'react';

import './WaveLoader.css';

export const WaveLoader = (): React.Node => (
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


export default WaveLoader;
