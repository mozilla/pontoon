import React from 'react';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import { actions } from '..';
import History, { HistoryBase } from './History';


describe('<History>', () => {
    beforeAll(() => {
        sinon.stub(actions, 'get');
        actions.get.returns({
            type: 'whatever',
        });
    });

    afterEach(() => {
        actions.get.resetHistory();
    });

    afterAll(() => {
        actions.get.restore();
    });

    it('shows the correct number of translations', () => {
        const initialState = {
            history: {
                translations: [
                    { pk: 1 },
                    { pk: 2 },
                    { pk: 3 },
                ],
            },
        };
        const store = createReduxStore(initialState);
        const wrapper = shallowUntilTarget(<History store={ store } />, HistoryBase);

        expect(wrapper.find('Translation')).toHaveLength(3);
    });

    it('gets a new history when the entity is created', () => {
        const initialState = {};
        const store = createReduxStore(initialState);
        shallowUntilTarget(<History store={ store } />, HistoryBase);

        expect(actions.get.callCount).toEqual(1);

        // TODO: complete this to test a change after the component has been
        // mounted.
        // I haven't been able to do that yet. In theory, we should update
        // the store to change the current route, so that the selected entity
        // becomes different, then update the `wrapper` and check that while
        // updating, it called `actions.get`. That's the theory anyway, and
        // in practice I haven't been able to make that work. Maybe there's a
        // different way to test this, and I'll need to figure it out someday.
    });
});
