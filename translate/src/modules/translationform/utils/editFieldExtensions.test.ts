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

describe('keyword', () => {
  describe('common mode', () => {
    test('i18next format', () => {
      const view1 = tempView('{{name}} foo', 'common');
      const nameEl = getAncestorWith(view1.domAtPos(1).node, 'dir');
      expect(nameEl?.textContent).toBe('{{name}}');

      const view2 = tempView('{{balance, money}} foo', 'common');
      const balanceEl = getAncestorWith(view2.domAtPos(1).node, 'dir');
      expect(balanceEl?.textContent).toBe('{{balance, money}}');

      const view3 = tempView('{{num, number(minimumFractionDigits: 2)}} foo', 'common');
      const numEl = getAncestorWith(view3.domAtPos(1).node, 'dir');
      expect(numEl?.textContent).toBe('{{num, number(minimumFractionDigits: 2)}}');
      
      const view4 = tempView('{{value, formatter1, formatter2}} foo', 'common');
      const valueEl = getAncestorWith(view4.domAtPos(1).node, 'dir');
      expect(valueEl?.textContent).toBe('{{value, formatter1, formatter2}}');
    });
  })
})