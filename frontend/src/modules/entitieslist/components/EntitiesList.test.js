import React from 'react';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import { actions } from '..';
import EntitiesList, { EntitiesListBase } from './EntitiesList';


// Entities shared between tests
const ENTITIES = [
    { pk: 1 },
    { pk: 2 },
];

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

    it('shows a loading animation when there are more entities to load', () => {
        const store = createReduxStore();

        store.dispatch(actions.receive(ENTITIES, true));

        const wrapper = shallowUntilTarget(<EntitiesList store={store} />, EntitiesListBase);
        const scroll  = wrapper.find('InfiniteScroll').shallow({ disableLifecycleMethods: true });

        expect(scroll.find('CircleLoader')).toHaveLength(1);
    });

    it("doesn't display a loading animation when there aren't entities to load", () => {
        const store = createReduxStore();

        store.dispatch(actions.receive(ENTITIES, false));

        const wrapper = shallowUntilTarget(<EntitiesList store={store} />, EntitiesListBase);
        const scroll  = wrapper.find('InfiniteScroll').shallow({ disableLifecycleMethods: true });

        expect(scroll.find('CircleLoader')).toHaveLength(0);
    });

    it("shows a loading animation when entities are being fetched from the server", () => {
        const store = createReduxStore();

        store.dispatch(actions.request());

        const wrapper = shallowUntilTarget(<EntitiesList store={store} />, EntitiesListBase);
        const scroll  = wrapper.find('InfiniteScroll').shallow({ disableLifecycleMethods: true });

        expect(scroll.find('CircleLoader')).toHaveLength(1);
    });

    it('shows the correct number of entities', () => {
        const store = createReduxStore();

        store.dispatch(actions.receive(ENTITIES, false));

        const wrapper = shallowUntilTarget(<EntitiesList store={ store } />, EntitiesListBase);

        expect(wrapper.find('Entity')).toHaveLength(2);
    });

    it('excludes current entities when requesting new entities', () => {
        const store = createReduxStore();

        store.dispatch(actions.receive(ENTITIES, false));

        const wrapper = shallowUntilTarget(<EntitiesList store={ store } />, EntitiesListBase);

        wrapper.instance().getMoreEntities();

        // Verify the 4th argument of `actions.get` is the list of current entities.
        expect(actions.get.args[0][3]).toEqual([1, 2]);
    });
});
