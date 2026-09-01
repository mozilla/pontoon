import { EditorView } from '@codemirror/view';
import ftl from '@fluent/dedent';
import { fluentParseEntry } from '@mozilla/l10n';
import { fireEvent } from '@testing-library/react';
import { useContext, useState } from 'react';
import { act } from 'react-dom/test-utils';
import { beforeAll, describe, expect, it, vi } from 'vitest';

import { EditorActions, EditorProvider, EditorResult } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';

import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { TranslationForm } from './TranslationForm';

const DEFAULT_LOCALE = {
  direction: 'ltr',
  code: 'kg',
  script: 'Latn',
  cldrPlurals: [1, 5],
};

function mountForm(source, target = null, locale = DEFAULT_LOCALE) {
  target ??= source;
  const store = createReduxStore();
  createDefaultUser(store);

  const [id, sourceEntry] = fluentParseEntry(source);
  const [, targetEntry] = fluentParseEntry(target);
  const entity = {
    pk: 1,
    format: 'fluent',
    key: [id],
    original: source,
    value: sourceEntry['='] ?? [],
    properties: sourceEntry['+'],
    translation: {
      string: target,
      value: targetEntry['='] ?? [],
      properties: targetEntry['+'],
    },
  };

  let actions, result, setCurrentEntity;
  const Spy = () => {
    actions = useContext(EditorActions);
    result = useContext(EditorResult);
    return null;
  };

  const wrapper = mountComponentWithStore(() => {
    const [currentEntity, updateCurrentEntity] = useState(entity);
    setCurrentEntity = updateCurrentEntity;
    return (
      <Locale.Provider value={locale}>
        <MockLocalizationProvider>
          <EntityView.Provider value={{ entity: currentEntity }}>
            <EditorProvider>
              <Spy />
              <TranslationForm />
            </EditorProvider>
          </EntityView.Provider>
        </MockLocalizationProvider>
      </Locale.Provider>
    );
  }, store);
  vi.runAllTimers();

  // TODO:Replace the querySelector with testing-library-ish approaches
  const form = wrapper.container.querySelector('.translationform');
  const views = Array.from(form.querySelectorAll('.cm-content')).map((el) =>
    EditorView.findFromDOM(el),
  );

  return { actions, getResult: () => result, setCurrentEntity, views, wrapper };
}

describe('<TranslationForm> with multiple fields', () => {
  beforeAll(() => {
    vi.useFakeTimers();
  });

  it('renders textarea for a value and each attribute', () => {
    const { views } = mountForm(ftl`
      message = Value
        .attr-1 = And
        .attr-2 = Attributes
      `);

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Value',
      'And',
      'Attributes',
    ]);
  });

  it('renders select expression properly', () => {
    const {
      views,
      wrapper: { container },
    } = mountForm(ftl`
      my-entry =
        { PLATFORM() ->
            [variant] Hello!
           *[another-variant] World!
        }
      `);

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Hello!',
      'World!',
    ]);
    const labels = container.querySelectorAll('label');
    expect(labels[0]).toHaveTextContent('variant');
    expect(labels[1]).toHaveTextContent('another-variant');
  });

  it('renders select expression in attributes properly', () => {
    const {
      views,
      wrapper: { container },
    } = mountForm(ftl`
      my-entry =
        .label =
            { PLATFORM() ->
                [macosx] Preferences
               *[other] Options
            }
        .accesskey =
            { PLATFORM() ->
                [macosx] e
               *[other] s
            }
      `);

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Preferences',
      'Options',
    ]);
    expect(container.querySelectorAll('input')).toHaveLength(2);

    const labels = Array.from(container.querySelectorAll('label'), (l) =>
      Array.from(l.querySelectorAll('span'), (span) => span.textContent),
    );
    expect(labels).toEqual([
      ['label', 'macosx'],
      ['label', 'other'],
      ['accesskey', 'macosx'],
      ['accesskey', 'other'],
    ]);

    expect(container.querySelectorAll('input')[0]).toHaveValue('e');
    expect(container.querySelectorAll('input')[1]).toHaveValue('s');
  });

  it('renders plural string properly', () => {
    const {
      views,
      wrapper: { container },
    } = mountForm(ftl`
      my-entry =
        { $num ->
            [one] Hello!
           *[other] World!
        }
      `);
    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Hello!',
      'World!',
    ]);

    const labels = Array.from(container.querySelectorAll('label'), (l) =>
      Array.from(l.querySelectorAll('span'), (span) => span.textContent),
    );
    expect(labels).toEqual([
      [expect.stringMatching(/^one/), '1'],
      [expect.stringMatching(/^other/), '2'],
    ]);
  });

  it('renders plural string in attributes properly', () => {
    const {
      views,
      wrapper: { container },
    } = mountForm(ftl`
      my-entry =
        .label =
            { $num ->
                [one] Hello!
               *[other] World!
            }
        .attr = Foo
      `);

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Hello!',
      'World!',
      'Foo',
    ]);

    const labels = Array.from(container.querySelectorAll('label'), (l) =>
      Array.from(l.querySelectorAll('span'), (span) => span.textContent),
    );
    expect(labels).toEqual([
      ['label', expect.stringMatching(/^one/), '1'],
      ['label', expect.stringMatching(/^other/), '2'],
      ['attr'],
    ]);
  });

  it('renders translation-only attributes in proper order', () => {
    const {
      views,
      wrapper: { container },
    } = mountForm(
      ftl`
      key =
        .a = Foo
        .b = Bar
      `,
      ftl`
      key =
        .c = Baz
        .a = Foo
      `,
    );

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Foo',
      '',
      'Baz',
    ]);

    const labels = Array.from(container.querySelectorAll('label'), (l) =>
      Array.from(l.querySelectorAll('span'), (span) => span.textContent),
    );
    expect(labels).toEqual([['a'], ['b'], ['c']]);
  });

  it('renders empty value even if missing from translation', () => {
    const {
      views,
      wrapper: { container },
    } = mountForm(
      ftl`
      key = Val
        .a = Foo
      `,
      ftl`
      key =
        .a = Bar
      `,
    );

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      '',
      'Bar',
    ]);

    const labels = Array.from(container.querySelectorAll('label'), (l) =>
      Array.from(l.querySelectorAll('span'), (span) => span.textContent),
    );
    expect(labels).toEqual([['Value'], ['a']]);
  });

  it('leaves out value if missing from source', () => {
    const {
      views,
      wrapper: { container },
    } = mountForm(
      ftl`
      key =
        .a = Foo
      `,
      ftl`
      key = Val
        .a = Bar
        .b = Baz
      `,
    );

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Bar',
      'Baz',
    ]);

    const labels = Array.from(container.querySelectorAll('label'), (l) =>
      Array.from(l.querySelectorAll('span'), (span) => span.textContent),
    );
    expect(labels).toEqual([['a'], ['b']]);
  });

  it('renders access keys properly', () => {
    const {
      getResult,
      views,
      wrapper: { container },
    } = mountForm(ftl`
      title = Title
        .label = Candidates
        .accesskey = C
      `);

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Title',
      'Candidates',
    ]);

    expect(container.querySelectorAll('label')[1]).toHaveTextContent('label');
    expect(container.querySelectorAll('label')[2]).toHaveTextContent(
      'accesskey',
    );

    const input = container.querySelectorAll('input');
    expect(input).toHaveLength(1);
    expect(input[0]).toHaveValue('C');
    expect(input[0]).toHaveAttribute('maxLength', '1');

    expect(container.querySelectorAll('.accesskeys')).toHaveLength(1);
    const buttons = container.querySelectorAll('.accesskeys button');
    const buttonTexts = Array.from(buttons, (button) => button.textContent);
    expect(buttonTexts).toMatchObject(['C', 'a', 'n', 'd', 'i', 't', 'e', 's']);

    fireEvent.click(buttons[1]);
    vi.runAllTimers();

    expect(getResult().attributes).toEqual(
      new Map([
        ['label', ['Candidates']],
        ['accesskey', ['a']],
      ]),
    );
  });

  it('does not render accesskey buttons if no candidates can be generated', () => {
    const {
      wrapper: { container },
    } = mountForm(ftl`
      title =
        .label = { reference }
        .accesskey = C
      `);

    expect(container.querySelectorAll('.accesskeys button')).toHaveLength(0);
  });

  it('does not render the access key UI if access key is longer than 1 character', () => {
    const {
      wrapper: { container },
    } = mountForm(ftl`
      title =
        .label = Candidates
        .accesskey = { reference }
      `);

    expect(container.querySelectorAll('.accesskeys')).toHaveLength(0);
  });

  it('updates the translation when setEditorSelection is passed', async () => {
    const { actions, getResult } = mountForm(ftl`
      title = Value
        .label = Something
      `);
    act(() => actions.setEditorSelection('Add'));

    const result = getResult();
    expect(result).toMatchObject({
      format: 'fluent',
      id: 'title',
      value: ['ValueAdd'],
      attributes: new Map([['label', ['Something']]]),
    });
  });

  it('re-applies a history entry after a field was edited', () => {
    const { actions, views } = mountForm(ftl`
      title = Value
        .label = Something
      `);

    const restore = () =>
      act(() =>
        actions.setEditorFromHistory('title = RESTORED\n    .label = LABEL\n'),
      );
    const docs = () => views.map((view) => view.state.doc.toString());

    restore();
    expect(docs()).toEqual(['RESTORED', 'LABEL']);

    act(() =>
      views[0].dispatch({
        changes: { from: 0, to: views[0].state.doc.length, insert: 'EDITED' },
      }),
    );

    restore();
    expect(docs()).toEqual(['RESTORED', 'LABEL']);
  });

  it('re-applies a composed suggestion after a field was edited', () => {
    const { actions, views } = mountForm(ftl`
      title = Value
        .label = Something
      `);

    const applyComposed = () =>
      act(() =>
        actions.setEditorFromComposed(
          ['COMPOSED'],
          { label: ['COMPOSED_LABEL'] },
          ['translation-memory'],
          true,
        ),
      );
    const docs = () => views.map((view) => view.state.doc.toString());

    applyComposed();
    expect(docs()).toEqual(['COMPOSED', 'COMPOSED_LABEL']);

    act(() =>
      views[0].dispatch({
        changes: { from: 0, to: views[0].state.doc.length, insert: 'EDITED' },
      }),
    );
    expect(docs()).toEqual(['EDITED', 'COMPOSED_LABEL']);

    // Same suggestion, same values: the edited field must still be reset.
    applyComposed();
    expect(docs()).toEqual(['COMPOSED', 'COMPOSED_LABEL']);
  });

  it('inserts a placeable into the focused field after a rejection', () => {
    const source = ftl`
      key =
          { $num ->
              [one] ONE
             *[other] OTHER
          }
      `;
    const { actions, getResult, setCurrentEntity, views } = mountForm(source);

    act(() =>
      setCurrentEntity((entity) => ({
        ...entity,
        translation: { ...entity.translation, status: 'rejected' },
      })),
    );
    vi.runAllTimers();

    act(() => views[1].contentDOM.focus());
    vi.runAllTimers();

    act(() => actions.setEditorSelection('{ $num }'));

    expect(views.map((view) => view.state.doc.toString())).toEqual([
      '',
      '{ $num }',
    ]);
    expect(getResult().value.alt).toMatchObject([
      { keys: ['one'], pat: [] },
      { keys: [{ '*': 'other' }], pat: [{ $: 'num' }] },
    ]);
  });

  it('copies a translation naming its catchall after the source, on one click', () => {
    const source = ftl`
      key =
          { $count ->
              [one] ONE
             *[other] OTHER
          }
      `;
    const inLocale = ftl`
      key =
          { $count ->
              [one] ОДИН
              [few] КІЛЬКА
             *[many] БАГАТО
          }
      `;
    const fromSource = ftl`
      key =
          { $count ->
              [one] ОДИН2
              [few] КІЛЬКА2
             *[other] БАГАТО2
          }
      `;
    const { actions, views, wrapper } = mountForm(source, inLocale, {
      direction: 'ltr',
      code: 'uk',
      script: 'Cyrl',
      cldrPlurals: [1, 3, 4],
    });
    const labels = () =>
      Array.from(
        wrapper.container.querySelectorAll('.translationform label'),
      ).map((el) => el.textContent.trim());
    const docs = () => views.map((view) => view.state.doc.toString());

    expect(labels()).toEqual(['one', 'few', 'many']);

    act(() => actions.setEditorFromHistory(fromSource));

    expect(docs()).toEqual(['ОДИН2', 'КІЛЬКА2', 'БАГАТО2']);
    expect(labels()).toEqual(['one', 'few', 'other']);

    act(() => actions.setEditorFromHistory(inLocale));

    expect(docs()).toEqual(['ОДИН', 'КІЛЬКА', 'БАГАТО']);
    expect(labels()).toEqual(['one', 'few', 'many']);
  });
});
