import ftl from '@fluent/dedent';
import { mount } from 'enzyme';
import { createMemoryHistory } from 'history';
import React, { useContext } from 'react';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';
import sinon from 'sinon';

import * as TranslationAPI from '~/api/translation';
import { EditorActions, EditorProvider } from '~/context/Editor';
import { EntityViewProvider } from '~/context/EntityView';
import { LocationProvider } from '~/context/Location';
import { RECEIVE_ENTITIES } from '~/modules/entities/actions';
import { EditField } from '~/modules/translationform/components/EditField';

import { createDefaultUser, createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { Editor } from './Editor';
import { vi } from 'vitest';

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

const BROKEN_STRING = `my-message = Why so {} serious?\n`;

const ENTITIES = [
  {
    pk: 1,
    format: 'fluent',
    key: ['my-message'],
    original: 'my-message = Hello',
    translation: { string: 'my-message = Salut' },
  },
  {
    pk: 2,
    format: 'fluent',
    key: ['my-message'],
    original: 'my-message =\n    .my-attr = Something guud',
    translation: {
      string: 'my-message =\n    .my-attr = Quelque chose de bien',
    },
  },
  {
    pk: 3,
    format: 'fluent',
    key: ['my-message'],
    original: RICH_MESSAGE_STRING,
    translation: undefined,
  },
  {
    pk: 4,
    format: 'fluent',
    key: ['my-message'],
    original: 'my-message = Hello',
    translation: { string: '' },
  },
  {
    pk: 5,
    format: 'fluent',
    key: ['my-message'],
    original: NESTED_SELECTORS_STRING,
    translation: { string: NESTED_SELECTORS_STRING },
  },
  {
    pk: 6,
    format: 'fluent',
    key: ['my-message'],
    original: BROKEN_STRING,
    translation: { string: BROKEN_STRING },
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
          <EntityViewProvider>
            <EditorProvider>
              <Spy />
              <Editor />
            </EditorProvider>
          </EntityViewProvider>
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

    const input = wrapper.find(EditField);
    expect(input).toHaveLength(1);
    expect(input.prop('defaultValue')).toBe('Salut');
  });

  it('renders the simple form when passing a simple string with one attribute', () => {
    const [wrapper] = mountEditor(2);

    const input = wrapper.find(EditField);
    expect(input).toHaveLength(1);
    expect(input.prop('defaultValue')).toBe('Quelque chose de bien');
  });

  it('renders the rich form when passing a supported rich message', () => {
    const [wrapper] = mountEditor(3);

    expect(wrapper.find(EditField)).toHaveLength(2);
  });

  it('renders the rich form when passing a message with nested selector', () => {
    const [wrapper] = mountEditor(5);

    expect(wrapper.find(EditField)).toHaveLength(4);
  });

  it('renders the source form when passing a broken string', () => {
    const [wrapper] = mountEditor(6);

    const input = wrapper.find(EditField);
    expect(input).toHaveLength(1);
    expect(input.prop('defaultValue')).toBe(BROKEN_STRING.trim());
  });

  it('converts translation when switching source mode', () => {
    const [wrapper] = mountEditor(1);

    // Force source mode.
    wrapper.find('button.ftl').simulate('click');

    const input = wrapper.find(EditField);
    expect(input).toHaveLength(1);
    expect(input.prop('defaultValue')).toBe('my-message = Salut');
  });

  it('sets empty initial translation in source mode when untranslated', () => {
    const [wrapper] = mountEditor(4);

    // Force source mode.
    wrapper.find('button.ftl').simulate('click');

    const input = wrapper.find(EditField);
    expect(input).toHaveLength(1);
    expect(input.prop('defaultValue')).toBe('my-message = { "" }');
  });

  it('changes editor implementation when changing translation syntax', () => {
    const [wrapper, actions] = mountEditor(1);

    // Force source mode.
    wrapper.find('button.ftl').simulate('click');

    act(() => actions.setEditorFromHistory(RICH_MESSAGE_STRING));
    wrapper.update();

    // Switch to rich mode.
    wrapper.find('button.ftl').simulate('click');

    expect(wrapper.find(EditField)).toHaveLength(2);
  });

  it('updates content that comes from an external source', () => {
    const [wrapper, actions] = mountEditor(1);

    // Update the content with a Fluent string.
    act(() => actions.setEditorFromHistory('my-message = Coucou'));
    wrapper.update();

    // The translation has been updated to a simplified preview.
    expect(wrapper.find(EditField).text()).toEqual('Coucou');
  });

  it('passes a reconstructed translation to sendTranslation', async () => {
    const createSpy = vi
      .spyOn(TranslationAPI, 'createTranslation')
      .mockReturnValue({});

    const [wrapper, actions] = mountEditor(1);

    // Update the content with new input
    act(() => actions.setResultFromInput(0, 'Coucou'));
    wrapper.update();
    await act(() => wrapper.find('.action-suggest').prop('onClick')());

    expect(createSpy.mock.calls.length).toBe(1);
    const args = createSpy.mock.calls[0];
    expect(args[1]).toBe('my-message = Coucou\n');
  });
});
