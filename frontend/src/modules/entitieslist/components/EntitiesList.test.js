import React from 'react';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import { actions } from '..';
import EntitiesList, { EntitiesListBase } from './EntitiesList';


describe('<EntitiesList>', () => {
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

    it('shows the correct number of entities', () => {
        const store = createReduxStore();

        const entities = [
            { pk: 1 },
            { pk: 2 },
        ];
        store.dispatch(actions.receive(entities, false));
        const wrapper = shallowUntilTarget(<EntitiesList store={ store } />, EntitiesListBase);
        expect(wrapper.find('Entity')).toHaveLength(2);
    });

    it('excludes current entities when requesting new entities', () => {
        const store = createReduxStore();

        const entities = [
            { pk: 1 },
            { pk: 2 },
        ];
        store.dispatch(actions.receive(entities, false));

        const wrapper = shallowUntilTarget(<EntitiesList store={ store } />, EntitiesListBase);

        wrapper.instance().getMoreEntities();
        // Verify the 4th argument of `actions.get` is the list of current entities.
        expect(actions.get.args[0][3]).toEqual([1, 2]);
    });
});
