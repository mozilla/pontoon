import { EditorView } from '@codemirror/view';
import { EditorState } from '@codemirror/state';

import { getExtensions } from './editFieldExtensions';

const div = document.createElement('div');
document.body.appendChild(div);

let currentTempView: EditorView | null = null;

// Create a hidden view with the given document and extensions that
// lives until the next call to `tempView`.
// From: https://github.com/codemirror/view/blob/main/test/tempview.ts
function tempView(doc = '', format: string): EditorView {
  if (currentTempView) {
    currentTempView.destroy();
    currentTempView = null;
  }

  const extensions = getExtensions(format, {} as any);
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
  test('ftl mode', () => {
    const view = tempView('foo { $bar }', 'ftl');

    const text = getAncestorWith(view.domAtPos(1).node, 'spellcheck');
    expect(text?.getAttribute('spellcheck')).toBe('true');

    const ph = getAncestorWith(view.domAtPos(8).node, 'spellcheck');
    expect(ph?.getAttribute('spellcheck')).toBe('false');
  });

  test('common mode', () => {
    const view = tempView('%1$s foo', 'common');

    const text = getAncestorWith(view.domAtPos(7).node, 'spellcheck');
    expect(text?.getAttribute('spellcheck')).toBe('true');

    const ph = getAncestorWith(view.domAtPos(1).node, 'spellcheck');
    expect(ph?.getAttribute('spellcheck')).toBe('false');
  });
});
