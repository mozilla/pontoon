import { Compartment, type Extension } from '@codemirror/state';
import { drawSelection, EditorView } from '@codemirror/view';

// drawSelection fixes tiny native caret (#4249) but regresses RTL selection (#4240)
// hence emptyEditorCaret toggles it on the empty <-> content boundary
// NOT NEEDED after https://bugzilla.mozilla.org/show_bug.cgi?id=2056439 is fixed
export function emptyEditorCaret(emptyAtInit: boolean): Extension {
  const drawn = new Compartment();
  return [
    drawn.of(emptyAtInit ? drawSelection() : []),
    EditorView.updateListener.of((update) => {
      const empty = update.state.doc.length === 0;
      if (update.docChanged && empty !== (update.startState.doc.length === 0)) {
        update.view.dispatch({
          effects: drawn.reconfigure(empty ? drawSelection() : []),
        });
      }
    }),
  ];
}
