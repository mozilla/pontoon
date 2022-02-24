import sinon from 'sinon';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import * as entitiesActions from '~/core/entities/actions';
import * as navigationActions from '~/core/navigation/actions';
import * as batchActions from '~/modules/batchactions/actions';

import EntitiesList, { EntitiesListBase } from './EntitiesList';

// Entities shared between tests
const ENTITIES = [
  { pk: 1, translation: [{ string: '', errors: [], warnings: [] }] },
  { pk: 2, translation: [{ string: '', errors: [], warnings: [] }] },
];

describe('<EntitiesList>', () => {
  beforeAll(() => {
    sinon.stub(batchActions, 'resetSelection').returns({ type: 'whatever' });
    sinon.stub(batchActions, 'toggleSelection').returns({ type: 'whatever' });
    sinon.stub(entitiesActions, 'get').returns({ type: 'whatever' });
    sinon.stub(navigationActions, 'updateEntity').returns({ type: 'whatever' });
  });

  afterEach(() => {
    // Make sure tests do not pollute one another.
    batchActions.resetSelection.resetHistory();
    batchActions.toggleSelection.resetHistory();
    entitiesActions.get.resetHistory();
    navigationActions.updateEntity.resetHistory();
  });

  afterAll(() => {
    batchActions.resetSelection.restore();
    batchActions.toggleSelection.restore();
    entitiesActions.get.restore();
    navigationActions.updateEntity.restore();
  });

  it('shows a loading animation when there are more entities to load', () => {
    const store = createReduxStore();

    store.dispatch(entitiesActions.receive(ENTITIES, true));

    const root = mountComponentWithStore(EntitiesList, store);
    const wrapper = root.find(EntitiesListBase);
    const scroll = wrapper.find('InfiniteScroll');

    expect(scroll.find('SkeletonLoader')).toHaveLength(1);
  });

  it("doesn't display a loading animation when there aren't entities to load", () => {
    const store = createReduxStore();

    store.dispatch(entitiesActions.receive(ENTITIES, false));

    const root = mountComponentWithStore(EntitiesList, store);
    const wrapper = root.find(EntitiesListBase);
    const scroll = wrapper.find('InfiniteScroll');

    expect(scroll.find('SkeletonLoader')).toHaveLength(0);
  });

  it('shows a loading animation when entities are being fetched from the server', () => {
    const store = createReduxStore();

    store.dispatch(entitiesActions.request());

    const root = mountComponentWithStore(EntitiesList, store);
    const wrapper = root.find(EntitiesListBase);
    const scroll = wrapper.find('InfiniteScroll');

    expect(scroll.find('SkeletonLoader')).toHaveLength(1);
  });

  it('shows the correct number of entities', () => {
    const store = createReduxStore();

    store.dispatch(entitiesActions.receive(ENTITIES, false));

    const root = mountComponentWithStore(EntitiesList, store);
    const wrapper = root.find(EntitiesListBase);

    expect(wrapper.find('Entity')).toHaveLength(2);
  });

  it.skip('excludes current entities when requesting new entities', () => {
    const store = createReduxStore();

    store.dispatch(entitiesActions.receive(ENTITIES, false));

    const root = mountComponentWithStore(EntitiesList, store);
    const wrapper = root.find(EntitiesListBase);

    // No longer available externally, and only called from react-infinite-scroller
    wrapper.instance().getMoreEntities();

    // Verify the 5th argument of `actions.get` is the list of current entities.
    expect(entitiesActions.get.args[0][4]).toEqual([1, 2]);
  });

  it('redirects to the first entity when none is selected', () => {
    const store = createReduxStore();

    store.dispatch(entitiesActions.receive(ENTITIES, false));

    mountComponentWithStore(EntitiesList, store);

    expect(batchActions.resetSelection.calledOnce).toBeTruthy();
    expect(navigationActions.updateEntity.calledOnce).toBeTruthy();

    const call = navigationActions.updateEntity.firstCall;
    expect(call.args[1]).toEqual(ENTITIES[0].pk.toString());
  });

  it.skip('toggles entity for batch editing', () => {
    const store = createReduxStore();

    store.dispatch(entitiesActions.receive(ENTITIES, false));

    const root = mountComponentWithStore(EntitiesList, store);
    const wrapper = root.find(EntitiesListBase);

    // No longer available externally
    wrapper.instance().toggleForBatchEditing(ENTITIES[0].pk, false);

    expect(batchActions.toggleSelection.calledOnce).toBeTruthy();
  });
});
