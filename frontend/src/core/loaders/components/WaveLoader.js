/* @flow */

import * as React from 'react';

import './WaveLoader.css';

export const WaveLoader = (): React.Element<any> => (
    <div className='wave-loader'>
        <div className='inner'>
            <div className='animation'>
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
        </div>
    </div>
);

export default WaveLoader;
