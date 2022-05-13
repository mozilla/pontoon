import { mount } from 'enzyme';
import { createMemoryHistory } from 'history';
import React from 'react';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';

import { LocationProvider } from '~/context/Location';
import { RECEIVE_ENTITIES } from '~/core/entities/actions';

import { createDefaultUser, createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { EditorMenu } from './EditorMenu';
import { EditorSettings } from './EditorSettings';
import { KeyboardShortcuts } from './KeyboardShortcuts';
import { TranslationLength } from './TranslationLength';

const SELECTED_ENTITY = {
  pk: 1,
  original: 'le test',
  original_plural: 'les tests',
  translation: [{ string: 'test' }, { string: 'test plural' }],
};

function createEditorMenu({
  forceSuggestions = true,
  isAuthenticated = true,
  entity = SELECTED_ENTITY,
  firstItemHook = null,
} = {}) {
  const store = createReduxStore();
  createDefaultUser(store, {
    is_authenticated: isAuthenticated,
    settings: {
      force_suggestions: forceSuggestions,
    },
  });

  store.dispatch({
    type: RECEIVE_ENTITIES,
    entities: [entity],
    hasMore: false,
  });

  const history = createMemoryHistory({
    initialEntries: ['/kg/firefox/all-resources/'],
  });

  const wrapper = mount(
    <Provider store={store}>
      <LocationProvider history={history}>
        <MockLocalizationProvider>
          <EditorMenu firstItemHook={firstItemHook} />
        </MockLocalizationProvider>
      </LocationProvider>
    </Provider>,
  );

  act(() => history.push(`?string=1`));
  wrapper.update();

  return wrapper;
}

function expectHiddenSettingsAndActions(wrapper) {
  expect(wrapper.find('button')).toHaveLength(0);
  expect(wrapper.find(EditorSettings)).toHaveLength(0);
  expect(wrapper.find(KeyboardShortcuts)).toHaveLength(0);
  expect(wrapper.find(TranslationLength)).toHaveLength(0);
  expect(wrapper.find('#editor-EditorMenu--button-copy')).toHaveLength(0);
}

describe('<EditorMenu>', () => {
  it('renders correctly', () => {
    const wrapper = createEditorMenu();

    // 3 buttons to control the editor.
    expect(wrapper.find('.action-copy').exists()).toBeTruthy();
    expect(wrapper.find('.action-clear').exists()).toBeTruthy();
    expect(wrapper.find('EditorMainAction')).toHaveLength(1);
  });

  it('hides the settings and actions when the user is logged out', () => {
    const wrapper = createEditorMenu({ isAuthenticated: false });

    expectHiddenSettingsAndActions(wrapper);

    expect(
      wrapper.find('#editor-EditorMenu--sign-in-to-translate'),
    ).toHaveLength(1);
  });

  it('hides the settings and actions when the entity is read-only', () => {
    const entity = { ...SELECTED_ENTITY, readonly: true };
    const wrapper = createEditorMenu({ entity });

    expectHiddenSettingsAndActions(wrapper);

    expect(
      wrapper.find('#editor-EditorMenu--read-only-localization'),
    ).toHaveLength(1);
  });

  it('accepts a firstItemHook and shows it as its first child', () => {
    const firstItemHook = <p>Hello</p>;
    const wrapper = createEditorMenu({ firstItemHook });

    expect(wrapper.find('menu').children().first().text()).toEqual('Hello');
  });
});
