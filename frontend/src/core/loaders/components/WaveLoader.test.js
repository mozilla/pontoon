import React from 'react';
import WaveLoader, { WaveLoadingBar } from './WaveLoader';

import { shallowUntilTarget } from 'test/utils';


const MockAppComponent = () => (
    <div id="app">
        Pontoon
    </div>
);

describe('<WaveLoader>', () => {
    it('renders the loading bar when the app is loading', () => {
        const wrapper = shallowUntilTarget(
            <WaveLoader isLoading={ true } />,
            WaveLoadingBar,
        );

        expect(wrapper.find('#project-load')).toHaveLength(1);
        expect(wrapper.find('#app')).toHaveLength(0);
    });

    it('renders children when the app is ready', () => {
        const wrapper = shallowUntilTarget(
            <WaveLoader isLoading={ false }>
                <MockAppComponent/>
            </WaveLoader>,
            MockAppComponent,
        );

        expect(wrapper.find('#project-load')).toHaveLength(0);
        expect(wrapper.find('#app')).toHaveLength(1);
    });
});
