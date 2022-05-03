import { mount } from 'enzyme';
import { createMemoryHistory } from 'history';
import React from 'react';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';

import { LocationProvider } from '~/context/location';
import * as editor from '~/core/editor';
import { RECEIVE_ENTITIES } from '~/core/entities/actions';

import { createDefaultUser, createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import FluentEditor from './FluentEditor';

const NESTED_SELECTORS_STRING = `my-message =
    { $thing ->
        *[option] { $stuff ->
            [foo] FOO
            *[bar] BAR
        }
        [select] WOW
    }
`;

const RICH_MESSAGE_STRING = `my-message =
    Why so serious?
    .reason = Because
`;

const ENTITIES = [
  {
    pk: 1,
    original: 'my-message = Hello',
    translation: [
      {
        string: 'my-message = Salut',
      },
    ],
  },
  {
    pk: 2,
    original: 'my-message =\n    .my-attr = Something guud',
    translation: [
      { string: 'my-message =\n    .my-attr = Quelque chose de bien' },
    ],
  },
  {
    pk: 3,
    original: NESTED_SELECTORS_STRING,
    translation: [{ string: NESTED_SELECTORS_STRING }],
  },
  {
    pk: 4,
    original: 'my-message = Hello',
    translation: [{ string: '' }],
  },
  {
    pk: 5,
    original: RICH_MESSAGE_STRING,
    translation: [],
  },
];

function createComponent(entityPk = 1) {
  const store = createReduxStore();
  createDefaultUser(store);

  const history = createMemoryHistory({
    initialEntries: ['/kg/firefox/all-resources/'],
  });

  const wrapper = mount(
    <Provider store={store}>
      <LocationProvider history={history}>
        <MockLocalizationProvider>
          <FluentEditor />
        </MockLocalizationProvider>
      </LocationProvider>
    </Provider>,
  );

  store.dispatch({
    type: RECEIVE_ENTITIES,
    entities: ENTITIES,
    hasMore: false,
  });
  store.dispatch(editor.actions.reset());
  act(() => history.push(`?string=${entityPk}`));
  wrapper.update();

  return [wrapper, store];
}

describe('<FluentEditor>', () => {
  it('renders the simple form when passing a simple string', () => {
    const [wrapper] = createComponent(1);

    expect(wrapper.find('SourceEditor').exists()).toBeFalsy();
    expect(wrapper.find('SimpleEditor').exists()).toBeTruthy();
  });

  it('renders the simple form when passing a simple string with one attribute', () => {
    const [wrapper] = createComponent(2);

    expect(wrapper.find('SourceEditor').exists()).toBeFalsy();
    expect(wrapper.find('SimpleEditor').exists()).toBeTruthy();
  });

  it('renders the rich form when passing a supported rich message', () => {
    const [wrapper] = createComponent(5);

    expect(wrapper.find('RichEditor').exists()).toBeTruthy();
  });

  it('renders the source form when passing a complex string', () => {
    const [wrapper] = createComponent(3);

    expect(wrapper.find('SourceEditor').exists()).toBeTruthy();
    expect(wrapper.find('SimpleEditor').exists()).toBeFalsy();
  });

  it('converts translation when switching source mode', () => {
    const [wrapper] = createComponent(1);
    expect(wrapper.find('SimpleEditor').exists()).toBeTruthy();

    // Force source mode.
    wrapper.find('button.ftl').simulate('click');

    expect(wrapper.find('SourceEditor').exists()).toBeTruthy();
    expect(wrapper.find('textarea').text()).toEqual('my-message = Salut\n');
  });

  it('sets empty initial translation in source mode when untranslated', () => {
    const [wrapper] = createComponent(4);

    // Force source mode.
    wrapper.find('button.ftl').simulate('click');

    expect(wrapper.find('SourceEditor').exists()).toBeTruthy();
    expect(wrapper.find('textarea').text()).toEqual('my-message = ');
  });

  it('changes editor implementation when changing translation syntax', () => {
    const [wrapper, store] = createComponent(1);
    expect(wrapper.find('SimpleEditor').exists()).toBeTruthy();

    // Change translation to a rich string.
    store.dispatch(editor.actions.update(RICH_MESSAGE_STRING, 'external'));
    wrapper.update();

    expect(wrapper.find('RichEditor').exists()).toBeTruthy();
  });
});
