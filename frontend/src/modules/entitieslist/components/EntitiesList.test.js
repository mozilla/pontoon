import React from 'react';
import sinon from 'sinon';

import InfiniteScroll from 'react-infinite-scroller';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import { actions } from '..';
import EntitiesList, { EntitiesListBase } from './EntitiesList';


describe('<EntitiesList>', () => {
    let store;
    let entities;

    beforeAll(() => {
        const getMock = sinon.stub(actions, 'get');
        getMock.returns({type: 'whatever'});
    });

    beforeEach(() => {
        store = createReduxStore();

        entities = [
            { pk: 1 },
            { pk: 2 },
        ];
    });

    afterEach(() => {
        // Make sure tests do not pollute one another.
        actions.get.resetHistory();
    });

    afterAll(() => {
        actions.get.restore();
    });

    it('shows loading animation when there are more entities to load', () => {
        store.dispatch(actions.receive(entities, true));

        const wrapper = shallowUntilTarget(<EntitiesList store={store} />, EntitiesListBase);
        const scroll  = wrapper.find('InfiniteScroll').shallow({ disableLifecycleMethods: true });

        expect(scroll.find('EntitiesLoader')).toHaveLength(1);
    });

    it("doesn't display loading animation when there aren't entities to load", () => {
        store.dispatch(actions.receive(entities, false));

        const wrapper = shallowUntilTarget(<EntitiesList store={store} />, EntitiesListBase);
        const scroll  = wrapper.find('InfiniteScroll').shallow({ disableLifecycleMethods: true });

        expect(scroll.find('EntitiesLoader')).toHaveLength(0);
    });

    it("show loading animation when entities are being fetched from the server", () => {
        store.dispatch(actions.request());

        const wrapper = shallowUntilTarget(<EntitiesList store={store} />, EntitiesListBase);
        const scroll  = wrapper.find('InfiniteScroll').shallow({ disableLifecycleMethods: true });

        expect(scroll.find('EntitiesLoader')).toHaveLength(1);
    });

    it('shows the correct number of entities', () => {
        store.dispatch(actions.receive(entities, false));

        const wrapper = shallowUntilTarget(<EntitiesList store={ store } />, EntitiesListBase);

        expect(wrapper.find('Entity')).toHaveLength(2);
    });

    it('excludes current entities when requesting new entities', () => {
        store.dispatch(actions.receive(entities, false));

        const wrapper = shallowUntilTarget(<EntitiesList store={ store } />, EntitiesListBase);

        wrapper.instance().getMoreEntities();

        // Verify the 4th argument of `actions.get` is the list of current entities.
        expect(actions.get.args[0][3]).toEqual([1, 2]);
    });
});
