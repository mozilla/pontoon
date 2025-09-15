import { EditorView } from '@codemirror/view';
import { EditorState } from '@codemirror/state';

import { getExtensions } from './editFieldExtensions';

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

  const extensions = getExtensions(format, `key = ${doc}`, {} as any);
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
    const view = tempView('plain', '%1$s foo');

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
