import React from 'react';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import { actions } from '..';
import Locales, { LocalesBase } from './Locales';


describe('<Locales>', () => {
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
            otherlocales: {
                translations: [
                    { code: 'ar' },
                    { code: 'br' },
                    { code: 'cr' },
                ],
            }
        };
        const store = createReduxStore(initialState);
        const wrapper = shallowUntilTarget(<Locales store={ store } />, LocalesBase);

        expect(wrapper.find('li')).toHaveLength(3);
    });

    it('gets a new list of otherlocales when the entity is created', () => {
        const initialState = {};
        const store = createReduxStore(initialState);
        shallowUntilTarget(<Locales store={ store } />, LocalesBase);

        expect(actions.get.callCount).toEqual(1);
    });
});
