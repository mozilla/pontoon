import React from 'react';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import * as entities from 'core/entities';
import * as navigation from 'core/navigation';
import * as batchactions from 'modules/batchactions';

import EntitiesList, { EntitiesListBase } from './EntitiesList';

// Entities shared between tests
const ENTITIES = [{ pk: 1 }, { pk: 2 }];

describe('<EntitiesList>', () => {
    beforeAll(() => {
        sinon
            .stub(batchactions.actions, 'resetSelection')
            .returns({ type: 'whatever' });
        sinon
            .stub(batchactions.actions, 'toggleSelection')
            .returns({ type: 'whatever' });
        sinon.stub(entities.actions, 'get').returns({ type: 'whatever' });
        sinon
            .stub(navigation.actions, 'updateEntity')
            .returns({ type: 'whatever' });
    });

    afterEach(() => {
        // Make sure tests do not pollute one another.
        batchactions.actions.resetSelection.resetHistory();
        batchactions.actions.toggleSelection.resetHistory();
        entities.actions.get.resetHistory();
        navigation.actions.updateEntity.resetHistory();
    });

    afterAll(() => {
        batchactions.actions.resetSelection.restore();
        batchactions.actions.toggleSelection.restore();
        entities.actions.get.restore();
        navigation.actions.updateEntity.restore();
    });

    it('shows a loading animation when there are more entities to load', () => {
        const store = createReduxStore();

        store.dispatch(entities.actions.receive(ENTITIES, true));

        const wrapper = shallowUntilTarget(
            <EntitiesList store={store} />,
            EntitiesListBase,
        );
        const scroll = wrapper
            .find('InfiniteScroll')
            .shallow({ disableLifecycleMethods: true });

        expect(scroll.find('SkeletonLoader')).toHaveLength(1);
    });

    it("doesn't display a loading animation when there aren't entities to load", () => {
        const store = createReduxStore();

        store.dispatch(entities.actions.receive(ENTITIES, false));

        const wrapper = shallowUntilTarget(
            <EntitiesList store={store} />,
            EntitiesListBase,
        );
        const scroll = wrapper
            .find('InfiniteScroll')
            .shallow({ disableLifecycleMethods: true });

        expect(scroll.find('SkeletonLoader')).toHaveLength(0);
    });

    it('shows a loading animation when entities are being fetched from the server', () => {
        const store = createReduxStore();

        store.dispatch(entities.actions.request());

        const wrapper = shallowUntilTarget(
            <EntitiesList store={store} />,
            EntitiesListBase,
        );
        const scroll = wrapper
            .find('InfiniteScroll')
            .shallow({ disableLifecycleMethods: true });

        expect(scroll.find('SkeletonLoader')).toHaveLength(1);
    });

    it('shows the correct number of entities', () => {
        const store = createReduxStore();

        store.dispatch(entities.actions.receive(ENTITIES, false));

        const wrapper = shallowUntilTarget(
            <EntitiesList store={store} />,
            EntitiesListBase,
        );

        expect(wrapper.find('Entity')).toHaveLength(2);
    });

    it('excludes current entities when requesting new entities', () => {
        const store = createReduxStore();

        store.dispatch(entities.actions.receive(ENTITIES, false));

        const wrapper = shallowUntilTarget(
            <EntitiesList store={store} />,
            EntitiesListBase,
        );

        wrapper.instance().getMoreEntities();

        // Verify the 5th argument of `actions.get` is the list of current entities.
        expect(entities.actions.get.args[0][4]).toEqual([1, 2]);
    });

    it('redirects to the first entity when none is selected', () => {
        const store = createReduxStore();

        store.dispatch(entities.actions.receive(ENTITIES, false));

        shallowUntilTarget(<EntitiesList store={store} />, EntitiesListBase);

        expect(batchactions.actions.resetSelection.calledOnce).toBeTruthy();
        expect(navigation.actions.updateEntity.calledOnce).toBeTruthy();

        const call = navigation.actions.updateEntity.firstCall;
        expect(call.args[1]).toEqual(ENTITIES[0].pk.toString());
    });

    it('toggles entity for batch editing', () => {
        const store = createReduxStore();

        store.dispatch(entities.actions.receive(ENTITIES, false));

        const wrapper = shallowUntilTarget(
            <EntitiesList store={store} />,
            EntitiesListBase,
        );

        wrapper.instance().toggleForBatchEditing(ENTITIES[0].pk, false);

        expect(batchactions.actions.toggleSelection.calledOnce).toBeTruthy();
    });
});
