import React from 'react';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import { actions } from '..';
import UserAutoUpdater, { UserAutoUpdaterBase } from './UserAutoUpdater';


describe('<UserAutoUpdater>', () => {
    beforeAll(() => {
        sinon.stub(actions, 'get');
        actions.get.returns({
            type: 'whatever',
        });

        jest.useFakeTimers();
    });

    afterEach(() => {
        actions.get.resetHistory();
        jest.clearAllTimers();
    })

    afterAll(() => {
        actions.get.restore();
    });

    it('fetches user data on mount', () => {
        const store = createReduxStore();
        shallowUntilTarget(<UserAutoUpdater store={ store } />, UserAutoUpdaterBase);

        expect(actions.get.callCount).toEqual(1);
    });

    it('fetches user data every 2 minutes', () => {
        const store = createReduxStore();
        shallowUntilTarget(<UserAutoUpdater store={ store } />, UserAutoUpdaterBase);

        jest.runTimersToTime(2 * 60 * 1000);
        expect(actions.get.callCount).toEqual(2);

        jest.runTimersToTime(2 * 60 * 1000);
        expect(actions.get.callCount).toEqual(3);

        // If less than 2 minutes have passed, it doesn't trigger.
        jest.runTimersToTime(60 * 1000);
        expect(actions.get.callCount).toEqual(3);
    });
});
