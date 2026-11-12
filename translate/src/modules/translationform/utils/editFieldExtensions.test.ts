import { currentCompletions, startCompletion } from '@codemirror/autocomplete';
import { EditorView } from '@codemirror/view';
import { EditorState, type Extension } from '@codemirror/state';

import { getExtensions } from './editFieldExtensions';
import { parseEntry } from '~/utils/message';

import type { FluentTerms } from '~/api/fluentTerms';
import { fluentLanguageMode } from './editFieldModes';
import { fluentTermVariantsCompletion } from './fluentTermVariantsCompletion';

const div = document.createElement('div');
document.body.appendChild(div);

let currentTempView: EditorView | null = null;

// Create a hidden view with the given document and extensions that
// lives until the next call to `tempView`.
// From: https://github.com/codemirror/view/blob/main/test/tempview.ts
function tempView(format: string, doc = '', extra: Extension = []): EditorView {
  if (currentTempView) {
    currentTempView.destroy();
    currentTempView = null;
  }

  // Docs with unbalanced syntax (e.g. an unclosed `{`) cannot be parsed;
  // fall back to a minimal valid entry, as only the format is needed then.
  const entry =
    parseEntry(format, `key = ${doc}`) ?? parseEntry(format, 'key = x')!;
  const extensions = getExtensions(entry, {} as any, doc);
  currentTempView = new EditorView({
    state: EditorState.create({ doc, extensions: [extensions, extra] }),
  });
  div.appendChild(currentTempView.dom);
  return currentTempView;
}

describe('term variants autocomplete', () => {
  const terms: FluentTerms = {
    '-brand-name': {
      value: {
        decl: {},
        sel: ['case'],
        alt: [
          { keys: [{ '*': 'nominative' }], pat: ['Brand'] },
          { keys: ['accusative'], pat: ['the Brand'] },
        ],
      },
      properties: null,
      translation_value: null,
      translation_properties: null,
    },
  };

  async function completeInto(doc: string, insert: string) {
    const view = tempView('fluent', doc, [
      fluentLanguageMode.data.of({
        autocomplete: fluentTermVariantsCompletion(async () => terms),
      }),
    ]);

    view.dispatch({
      changes: { from: doc.length, insert },
      selection: { anchor: doc.length + insert.length },
    });
    startCompletion(view);

    await vi.waitFor(() => {
      expect(currentCompletions(view.state).length).toBeGreaterThan(0);
    });
    return { view, options: currentCompletions(view.state) };
  }

  it('offers term variants with the default variant last', async () => {
    const { options } = await completeInto('foo ', '{ -brand-name(');

    expect(options.map((option) => option.label)).toEqual([
      'case: "accusative"',
      'case: "nominative"',
    ]);
  });

  it('keeps the default variant visible when filtering', async () => {
    const { options } = await completeInto('foo ', '{ -brand-name(no');

    expect(options.map((option) => option.label)).toContain(
      'case: "nominative"',
    );
  });

  it.skip('closes brackets', async () => {
    const { view } = await completeInto('foo ', '{ -brand-name(');

    expect(view.state.doc.toString()).toBe('foo { -brand-name()');
  });

  it('offers term variants in a message with placeholders', async () => {
    const { options } = await completeInto('foo { $bar } ', '{ -brand-name(');

    expect(options.map((option) => option.label)).toEqual(
      expect.arrayContaining(['case: "nominative"', 'case: "accusative"']),
    );
  });
});

function getAncestorWith(node: Node | null, attribute: string) {
  let el = node instanceof HTMLElement ? node : node?.parentElement;
  while (el && !el.hasAttribute(attribute)) {
    el = el.parentElement;
  }
  return el;
}

describe('spellcheck', () => {
  test('fluent mode', () => {
    const view = tempView('fluent', 'foo { $bar }');

    const text = getAncestorWith(view.domAtPos(1).node, 'spellcheck');
    expect(text?.getAttribute('spellcheck')).toBe('true');

    const ph = getAncestorWith(view.domAtPos(8).node, 'spellcheck');
    expect(ph?.getAttribute('spellcheck')).toBe('false');
  });

  test('common mode', () => {
    const view = tempView('android', '%1$s foo');

    const text = getAncestorWith(view.domAtPos(7).node, 'spellcheck');
    expect(text?.getAttribute('spellcheck')).toBe('true');

    const ph = getAncestorWith(view.domAtPos(1).node, 'spellcheck');
    expect(ph?.getAttribute('spellcheck')).toBe('false');
  });
});

describe('keyword', () => {
  describe('common mode', () => {
    test('i18next format', () => {
      const view1 = tempView('plain', '{{name}} foo');
      const nameEl = getAncestorWith(view1.domAtPos(1).node, 'dir');
      expect(nameEl?.textContent).toBe('{{name}}');

      const view2 = tempView('plain', '{{balance, money}} foo');
      const balanceEl = getAncestorWith(view2.domAtPos(1).node, 'dir');
      expect(balanceEl?.textContent).toBe('{{balance, money}}');

      const view3 = tempView(
        'plain',
        '{{num, number(minimumFractionDigits: 2)}} foo',
      );
      const numEl = getAncestorWith(view3.domAtPos(1).node, 'dir');
      expect(numEl?.textContent).toBe(
        '{{num, number(minimumFractionDigits: 2)}}',
      );

      const view4 = tempView('plain', '{{value, formatter1, formatter2}} foo');
      const valueEl = getAncestorWith(view4.domAtPos(1).node, 'dir');
      expect(valueEl?.textContent).toBe('{{value, formatter1, formatter2}}');
    });
  });
});
