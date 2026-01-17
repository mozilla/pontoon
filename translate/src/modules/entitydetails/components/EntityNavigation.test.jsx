import { createMemoryHistory } from 'history';
import React from 'react';

import { EntityViewProvider } from '~/context/EntityView';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { EntityNavigation } from './EntityNavigation';
import { vi } from 'vitest';
import { fireEvent } from '@testing-library/react';

function mountEntityNav() {
  const store = createReduxStore({
    entities: {
      entities: [
        { pk: 1, translation: { string: '', errors: [], warnings: [] } },
        { pk: 2, translation: { string: '', errors: [], warnings: [] } },
        { pk: 3, translation: { string: '', errors: [], warnings: [] } },
      ],
    },
  });
  const history = createMemoryHistory({
    initialEntries: ['/kg/firefox/all-resources/?string=2'],
  });
  vi.spyOn(history, 'push');
  const wrapper = mountComponentWithStore(
    () => (
      <EntityViewProvider>
        <EntityNavigation />
      </EntityViewProvider>
    ),
    store,
    {},
    history,
  );
  return { history, wrapper };
}

describe('<EntityNavigation>', () => {
  beforeAll(() => {
    navigator.clipboard = { writeText: vi.fn() };
  });

  afterAll(() => {
    delete navigator.clipboard;
  });

  it('does not trigger actions on mount', () => {
    const { history } = mountEntityNav();

    expect(history.push).not.toHaveBeenCalled();
    expect(navigator.clipboard.writeText).not.toHaveBeenCalled();
  });

  it('puts a copy of string link on clipboard', () => {
    const { wrapper } = mountEntityNav();

    fireEvent.click(wrapper.container.querySelector('button.link'));
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      'http://localhost/kg/firefox/all-resources/?string=2',
    );
  });

  it('goes to the next entity on click on the Next button', () => {
    const { history, wrapper } = mountEntityNav();

    fireEvent.click(wrapper.container.querySelector('button.next'));
    expect(history.push).toHaveBeenCalledWith(
      '/kg/firefox/all-resources/?string=3',
    );
  });

  it('goes to the next entity on Alt + Down', () => {
    // Simulating the key presses on `document`.
    // See https://github.com/airbnb/enzyme/issues/426
    const eventsMap = {};
    document.addEventListener = vi.fn((event, cb) => {
      eventsMap[event] = cb;
    });

    const { history } = mountEntityNav();

    const event = {
      preventDefault: vi.fn(),
      key: 'ArrowDown',
      altKey: true,
      ctrlKey: false,
      shiftKey: false,
    };
    eventsMap.keydown(event);
    expect(history.push).toHaveBeenCalledWith(
      '/kg/firefox/all-resources/?string=3',
    );
  });

  it('goes to the previous entity on click on the Previous button', () => {
    const { history, wrapper } = mountEntityNav();

    fireEvent.click(wrapper.container.querySelector('button.previous'));
    expect(history.push).toHaveBeenCalledWith(
      '/kg/firefox/all-resources/?string=1',
    );
  });

  it('goes to the previous entity on Alt + Up', () => {
    // Simulating the key presses on `document`.
    // See https://github.com/airbnb/enzyme/issues/426
    const eventsMap = {};
    document.addEventListener = vi.fn((event, cb) => {
      eventsMap[event] = cb;
    });

    const { history } = mountEntityNav();

    const event = {
      preventDefault: vi.fn(),
      key: 'ArrowUp',
      altKey: true,
      ctrlKey: false,
      shiftKey: false,
    };
    eventsMap.keydown(event);
    expect(history.push).toHaveBeenCalledWith(
      '/kg/firefox/all-resources/?string=1',
    );
  });
});
