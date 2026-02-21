import React from 'react';
import { createMemoryHistory } from 'history';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';

import { EntityView } from '~/context/EntityView';
import { LocationProvider } from '~/context/Location';

import { createDefaultUser, createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { EditorMenu } from './EditorMenu';
import { render } from '@testing-library/react';

const SELECTED_ENTITY = {
  pk: 1,
  original: 'le test',
  translation: { string: 'test' },
};

function createEditorMenu({
  isAuthenticated = true,
  entity = SELECTED_ENTITY,
} = {}) {
  const store = createReduxStore();
  createDefaultUser(store, {
    is_authenticated: isAuthenticated,
    settings: { force_suggestions: true },
  });

  const history = createMemoryHistory({
    initialEntries: ['/kg/firefox/all-resources/'],
  });

  const wrapper = render(
    <Provider store={store}>
      <LocationProvider history={history}>
        <MockLocalizationProvider>
          <EntityView.Provider value={{ entity }}>
            <EditorMenu />
          </EntityView.Provider>
        </MockLocalizationProvider>
      </LocationProvider>
    </Provider>,
  );

  act(() => history.push(`?string=1`));

  return wrapper;
}

function expectHiddenSettingsAndActions({ container, queryByRole }) {
  expect(queryByRole('button')).toBeNull();
  expect(container.querySelector('.editor-settings')).toBeNull();
  expect(container.querySelector('.keyboard-shortcuts')).toBeNull();
  expect(container.querySelector('.translation-length')).toBeNull();
  expect(queryByRole('button', { name: /^COPY$/i })).toBeNull();
}

describe('<EditorMenu>', () => {
  it('does not render while loading', () => {
    const { container } = createEditorMenu({ isAuthenticated: null });
    expect(container.querySelector('menu')).toBeEmptyDOMElement();
  });

  it('renders correctly', () => {
    const { getByRole } = createEditorMenu();

    // 3 buttons to control the editor.
    getByRole('button', { name: /^COPY$/i });
    getByRole('button', { name: /^CLEAR$/i });
    getByRole('button', { name: /^SUGGEST$/i });
  });

  it('hides the settings and actions when the user is logged out', () => {
    const wrapper = createEditorMenu({ isAuthenticated: false });

    expectHiddenSettingsAndActions(wrapper);

    wrapper.getByText(/SIGN IN/i);
  });

  it('hides the settings and actions when the entity is read-only', () => {
    const entity = { ...SELECTED_ENTITY, readonly: true };
    const wrapper = createEditorMenu({ entity });

    expectHiddenSettingsAndActions(wrapper);

    wrapper.getByText(/THIS IS A READ-ONLY LOCALIZATION/i);
  });
});
