import { createMemoryHistory } from 'history';
// import { mockAllIsIntersecting } from 'react-intersection-observer/test-utils';

import * as BatchActions from '~/modules/batchactions/actions';
import * as EntitiesActions from '~/modules/entities/actions';

import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';

import { EntitiesList } from './EntitiesList';
import { vi } from 'vitest';
import { fireEvent } from '@testing-library/react';

// Entities shared between tests
const ENTITIES = [
  { pk: 1, translation: { string: '', errors: [], warnings: [] } },
  { pk: 2, translation: { string: '', errors: [], warnings: [] } },
];

describe('<EntitiesList>', () => {
  beforeAll(() => {
    vi.spyOn(BatchActions, 'resetSelection').mockReturnValue({
      type: 'whatever',
    });
    vi.spyOn(BatchActions, 'toggleSelection').mockReturnValue({
      type: 'whatever',
    });
    vi.spyOn(EntitiesActions, 'getEntities').mockReturnValue({
      type: 'whatever',
    });
  });

  beforeEach(() => {
    // Make sure tests do not pollute one another.
    BatchActions.resetSelection.mockClear();
    BatchActions.toggleSelection.mockClear();
    EntitiesActions.getEntities.mockClear();
    // mockAllIsIntersecting(true);
  });

  afterAll(() => {
    vi.restoreAllMocks();
  });
  // FIXME: https://github.com/mozilla/pontoon/issues/3883
  it.skip('shows a loading animation when there are more entities to load', () => {
    const store = createReduxStore();
    store.dispatch({
      type: EntitiesActions.RECEIVE_ENTITIES,
      entities: ENTITIES,
      hasMore: true,
    });
    const wrapper = mountComponentWithStore(EntitiesList, store);
    expect(wrapper.queryByTestId('skeleton-loader')).toBeInTheDocument();
  });

  it("doesn't display a loading animation when there aren't entities to load", () => {
    const store = createReduxStore();
    store.dispatch({
      type: EntitiesActions.RECEIVE_ENTITIES,
      entities: ENTITIES,
      hasMore: false,
    });
    const wrapper = mountComponentWithStore(EntitiesList, store);

    expect(wrapper.queryByTestId('skeleton-loader')).not.toBeInTheDocument();
  });

  // FIXME: https://github.com/mozilla/pontoon/issues/3883
  it.skip('shows a loading animation when entities are being fetched from the server', () => {
    const store = createReduxStore();
    store.dispatch({ type: EntitiesActions.REQUEST_ENTITIES });
    const wrapper = mountComponentWithStore(EntitiesList, store);

    expect(wrapper.queryByTestId('skeleton-loader')).toBeInTheDocument();
  });

  it('shows the correct number of entities', () => {
    const history = createMemoryHistory({
      initialEntries: ['/kg/firefox/all-resources/?string=1'],
    });

    const store = createReduxStore();
    store.dispatch({
      type: EntitiesActions.RECEIVE_ENTITIES,
      entities: ENTITIES,
      hasMore: false,
    });
    const wrapper = mountComponentWithStore(EntitiesList, store, {}, history);

    expect(wrapper.queryAllByTestId('entity')).toHaveLength(2);
  });

  // FIXME: https://github.com/mozilla/pontoon/issues/3883
  it.skip('when requesting new entities, load page 2', () => {
    vi.useFakeTimers();
    // mockAllIsIntersecting(false);

    const store = createReduxStore();
    store.dispatch({
      type: EntitiesActions.RECEIVE_ENTITIES,
      entities: ENTITIES,
      hasMore: true,
    });
    mountComponentWithStore(EntitiesList, store);

    // mockAllIsIntersecting(true);
    vi.advanceTimersByTime(100); // default value for react-infinite-scroll-hook delayInMs

    expect(EntitiesActions.getEntities.args[0][1]).toEqual(2);
  });

  it('redirects to the first entity when none is selected', () => {
    const history = createMemoryHistory({
      initialEntries: ['/kg/firefox/all-resources/'],
    });
    const spy = vi.fn();
    history.listen(spy);

    const store = createReduxStore();
    store.dispatch({
      type: EntitiesActions.RECEIVE_ENTITIES,
      entities: ENTITIES,
      hasMore: false,
    });

    mountComponentWithStore(EntitiesList, store, {}, history);

    expect(spy.mock.calls).toMatchObject([
      [
        expect.objectContaining({
          pathname: '/kg/firefox/all-resources/',
          search: '?string=1',
          hash: '',
        }),
        'REPLACE',
      ],
    ]);
  });

  it('toggles entity for batch editing', () => {
    const store = createReduxStore();
    store.dispatch({
      type: EntitiesActions.RECEIVE_ENTITIES,
      entities: ENTITIES,
      hasMore: false,
    });

    // HACK to get isTranslator === true in Entity
    createDefaultUser(store, { can_translate_locales: [''] });

    const { container } = mountComponentWithStore(EntitiesList, store);

    fireEvent.click(container.querySelector('.entity .status'));

    expect(BatchActions.toggleSelection).toHaveBeenCalledTimes(1);
  });
});
