import { createMemoryHistory } from 'history';
// import { mockAllIsIntersecting } from 'react-intersection-observer/test-utils';

import * as BatchActions from '~/modules/batchactions/actions';
import * as EntitiesActions from '~/modules/entities/actions';
import * as uxaction from '~/api/uxaction';

import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';

import { EntitiesList } from './EntitiesList';
import { expect, vi } from 'vitest';

// Entities shared between tests
const ENTITIES = [
  { pk: 1, translation: { string: '', errors: [], warnings: [] } },
  { pk: 2, translation: { string: '', errors: [], warnings: [] } },
];

describe('<EntitiesList>', () => {
  let mockLogUXAction;

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
    mockLogUXAction = vi
      .spyOn(uxaction, 'logUXAction')
      .mockImplementation(() => {});
  });

  beforeEach(() => {
    // Make sure tests do not pollute one another.
    BatchActions.resetSelection.mockClear();
    BatchActions.toggleSelection.mockClear();
    EntitiesActions.getEntities.mockClear();
    uxaction.logUXAction.mockClear();
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
    expect(wrapper.find('SkeletonLoader')).toHaveLength(1);
  });

  it("doesn't display a loading animation when there aren't entities to load", () => {
    const store = createReduxStore();
    store.dispatch({
      type: EntitiesActions.RECEIVE_ENTITIES,
      entities: ENTITIES,
      hasMore: false,
    });
    const wrapper = mountComponentWithStore(EntitiesList, store);

    expect(wrapper.find('SkeletonLoader')).toHaveLength(0);
  });

  // FIXME: https://github.com/mozilla/pontoon/issues/3883
  it.skip('shows a loading animation when entities are being fetched from the server', () => {
    const store = createReduxStore();
    store.dispatch({ type: EntitiesActions.REQUEST_ENTITIES });
    const wrapper = mountComponentWithStore(EntitiesList, store);

    expect(wrapper.find('SkeletonLoader')).toHaveLength(1);
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

    expect(wrapper.find('Entity')).toHaveLength(2);
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

    const wrapper = mountComponentWithStore(EntitiesList, store);

    wrapper.find('.entity .status').first().simulate('click');

    expect(BatchActions.toggleSelection).toHaveBeenCalledTimes(1);
  });

  it('does not log UX action when unauthenticated user loads page with search parameter', () => {
    const history = createMemoryHistory({
      initialEntries: [
        '/kg/firefox/all-resources/?string=1&search=test&search_identifiers=true',
      ],
    });

    const store = createReduxStore();
    store.dispatch({
      type: EntitiesActions.RECEIVE_ENTITIES,
      entities: ENTITIES,
      hasMore: false,
    });

    createDefaultUser(store, { is_authenticated: false });

    mountComponentWithStore(EntitiesList, store, {}, history);

    // Verify that logUXAction was NOT called for unauthenticated user
    expect(mockLogUXAction).not.toHaveBeenCalled();
  });

  it('logs UX action when authenticated user loads page with search parameter', () => {
    const history = createMemoryHistory({
      initialEntries: [
        '/kg/firefox/all-resources/?string=1&search=test&search_identifiers=true',
      ],
    });

    const store = createReduxStore();
    store.dispatch({
      type: EntitiesActions.RECEIVE_ENTITIES,
      entities: ENTITIES,
      hasMore: false,
    });

    createDefaultUser(store, { is_authenticated: true });

    mountComponentWithStore(EntitiesList, store, {}, history);

    // Verify that logUXAction was called when component mounted with search parameters
    expect(mockLogUXAction).toHaveBeenCalledWith(
      'Load: String list with search parameter',
      'Search Options Statistics',
      {
        search_exclude_source_strings: false,
        search_identifiers: true,
        search_match_case: false,
        search_match_whole_word: false,
        search_rejected_translations: false,
      },
    );
  });

  it('preserves search and list parameters when selecting an entity', () => {
    const history = createMemoryHistory({
      initialEntries: [
        '/kg/firefox/all-resources/?list=1,2&search=test&string=1',
      ],
    });

    const spy = vi.fn();
    history.listen(spy);

    const store = createReduxStore();
    store.dispatch({
      type: EntitiesActions.RECEIVE_ENTITIES,
      entities: ENTITIES,
      hasMore: false,
    });

    const wrapper = mountComponentWithStore(EntitiesList, store, {}, history);

    wrapper.find('.entity').at(1).simulate('click');

    expect(spy).toHaveBeenCalled();
    const lastCall = spy.mock.calls[spy.mock.calls.length - 1];
    expect(lastCall[0]).toMatchObject({
      pathname: '/kg/firefox/all-resources/',
      search: expect.stringContaining('list=1,2'),
    });

    expect(lastCall[0].search).toContain('search=test');
    expect(lastCall[0].search).toContain('string=2');
  });
});
