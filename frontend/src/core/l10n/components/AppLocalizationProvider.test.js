import React from 'react';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import { actions } from '..';
import AppLocalizationProvider, { AppLocalizationProviderBase } from './AppLocalizationProvider';


describe('<AppLocalizationProvider>', () => {
    beforeAll(() => {
        const getMock = sinon.stub(actions, 'get');
        getMock.returns({type: 'whatever'});
    });

    afterEach(() => {
        // Make sure tests do not pollute one another.
        actions.get.resetHistory();
    });

    afterAll(() => {
        actions.get.restore();
    });

    it('fetches a locale when the component mounts', () => {
        const store = createReduxStore();

        shallowUntilTarget(
            <AppLocalizationProvider store={store} />,
            AppLocalizationProviderBase
        );

        expect(actions.get.callCount).toEqual(1);
    });

    it('shows a loader when the locales are not loaded yet', () => {
        const store = createReduxStore();

        store.dispatch(actions.request());

        const wrapper = shallowUntilTarget(
            <AppLocalizationProvider store={store}>
                <div id="content-test-AppLocalizationProvider" />
            </AppLocalizationProvider>,
            AppLocalizationProviderBase
        );

        expect(wrapper.text()).toEqual('LOADING');
        expect(wrapper.find('#content-test-AppLocalizationProvider')).toHaveLength(0);
    });

    it('renders its children when locales are loaded', () => {
        const store = createReduxStore();
        store.dispatch(actions.receive('fr', { messages: [ 'hello' ] }));

        const wrapper = shallowUntilTarget(
            <AppLocalizationProvider store={store}>
                <div id="content-test-AppLocalizationProvider" />
            </AppLocalizationProvider>,
            AppLocalizationProviderBase
        );

        expect(wrapper.find('#content-test-AppLocalizationProvider')).toHaveLength(1);
    });
});
