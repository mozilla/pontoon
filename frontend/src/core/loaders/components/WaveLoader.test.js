import React from 'react';
import WaveLoader, { WaveLoader as WaveLoaderBase } from './WaveLoader';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

describe('<WaveLoader>', () => {
    it('renders the loading bar when the app is loading', () => {
        const wrapper = shallowUntilTarget(
            <WaveLoader isLoading={ true }>
                <div id="app">Pontoon</div>
            </WaveLoader>,
            WaveLoaderBase
        );

        expect(wrapper.find('WaveLoadingBar')).toHaveLength(1);
        expect(wrapper.find('#app')).toHaveLength(0);
    });

    it('renders children when the app is ready', () => {
        const wrapper = shallowUntilTarget(
            <WaveLoader isLoading={ false }>
                <div id="app">Pontoon</div>
            </WaveLoader>,
            WaveLoaderBase
        );

        expect(wrapper.find('WaveLoadingBar')).toHaveLength(0);
        expect(wrapper.find('#app')).toHaveLength(1);
    });
});
