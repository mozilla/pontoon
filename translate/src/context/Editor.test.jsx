import ftl from '@fluent/dedent';
import { createMemoryHistory } from 'history';
import React, { useContext } from 'react';
import { act } from 'react-dom/test-utils';
import { describe, expect, it } from 'vitest';

import { createReduxStore, mountComponentWithStore } from '~/test/store';
import { editMessageEntry, parseEntry } from '~/utils/message';

import {
  EditorActions,
  EditorData,
  EditorProvider,
  EditorResult,
} from './Editor';
import { EntityView, EntityViewProvider } from './EntityView';
import { Locale } from './Locale';
import { Location, LocationProvider } from './Location';
import { UnsavedChanges, UnsavedChangesProvider } from './UnsavedChanges';
import { fluentParseEntry, mf2ParseMessage } from '@mozilla/l10n';

function mountSpy(Spy, format, formatTranslation, formatSource = 'key = test') {
  const history = createMemoryHistory({
    initialEntries: [`/sl/pro/all/?string=42`],
  });

  let key = ['key'];
  let value, properties;
  let translation = undefined;
  switch (format) {
    case 'fluent': {
      const [id, entry] = fluentParseEntry(formatSource);
      key = [id];
      value = entry['='];
      properties = entry['+'];
      if (formatTranslation) {
        const [, entry] = fluentParseEntry(formatTranslation);
        translation = {
          string: formatTranslation,
          value: entry['='],
          properties: entry['+'],
        };
      }
      break;
    }
    case 'android':
      value = mf2ParseMessage(formatSource);
      if (formatTranslation) {
        translation = {
          string: formatTranslation,
          value: mf2ParseMessage(formatTranslation),
        };
      }
      break;
    default:
      value = [formatSource];
      if (formatTranslation) {
        translation = { string: formatTranslation, value: [formatTranslation] };
      }
  }

  const gettextSource =
    '.input {$n :number}\n.match $n\none {{orig one}}\n* {{orig other}}';
  const gettextTranslation =
    '.input {$n :number}\n.match $n\none {{trans one}}\n* {{trans other}}';

  const initialState = {
    entities: {
      entities: [
        {
          pk: 42,
          format,
          key,
          original: formatSource,
          value,
          properties,
          translation,
          project: { contact: '' },
        },
        {
          pk: 13,
          format: 'gettext',
          key: ['plural'],
          original: gettextSource,
          value: mf2ParseMessage(gettextSource),
          translation: {
            string: gettextTranslation,
            value: mf2ParseMessage(gettextTranslation),
          },
          project: { contact: '' },
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
          <UnsavedChangesProvider>
            <EditorProvider>
              <Spy />
            </EditorProvider>
          </UnsavedChangesProvider>
        </EntityViewProvider>
      </Locale.Provider>
    </LocationProvider>
  );
  return mountComponentWithStore(Wrapper, store, {}, history);
}

describe('<EditorProvider>', () => {
  it('provides a simple non-Fluent value', () => {
    let editor, result;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
      return null;
    };
    mountSpy(Spy, 'simple', 'message');
    expect(editor).toMatchObject({
      sourceView: false,
      initial: { id: 'key', value: ['message'] },
      fields: [
        {
          id: '',
          keys: [],
          labels: [],
          name: '',
          handle: { current: { value: 'message' } },
        },
      ],
    });
    expect(result).toEqual({ format: 'plain', id: 'key', value: ['message'] });
  });

  it('provides a simple Fluent value', () => {
    let editor, result;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
      return null;
    };
    mountSpy(Spy, 'fluent', 'key = message');
    expect(editor).toMatchObject({
      sourceView: false,
      initial: { id: 'key', value: ['message'] },
      fields: [
        {
          id: '',
          keys: [],
          labels: [],
          name: '',
          handle: { current: { value: 'message' } },
        },
      ],
    });
    expect(result).toEqual({
      format: 'fluent',
      id: 'key',
      value: ['message'],
    });
  });

  it('provides a rich Fluent value', () => {
    let editor, result;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
      return null;
    };
    const source = ftl`
      key =
          { $var ->
              [one] ONE
             *[other] OTHER
          }

      `;
    mountSpy(Spy, 'fluent', source);

    const entry = parseEntry('fluent', source);
    const fields = editMessageEntry(entry).map((field) => ({
      ...field,
      handle: { current: { value: field.handle.current.value } },
    }));
    expect(editor).toMatchObject({ sourceView: false, initial: entry, fields });
    expect(result).toEqual({
      format: 'fluent',
      id: 'key',
      value: {
        decl: { var: { $: 'var', fn: 'number' } },
        sel: ['var'],
        alt: [
          { keys: ['one'], pat: ['ONE'] },
          { keys: [{ '*': 'other' }], pat: ['OTHER'] },
        ],
      },
    });
  });

  it('provides a forced source Fluent value', () => {
    let editor, result;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
      return null;
    };
    const source = ftl`
      key =
          { $var ->
              [a] A
              [b] B
              [c] C
              [d] D
              [e] E
              [f] F
              [g] G
              [h] H
              [i] I
              [j] J
              [k] K
              [l] L
              [m] M
              [n] N
              [o] O
              [p] P
             *[q] Q
          }
      `;
    mountSpy(Spy, 'fluent', source, source);

    expect(editor).toMatchObject({
      sourceView: true,
      fields: [
        {
          handle: { current: { value: source } },
          id: '',
          keys: [],
          labels: [],
          name: '',
        },
      ],
    });
    expect(result).toEqual({
      format: 'fluent',
      id: 'key',
      value: fluentParseEntry(source)[1]['='],
    });
  });

  it('provides a multiline properties value with CRLF terminators', () => {
    let editor, result;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
      return null;
    };
    mountSpy(Spy, 'properties', 'föö\r\nbär\r\n', 'foo\r\nbar\r\n');
    expect(editor).toMatchObject({
      sourceView: false,
      initial: { id: 'key', value: ['föö\r\nbär\r\n'] },
      fields: [
        {
          id: '',
          keys: [],
          labels: [],
          name: '',
          handle: { current: { value: 'föö\\r\nbär\\r\n' } },
        },
      ],
    });
    expect(result).toEqual({
      format: 'properties',
      id: 'key',
      value: ['föö\r\nbär\r\n'],
    });
  });

  it('provides a simple Android value with no translation', () => {
    let editor, result;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
      return null;
    };
    mountSpy(
      Spy,
      'android',
      undefined,
      'Hello, {$arg1 :string @source=|%1$s|}!',
    );
    expect(editor).toMatchObject({
      sourceView: false,
      initial: { id: 'key', value: [] },
      fields: [
        {
          id: '',
          keys: [],
          labels: [],
          name: '',
          handle: { current: { value: '' } },
        },
      ],
    });
    expect(result).toEqual({ format: 'android', id: 'key', value: [] });
  });

  it('provides a simple Android value', () => {
    let editor, result;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
      return null;
    };
    mountSpy(
      Spy,
      'android',
      'Hei, {$arg1 :string @source=|%1$s|}!',
      'Hello, {$arg1 :string @source=|%1$s|}!',
    );
    const arg1 = { $: 'arg1', fn: 'string', attr: { source: '%1$s' } };
    expect(editor).toMatchObject({
      sourceView: false,
      initial: { id: 'key', value: ['Hei, ', arg1, '!'] },
      fields: [
        {
          id: '',
          keys: [],
          labels: [],
          name: '',
          handle: { current: { value: 'Hei, %1$s!' } },
        },
      ],
    });
    expect(result).toEqual({
      format: 'android',
      id: 'key',
      value: [
        'Hei, ',
        { $: 'arg1', fn: 'string', opt: undefined, attr: { source: '%1$s' } },
        '!',
      ],
    });
  });

  it('provides a rich Android value', () => {
    let editor, result;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
      return null;
    };
    const trans = ftl`
      .input {$quantity :number}
      .match $quantity
      one {{trans:ONE}}
      * {{trans:OTHER}}
      `;
    const source = ftl`
      .input {$quantity :number}
      .match $quantity
      one {{src:ONE}}
      * {{src:OTHER}}
      `;
    mountSpy(Spy, 'android', trans, source);

    const entry = parseEntry('android', trans);
    const fields = editMessageEntry(entry).map((field) => ({
      ...field,
      handle: { current: { value: field.handle.current.value } },
    }));
    expect(editor).toMatchObject({
      sourceView: false,
      initial: { ...entry, id: 'key' },
      fields,
    });
    expect(result).toEqual({
      format: 'android',
      id: 'key',
      value: {
        decl: {
          quantity: {
            $: 'quantity',
            fn: 'number',
            opt: undefined,
            attr: undefined,
          },
        },
        sel: ['quantity'],
        alt: [
          { keys: ['one'], pat: ['trans:ONE'] },
          { keys: [{ '*': '' }], pat: ['trans:OTHER'] },
        ],
      },
    });
  });

  it('provides an Android value with HTML', () => {
    let actions, result;
    const Spy = () => {
      actions = useContext(EditorActions);
      result = useContext(EditorResult);
      return null;
    };
    const trans = 'Tämä on <b>lihavoitu</b>.';
    mountSpy(Spy, 'android', trans, 'This is {|<b>| :html}bold{|</b>| :html}.');

    // Parse the translation with Android syntax
    act(() => actions.setResultFromInput());

    expect(result).toEqual({
      format: 'android',
      id: 'key',
      value: [
        'Tämä on ',
        { _: '<b>', fn: 'html' },
        'lihavoitu',
        { _: '</b>', fn: 'html' },
        '.',
      ],
    });
  });

  it('provides an Xliff value with HTML', () => {
    let actions, result;
    const Spy = () => {
      actions = useContext(EditorActions);
      result = useContext(EditorResult);
      return null;
    };
    const trans = 'Tämä on <b>lihavoitu</b>.';
    mountSpy(Spy, 'xliff', trans, 'This is <b>bold</b>.');

    // Parse the translation with Xliff syntax
    act(() => actions.setResultFromInput());

    expect(result).toEqual({ format: 'xliff', id: 'key', value: [trans] });
  });

  it('updates state on entity change', () => {
    let editor, result, location, entity;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
      location = useContext(Location);
      entity = useContext(EntityView).entity;
      return null;
    };
    mountSpy(Spy, 'plain', 'translated');

    act(() => location.push({ entity: 13 }));

    expect(editor).toMatchObject({
      initial: {
        ...parseEntry('gettext', entity.translation.string),
        id: 'plural',
      },
      fields: [
        { handle: { current: { value: 'trans one' } } },
        { handle: { current: { value: 'trans other' } } },
      ],
    });
    expect(result).toEqual({
      format: 'gettext',
      id: 'plural',
      value: {
        decl: { n: { $: 'n', attr: undefined, fn: 'number', opt: undefined } },
        sel: ['n'],
        alt: [
          { keys: ['one'], pat: ['trans one'] },
          { keys: [{ '*': '' }], pat: ['trans other'] },
        ],
      },
    });
  });

  it('clears a rich Fluent value', () => {
    let editor, actions;
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
    mountSpy(Spy, 'fluent', source);
    act(() => actions.clearEditor());

    expect(editor).toMatchObject({
      sourceView: false,
      fields: [
        {
          handle: { current: { value: '' } },
          id: '|one',
          keys: ['one'],
          labels: [{ label: 'one', plural: true }],
          name: '',
        },
        {
          handle: { current: { value: '' } },
          id: '|other',
          keys: [{ '*': 'other' }],
          labels: [{ label: 'other', plural: true }],
          name: '',
        },
      ],
    });
  });

  it('clears a rich Android value', () => {
    let editor, actions;
    const Spy = () => {
      editor = useContext(EditorData);
      actions = useContext(EditorActions);
      return null;
    };
    const source = ftl`
      .input {$quantity :number}
      .match $quantity
      one {{ONE}}
      * {{OTHER}}
      `;
    mountSpy(Spy, 'android', source, source);
    act(() => actions.clearEditor());

    expect(editor).toMatchObject({
      sourceView: false,
      fields: [
        {
          handle: { current: { value: '' } },
          id: '|one',
          keys: ['one'],
          labels: [{ label: 'one', plural: true }],
          name: '',
        },
        {
          handle: { current: { value: '' } },
          id: '|*',
          keys: [{ '*': '' }],
          labels: [{ label: 'other', plural: true }],
          name: '',
        },
      ],
    });
  });

  it('sets editor from history', () => {
    let editor, result, actions;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
      actions = useContext(EditorActions);
      return null;
    };
    mountSpy(Spy, 'fluent', `key = VALUE\n`);

    const source = ftl`
      key =
          { $var ->
              [one] ONE
             *[other] OTHER
          }
      `;
    act(() => actions.setEditorFromHistory(source));

    expect(editor).toMatchObject({
      sourceView: false,
      fields: [
        {
          handle: { current: { value: 'ONE' } },
          id: '|one',
          keys: ['one'],
          labels: [{ label: 'one', plural: true }],
          name: '',
        },
        {
          handle: { current: { value: 'OTHER' } },
          id: '|other',
          keys: [{ '*': 'other' }],
          labels: [{ label: 'other', plural: true }],
          name: '',
        },
      ],
    });
    expect(result).toEqual({
      format: 'fluent',
      id: 'key',
      value: {
        decl: { var: { $: 'var', fn: 'number' } },
        sel: ['var'],
        alt: [
          { keys: ['one'], pat: ['ONE'] },
          { keys: [{ '*': 'other' }], pat: ['OTHER'] },
        ],
      },
    });
  });

  it('toggles Fluent source view', () => {
    let editor, result, actions;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
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
    mountSpy(Spy, 'fluent', source);
    act(() => actions.toggleSourceView());

    expect(editor).toMatchObject({
      sourceView: true,
      fields: [
        {
          handle: { current: { value: source } },
          id: '',
          keys: [],
          labels: [],
          name: '',
        },
      ],
    });
    expect(result).toEqual({
      format: 'fluent',
      id: 'key',
      value: {
        decl: { var: { $: 'var', fn: 'number' } },
        sel: ['var'],
        alt: [
          { keys: ['one'], pat: ['ONE'] },
          { keys: [{ '*': 'other' }], pat: ['OTHER'] },
        ],
      },
    });

    act(() => actions.toggleSourceView());

    expect(editor).toMatchObject({ fields: [{}, {}], sourceView: false });
    expect(result).toEqual({
      format: 'fluent',
      id: 'key',
      value: {
        decl: { var: { $: 'var', fn: 'number' } },
        sel: ['var'],
        alt: [
          { keys: ['one'], pat: ['ONE'] },
          { keys: [{ '*': 'other' }], pat: ['OTHER'] },
        ],
      },
    });
  });

  it('reconstructs message after Fluent source view changes', () => {
    let editor, result, actions;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
      actions = useContext(EditorActions);
      return null;
    };
    const source = ftl`
      key = Value
          .a = Attr
          .b = Bttr
      `;
    mountSpy(Spy, 'fluent', source, source);

    act(() => actions.toggleSourceView());
    act(() =>
      editor.fields[0].handle.current.setValue(ftl`
        key =
            .b = Bttr
            .c = Cttr
        `),
    );
    act(() => actions.setResultFromInput());

    expect(result).toEqual({
      format: 'fluent',
      id: 'key',
      value: [],
      attributes: new Map([
        ['a', []],
        ['b', ['Bttr']],
      ]),
    });

    act(() => actions.toggleSourceView());

    expect(editor).toMatchObject({
      fields: [
        { id: '', handle: { current: { value: '' } } },
        { id: 'a', handle: { current: { value: '' } } },
        { id: 'b', handle: { current: { value: 'Bttr' } } },
      ],
      sourceView: false,
    });
  });

  it('reconstructs term after Fluent source view changes', () => {
    let editor, result, actions;
    const Spy = () => {
      editor = useContext(EditorData);
      result = useContext(EditorResult);
      actions = useContext(EditorActions);
      return null;
    };
    const source = ftl`
      -key = Value
          .a = Attr
          .b = Bttr
      `;
    mountSpy(Spy, 'fluent', source, source);

    act(() => actions.toggleSourceView());
    act(() =>
      editor.fields[0].handle.current.setValue(ftl`
        -key = { "" }
            .b = Bttr
            .c = Cttr
        `),
    );
    act(() => actions.setResultFromInput());

    expect(result).toEqual({
      format: 'fluent',
      id: '-key',
      value: [{ _: '' }],
      attributes: new Map([
        ['a', []],
        ['b', ['Bttr']],
        ['c', ['Cttr']],
      ]),
    });

    act(() => actions.toggleSourceView());

    expect(editor).toMatchObject({
      fields: [
        { id: '', handle: { current: { value: '' } } },
        { id: 'a', handle: { current: { value: '' } } },
        { id: 'b', handle: { current: { value: 'Bttr' } } },
        { id: 'c', handle: { current: { value: 'Cttr' } } },
      ],
      sourceView: false,
    });
  });

  it('reports no pending changes for empty android entry', () => {
    let unsaved;
    const Spy = () => {
      unsaved = useContext(UnsavedChanges);
      return null;
    };
    mountSpy(
      Spy,
      'android',
      undefined,
      'Hello, {$arg1 :string @source=|%1$s|}!',
    );
    expect(unsaved.check()).toBe(false);
  });
});
