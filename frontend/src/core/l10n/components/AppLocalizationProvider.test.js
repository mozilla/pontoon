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
        const getPreferredLocalesMock = sinon.stub(actions, 'getPreferredLocales');
        getPreferredLocalesMock.returns({type: 'whatever'});
    });

    afterEach(() => {
        // Make sure tests do not pollute one another.
        actions.get.resetHistory();
        actions.getPreferredLocales.resetHistory();
    });

    afterAll(() => {
        actions.get.restore();
        actions.getPreferredLocales.restore();
    });

    it('fetches the list of locales when the component mounts', () => {
        const store = createReduxStore();

        shallowUntilTarget(
            <AppLocalizationProvider store={store} />,
            AppLocalizationProviderBase
        );

        expect(actions.getPreferredLocales.callCount).toEqual(1);
    });

    // TODO: Fix this test and uncomment it.
    // I am failing to test the `componentDidUpdate` method of our component
    // after a store update. My expectation is that calling `store.dispatch`
    // runs the entire lifecycle of the wrapped component, but that doesn't
    // seem to happen, even when calling `wrapper.update()`.
    //
    // it('fetches the translation files once the locales list is loaded', () => {
    //     const store = createReduxStore();
    //
    //     const wrapper = shallowUntilTarget(
    //         <AppLocalizationProvider store={store} />,
    //         AppLocalizationProviderBase
    //     );
    //     expect(actions.get.callCount).toEqual(0);
    //
    //     store.dispatch(actions.selectLocales([ 'kg', 'gn' ]));
    //     wrapper.update();
    //     expect(actions.get.callCount).toEqual(1);
    // });

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
