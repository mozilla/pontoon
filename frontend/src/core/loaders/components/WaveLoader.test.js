import React from 'react';
import WaveLoader, { WaveLoader as WaveLoaderBase } from './WaveLoader';

import { createReduxStore } from '../../../test/store';
import { shallowUntilTarget } from '../../../test/utils';

describe('<WaveLoader>', () => {
    it('render the loader before l10n bundle will be fetched', () => {
        const store = createReduxStore({
          l10n: {
            fetching: true,
          },
          locales: {
            fetching: false,
          }
        });
        const wrapper = shallowUntilTarget(
            <WaveLoader store={store}>
                <div id="app">Pontoon</div>
            </WaveLoader>,
            WaveLoaderBase
        );

        expect(wrapper.find('WaveLoadingBar')).toHaveLength(1);
        expect(wrapper.find('#app')).toHaveLength(1);
    });

    it('render the loader before locales will be fetched', () => {
        const store = createReduxStore({
            l10n: {
                fetching: false,
            },
            locales: {
                fetching: true,
            }
        });
        const wrapper = shallowUntilTarget(
            <WaveLoader store={store}>
                <div id="app">Pontoon</div>
            </WaveLoader>,
            WaveLoaderBase
        );

        expect(wrapper.find('WaveLoadingBar')).toHaveLength(1);
        expect(wrapper.find('#app')).toHaveLength(1);
    });

    it('render children if locales and UI translations are loaded', () => {
        const store = createReduxStore({
            l10n: {
                fetching: false,
            },
            locales: {
                fetching: false,
            }
        });
        const wrapper = shallowUntilTarget(
            <WaveLoader store={store}>
                <div id="app">Pontoon</div>
            </WaveLoader>,
            WaveLoaderBase
        );

        expect(wrapper.find('WaveLoadingBar')).toHaveLength(0);
        expect(wrapper.find('#app')).toHaveLength(1);
    });
});
