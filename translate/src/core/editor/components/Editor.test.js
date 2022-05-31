import ftl from '@fluent/dedent';
import { mount } from 'enzyme';
import { createMemoryHistory } from 'history';
import React, { useContext } from 'react';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';
import sinon from 'sinon';

import * as TranslationAPI from '~/api/translation';
import { EditorActions, EditorProvider } from '~/context/Editor';
import { LocationProvider } from '~/context/Location';
import { RECEIVE_ENTITIES } from '~/core/entities/actions';

import { createDefaultUser, createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { Editor } from './Editor';

const NESTED_SELECTORS_STRING = ftl`
  my-message =
      { $thing ->
          *[option] { $stuff ->
              [foo] FOO
              *[bar] BAR
          }
          [select] WOW
      }
  `;

const RICH_MESSAGE_STRING = ftl`
  my-message =
    Why so serious?
    .reason = Because
  `;

const ENTITIES = [
  {
    pk: 1,
    format: 'ftl',
    original: 'my-message = Hello',
    translation: [
      {
        string: 'my-message = Salut',
      },
    ],
  },
  {
    pk: 2,
    format: 'ftl',
    original: 'my-message =\n    .my-attr = Something guud',
    translation: [
      { string: 'my-message =\n    .my-attr = Quelque chose de bien' },
    ],
  },
  {
    pk: 3,
    format: 'ftl',
    original: NESTED_SELECTORS_STRING,
    translation: [{ string: NESTED_SELECTORS_STRING }],
  },
  {
    pk: 4,
    format: 'ftl',
    original: 'my-message = Hello',
    translation: [{ string: '' }],
  },
  {
    pk: 5,
    format: 'ftl',
    original: RICH_MESSAGE_STRING,
    translation: [],
  },
];

function mountEditor(entityPk = 1) {
  const store = createReduxStore();
  createDefaultUser(store);

  const history = createMemoryHistory({
    initialEntries: ['/kg/firefox/all-resources/'],
  });

  let actions;
  const Spy = () => {
    actions = useContext(EditorActions);
    return null;
  };

  const wrapper = mount(
    <Provider store={store}>
      <LocationProvider history={history}>
        <MockLocalizationProvider>
          <EditorProvider>
            <Spy />
            <Editor />
          </EditorProvider>
        </MockLocalizationProvider>
      </LocationProvider>
    </Provider>,
  );

  store.dispatch({
    type: RECEIVE_ENTITIES,
    entities: ENTITIES,
    hasMore: false,
  });
  act(() => history.push(`?string=${entityPk}`));
  wrapper.update();

  return [wrapper, actions];
}

describe('<Editor>', () => {
  it('renders the simple form when passing a simple string', () => {
    const [wrapper] = mountEditor(1);

    const input = wrapper.find('GenericTranslationForm textarea');
    expect(input).toHaveLength(1);
    expect(input.prop('value')).toBe('Salut');
  });

  it('renders the simple form when passing a simple string with one attribute', () => {
    const [wrapper] = mountEditor(2);

    const input = wrapper.find('GenericTranslationForm textarea');
    expect(input).toHaveLength(1);
    expect(input.prop('value')).toBe('Quelque chose de bien');
  });

  it('renders the rich form when passing a supported rich message', () => {
    const [wrapper] = mountEditor(5);

    expect(wrapper.find('RichTranslationForm textarea')).toHaveLength(2);
  });

  it('renders the source form when passing a complex string', () => {
    const [wrapper] = mountEditor(3);

    const input = wrapper.find('GenericTranslationForm textarea');
    expect(input).toHaveLength(1);
    expect(input.prop('value')).toBe(NESTED_SELECTORS_STRING);
  });

  it('converts translation when switching source mode', () => {
    const [wrapper] = mountEditor(1);

    // Force source mode.
    wrapper.find('button.ftl').simulate('click');

    const input = wrapper.find('GenericTranslationForm textarea');
    expect(input).toHaveLength(1);
    expect(input.prop('value')).toBe('my-message = Salut\n');
  });

  it('sets empty initial translation in source mode when untranslated', () => {
    const [wrapper] = mountEditor(4);

    // Force source mode.
    wrapper.find('button.ftl').simulate('click');

    const input = wrapper.find('GenericTranslationForm textarea');
    expect(input).toHaveLength(1);
    expect(input.prop('value')).toBe('my-message = { "" }\n');
  });

  it('changes editor implementation when changing translation syntax', () => {
    const [wrapper] = mountEditor(1);

    // Force source mode.
    wrapper.find('button.ftl').simulate('click');

    const input = wrapper.find('GenericTranslationForm textarea');
    act(() =>
      input.prop('onChange')({ currentTarget: { value: RICH_MESSAGE_STRING } }),
    );
    wrapper.update();

    // Switch to rich mode.
    wrapper.find('button.ftl').simulate('click');

    expect(wrapper.find('RichTranslationForm textarea')).toHaveLength(2);
  });

  it('updates content that comes from an external source', () => {
    const [wrapper, actions] = mountEditor(1);

    // Update the content with a Fluent string.
    act(() => actions.setEditorFromHistory('my-message = Coucou'));
    wrapper.update();

    // The translation has been updated to a simplified preview.
    expect(wrapper.find('textarea').text()).toEqual('Coucou');
  });

  it('passes a reconstructed translation to sendTranslation', async () => {
    sinon.stub(TranslationAPI, 'createTranslation').returns({});

    const [wrapper, actions] = mountEditor(1);

    // Update the content with new input
    act(() => actions.setEditorFromInput('Coucou'));
    wrapper.update();
    await act(() => wrapper.find('.action-suggest').prop('onClick')());

    const { args } = TranslationAPI.createTranslation.getCalls()[0];
    expect(args[1]).toBe('my-message = Coucou\n');
  });
});
