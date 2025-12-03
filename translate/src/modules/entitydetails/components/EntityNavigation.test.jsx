import { createMemoryHistory } from 'history';
import React from 'react';
import sinon from 'sinon';

import { EntityViewProvider } from '~/context/EntityView';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { EntityNavigation } from './EntityNavigation';

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
  sinon.stub(history, 'push');
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
    navigator.clipboard = { writeText: sinon.stub() };
  });

  afterAll(() => {
    delete navigator.clipboard;
  });

  it('does not trigger actions on mount', () => {
    const { history } = mountEntityNav();

    expect(history.push.called).toBeFalsy();
    expect(navigator.clipboard.writeText.called).toBeFalsy();
  });

  it('puts a copy of string link on clipboard', () => {
    const { wrapper } = mountEntityNav();

    wrapper.find('button.link').simulate('click');
    expect(navigator.clipboard.writeText.getCalls()).toMatchObject([
      { args: ['http://localhost/kg/firefox/all-resources/?string=2'] },
    ]);
  });

  it('goes to the next entity on click on the Next button', () => {
    const { history, wrapper } = mountEntityNav();

    wrapper.find('button.next').simulate('click');
    expect(history.push.getCalls()).toMatchObject([
      { args: ['/kg/firefox/all-resources/?string=3'] },
    ]);
  });

  it('goes to the next entity on Alt + Down', () => {
    // Simulating the key presses on `document`.
    // See https://github.com/airbnb/enzyme/issues/426
    const eventsMap = {};
    document.addEventListener = sinon.spy((event, cb) => {
      eventsMap[event] = cb;
    });

    const { history } = mountEntityNav();

    const event = {
      preventDefault: sinon.spy(),
      key: 'ArrowDown',
      altKey: true,
      ctrlKey: false,
      shiftKey: false,
    };
    eventsMap.keydown(event);
    expect(history.push.getCalls()).toMatchObject([
      { args: ['/kg/firefox/all-resources/?string=3'] },
    ]);
  });

  it('goes to the previous entity on click on the Previous button', () => {
    const { history, wrapper } = mountEntityNav();

    wrapper.find('button.previous').simulate('click');
    expect(history.push.getCalls()).toMatchObject([
      { args: ['/kg/firefox/all-resources/?string=1'] },
    ]);
  });

  it('goes to the previous entity on Alt + Up', () => {
    // Simulating the key presses on `document`.
    // See https://github.com/airbnb/enzyme/issues/426
    const eventsMap = {};
    document.addEventListener = sinon.spy((event, cb) => {
      eventsMap[event] = cb;
    });

    const { history } = mountEntityNav();

    const event = {
      preventDefault: sinon.spy(),
      key: 'ArrowUp',
      altKey: true,
      ctrlKey: false,
      shiftKey: false,
    };
    eventsMap.keydown(event);
    expect(history.push.getCalls()).toMatchObject([
      { args: ['/kg/firefox/all-resources/?string=1'] },
    ]);
  });
});
