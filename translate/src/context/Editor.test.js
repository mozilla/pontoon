import ftl from '@fluent/dedent';
import { createMemoryHistory } from 'history';
import React, { useContext } from 'react';
import { act } from 'react-dom/test-utils';

import { createReduxStore, mountComponentWithStore } from '~/test/store';
import { editMessageEntry, parseEntry } from '~/utils/message';

import { EditorActions, EditorData, EditorProvider } from './Editor';
import { EntityView, EntityViewProvider } from './EntityView';
import { Locale } from './Locale';
import { Location, LocationProvider } from './Location';

function mountSpy(Spy, format, translation) {
  const history = createMemoryHistory({
    initialEntries: [`/sl/pro/all/?string=42`],
  });

  const initialState = {
    entities: {
      entities: [
        {
          pk: 42,
          format,
          key: 'key',
          original: 'key = test',
          translation: [{ string: translation, errors: [], warnings: [] }],
          project: { contact: '' },
          comment: '',
        },
        {
          pk: 13,
          format: 'simple',
          key: 'plural',
          original: 'original',
          original_plural: 'original plural',
          translation: [
            { string: 'one', errors: [], warnings: [] },
            { string: 'other', errors: [], warnings: [] },
          ],
          project: { contact: '' },
          comment: '',
        },
      ],
    },
    otherlocales: { translations: [] },
    user: {
      isAuthenticated: true,
      settings: { forceSuggestions: true },
      username: 'Franck',
    },
  };
  const store = createReduxStore(initialState);

  const Wrapper = () => (
    <LocationProvider history={history}>
      <Locale.Provider value={{ code: 'sl', cldrPlurals: [1, 2, 3, 5] }}>
        <EntityViewProvider>
          <EditorProvider>
            <Spy />
          </EditorProvider>
        </EntityViewProvider>
      </Locale.Provider>
    </LocationProvider>
  );
  return mountComponentWithStore(Wrapper, store, {}, history);
}

describe('<EditorProvider>', () => {
  it('provides a simple non-Fluent value', () => {
    let editor;
    const Spy = () => {
      editor = useContext(EditorData);
      return null;
    };
    mountSpy(Spy, 'simple', 'message');
    expect(editor).toMatchObject({
      sourceView: false,
      initial: [{ id: '', keys: [], labels: [], name: '', value: 'message' }],
      value: [{ id: '', keys: [], labels: [], name: '', value: 'message' }],
    });
  });

  it('provides a simple Fluent value', () => {
    let editor;
    const Spy = () => {
      editor = useContext(EditorData);
      return null;
    };
    mountSpy(Spy, 'ftl', 'key = message');
    expect(editor).toMatchObject({
      sourceView: false,
      initial: [{ id: '', keys: [], labels: [], name: '', value: 'message' }],
      value: [{ id: '', keys: [], labels: [], name: '', value: 'message' }],
    });
  });

  it('provides a rich Fluent value', () => {
    let editor;
    const Spy = () => {
      editor = useContext(EditorData);
      return null;
    };
    const source = ftl`
      key =
          { $var ->
              [one] ONE
             *[other] OTHER
          }

      `;
    mountSpy(Spy, 'ftl', source);

    const value = editMessageEntry(parseEntry(source));
    expect(editor).toMatchObject({ sourceView: false, initial: value, value });
  });

  it('provides a forced source Fluent value', () => {
    let editor;
    const Spy = () => {
      editor = useContext(EditorData);
      return null;
    };
    const source = '## comment\n';
    mountSpy(Spy, 'ftl', source);

    expect(editor).toMatchObject({
      sourceView: true,
      initial: [
        { id: '', keys: [], labels: [], name: '', value: '## comment' },
      ],
      value: [{ id: '', keys: [], labels: [], name: '', value: '## comment' }],
    });
  });

  it('updates state on entity and plural form changes', () => {
    let editor;
    let location;
    let entity;
    const Spy = () => {
      editor = useContext(EditorData);
      location = useContext(Location);
      entity = useContext(EntityView);
      return null;
    };
    const wrapper = mountSpy(Spy, 'simple', 'translated');

    act(() => location.push({ entity: 13 }));
    wrapper.update();

    expect(editor).toMatchObject({
      sourceView: false,
      initial: [{ id: '', keys: [], labels: [], name: '', value: 'one' }],
      value: [{ id: '', keys: [], labels: [], name: '', value: 'one' }],
    });

    act(() => entity.setPluralForm(1));
    wrapper.update();

    expect(editor).toMatchObject({
      sourceView: false,
      initial: [{ id: '', keys: [], labels: [], name: '', value: 'other' }],
      value: [{ id: '', keys: [], labels: [], name: '', value: 'other' }],
    });
  });

  it('clears a rich Fluent value', () => {
    let editor;
    let actions;
    const Spy = () => {
      editor = useContext(EditorData);
      actions = useContext(EditorActions);
      return null;
    };
    const source = ftl`
      key =
          { $var ->
              [one] ONE
             *[other] OTHER
          }
      `;
    const wrapper = mountSpy(Spy, 'ftl', source);
    act(() => actions.clearEditor());
    wrapper.update();

    expect(editor).toMatchObject({
      fields: [{ current: null }, { current: null }],
      sourceView: false,
      value: [
        {
          keys: [{ type: 'nmtoken', value: 'one' }],
          labels: [{ label: 'one', plural: true }],
          name: '',
          value: '',
        },
        {
          keys: [{ type: '*', value: 'other' }],
          labels: [{ label: 'other', plural: true }],
          name: '',
          value: '',
        },
      ],
    });
  });

  it('sets editor from history', () => {
    let editor;
    let actions;
    const Spy = () => {
      editor = useContext(EditorData);
      actions = useContext(EditorActions);
      return null;
    };
    const wrapper = mountSpy(Spy, 'ftl', `key = VALUE\n`);

    expect(editor).toMatchObject({
      fields: [{ current: null }],
      sourceView: false,
      value: [{ keys: [], labels: [], name: '', value: 'VALUE' }],
    });

    const source = ftl`
      key =
          { $var ->
              [one] ONE
             *[other] OTHER
          }
      `;
    act(() => actions.setEditorFromHistory(source));
    wrapper.update();

    expect(editor).toMatchObject({
      fields: [{ current: null }, { current: null }],
      sourceView: false,
      value: [
        {
          keys: [{ type: 'nmtoken', value: 'one' }],
          labels: [{ label: 'one', plural: true }],
          name: '',
          value: 'ONE',
        },
        {
          keys: [{ type: '*', value: 'other' }],
          labels: [{ label: 'other', plural: true }],
          name: '',
          value: 'OTHER',
        },
      ],
    });
  });

  it('toggles Fluent source view', () => {
    let editor;
    let actions;
    const Spy = () => {
      editor = useContext(EditorData);
      actions = useContext(EditorActions);
      return null;
    };
    const source = ftl`
      key =
          { $var ->
              [one] ONE
             *[other] OTHER
          }
      `;
    const wrapper = mountSpy(Spy, 'ftl', source);
    act(() => actions.toggleSourceView());
    wrapper.update();

    expect(editor).toMatchObject({
      fields: [{ current: null }],
      sourceView: true,
      value: [{ keys: [], labels: [], name: '', value: source }],
    });

    act(() => actions.toggleSourceView());
    wrapper.update();

    expect(editor).toMatchObject({
      fields: [{ current: null }, { current: null }],
      sourceView: false,
      value: [
        {
          keys: [{ type: 'nmtoken', value: 'one' }],
          labels: [{ label: 'one', plural: true }],
          name: '',
          value: 'ONE',
        },
        {
          keys: [{ type: '*', value: 'other' }],
          labels: [{ label: 'other', plural: true }],
          name: '',
          value: 'OTHER',
        },
      ],
    });
  });
});
