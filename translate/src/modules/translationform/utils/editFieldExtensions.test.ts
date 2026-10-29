import { EditorView } from '@codemirror/view';
import { EditorState } from '@codemirror/state';

import { getExtensions } from './editFieldExtensions';
import { parseEntry } from '~/utils/message';

const div = document.createElement('div');
document.body.appendChild(div);

let currentTempView: EditorView | null = null;

// Create a hidden view with the given document and extensions that
// lives until the next call to `tempView`.
// From: https://github.com/codemirror/view/blob/main/test/tempview.ts
function tempView(format: string, doc = ''): EditorView {
  if (currentTempView) {
    currentTempView.destroy();
    currentTempView = null;
  }

  const entry = parseEntry(format, `key = ${doc}`)!;
  const extensions = getExtensions(entry, {} as any);
  currentTempView = new EditorView({
    state: EditorState.create({ doc, extensions }),
  });
  div.appendChild(currentTempView.dom);
  return currentTempView;
}

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

describe('quoted literal direction', () => {
  // Returns the bidi level of each text span, in visual order
  function bidiLevels(view: EditorView) {
    const doc = view.state.doc.toString();
    return view
      .bidiSpans(view.state.doc.line(1))
      .map((span) => [doc.slice(span.from, span.to), span.level]);
  }

  test('RTL literal starting with a placeholder', () => {
    const view = tempView('fluent', '<a title="{ $name } سلام">متن</a>');

    const literal = getAncestorWith(view.domAtPos(21).node, 'dir');
    expect(literal?.textContent).toBe('{ $name } سلام');
    expect(literal?.getAttribute('dir')).toBe('rtl');

    expect(bidiLevels(view)).toEqual([
      ['<a title="', 0],
      [' سلام', 1],
      ['{ $name }', 2],
      ['">', 0],
      ['متن', 1],
      ['</a>', 0],
    ]);
  });

  test('LTR literal with RTL text after a placeholder', () => {
    const view = tempView('fluent', '<a title="{ $name } hello سلام">x</a>');

    const literal = getAncestorWith(view.domAtPos(21).node, 'dir');
    expect(literal?.getAttribute('dir')).toBe('ltr');
  });

  test('literal without strong characters', () => {
    const view = tempView('fluent', '<a title="{ $name } 123">x</a>');

    const literal = getAncestorWith(view.domAtPos(21).node, 'dir');
    expect(literal?.getAttribute('dir')).toBe('ltr');
  });
});

describe('quoted literal direction while editing', () => {
  const literalDir = (view: EditorView) =>
    getAncestorWith(view.domAtPos(11).node, 'dir')?.getAttribute('dir');

  test('does not flip when typing text in the other direction', () => {
    const view = tempView('fluent', '<a title="سلام">x</a>');
    expect(literalDir(view)).toBe('rtl');

    // '<a title="' is 10 characters, so the literal starts at 10.
    // On its own, the new content would be shown LTR.
    view.dispatch({ changes: { from: 10, insert: 'Firefox ' } });
    expect(view.state.doc.toString()).toBe('<a title="Firefox سلام">x</a>');
    expect(literalDir(view)).toBe('rtl');
  });

  test('is detected again for new content', () => {
    const view = tempView('fluent', '<a title="سلام">x</a>');
    view.dispatch({
      changes: {
        from: 0,
        to: view.state.doc.length,
        insert: '<a title="Firefox سلام">x</a>',
      },
    });
    expect(literalDir(view)).toBe('ltr');
  });
});
