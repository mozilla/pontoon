import { startCompletion } from '@codemirror/autocomplete';
import { undo } from '@codemirror/commands';
import { EditorState } from '@codemirror/state';
import { EditorView } from '@codemirror/view';

import { parseEntry } from '~/utils/message';

import { getExtensions } from './editFieldExtensions';
import { findGhostText, ghostText, setGhostTextCandidates } from './ghostText';

describe('findGhostText', () => {
  const segmenter = new Intl.Segmenter('it', { granularity: 'word' });
  const find = (before: string, candidates: string[], after = '') =>
    findGhostText(before, after, candidates, segmenter);

  const firefox = 'Firefox non riesce a trovare il server';

  test('suggests nothing without candidates or content', () => {
    expect(find('Firefox non r', [])).toBe('');
    expect(find('', [firefox])).toBe('');
  });

  test('suggests nothing for a short match', () => {
    expect(find('Un fi', ['Il file'])).toBe(''); // ' fi'
    expect(find('Un fil', ['Il file'])).toBe('e'); // ' fil'
  });

  test('completes the current word', () => {
    expect(find('Firefox non r', [firefox])).toBe('iesce');
    expect(find('Impossibile trov', [firefox])).toBe('are');
  });

  test('completes a word at the start of the content', () => {
    expect(find('Salv', ['Salva il file'])).toBe('a');
  });

  test('completes a word at the start of the candidate', () => {
    expect(find('Apri salv', ['salva il file'])).toBe('a');
  });

  test('does not complete a word from its middle', () => {
    // 'icon' is within 'sull'icona'
    expect(find('Una pericon', ["Fai clic sull'icona"])).toBe('');
    // 'salv' is within 'Aprisalv'
    expect(find('Aprisalv', ['salva il file'])).toBe('');
  });

  test('suggests the next word for a good match', () => {
    expect(find('Firefox non riesce', [firefox])).toBe(' a');
    expect(find('Firefox non riesce ', [firefox])).toBe('a');
    expect(find('Impossibile trovare il ', [firefox])).toBe('server');
  });

  test('does not suggest the next word for a weaker match', () => {
    expect(find('Apri il', ['Apri il file'])).toBe('');
    expect(find('Apri il ', ['Apri il file'])).toBe('file');
  });

  test('suggests trailing punctuation as the next word', () => {
    expect(find('Salva il file', ['Salva il file.'])).toBe('.');
    expect(find('Salva il file.', ['Salva il file.'])).toBe('');
  });

  test('prefers the longest match', () => {
    const candidates = ['Salva il documento', 'Ora salva il file'];
    expect(find('Ora salva il ', candidates)).toBe('file');
  });

  test('prefers the earlier candidate on a tie', () => {
    const candidates = ['Salva il file', 'Salva il documento'];
    expect(find('Salva il ', candidates)).toBe('file');
  });

  test('falls back to a shorter match with something to suggest', () => {
    const candidates = ['Elimina tutto', 'Eliminare tutto'];
    expect(find('Elimina', candidates)).toBe('re');
  });

  test('keeps placeholders and tags together', () => {
    const fluent = 'Elimina { $count } file';
    expect(find('Elimina ', [fluent])).toBe('{ $count }');
    expect(find('Elimina { $co', [fluent])).toBe('unt }');
    expect(find('Elimina { $count } ', [fluent])).toBe('file');

    const html = 'Fai clic su <strong>Salva</strong>';
    expect(find('Fai clic su ', [html])).toBe('<strong>');
    expect(find('Fai clic su <strong>', [html])).toBe('Salva');
  });

  test('does not continue past the end of the line', () => {
    const multiline = 'Prima riga \nSeconda riga';
    expect(find('Prima riga', [multiline])).toBe('');
    expect(find('Prima riga \nSec', [multiline])).toBe('onda');
  });

  test('does not suggest anything in the middle of a word', () => {
    expect(find('Salva il ', ['Salva il file'], 'file')).toBe('');
  });

  test('does not repeat what is already after the cursor', () => {
    expect(find('Salva il', ['Salva il file'], ' file')).toBe('');
    expect(find('Salva il', ['Salva il file'], ' documento')).toBe(' file');
  });

  test('uses word segmentation for languages without spaces', () => {
    const ja = new Intl.Segmenter('ja', { granularity: 'word' });
    // この | ファイル | を | 開く
    expect(findGhostText('このファイ', '', ['このファイルを開く'], ja)).toBe(
      'ル',
    );
  });
});

describe('ghostText extension', () => {
  const parent = document.createElement('div');
  document.body.appendChild(parent);

  let view: EditorView | null = null;
  afterEach(() => {
    view?.destroy();
    view = null;
  });

  function createView(
    doc: string,
    candidates: string[],
    source = doc,
    onEscape = () => false,
  ) {
    const entry = parseEntry('fluent', `key = ${source}`)!;
    const ref = { current: { onEscape } };
    const extensions = [getExtensions(entry, ref as any, doc), ghostText('it')];
    const state = EditorState.create({
      doc,
      extensions,
      selection: { anchor: doc.length },
    });
    view = new EditorView({ state, parent });
    view.dispatch({ effects: setGhostTextCandidates.of(candidates) });
    return view;
  }

  const ghost = () => parent.querySelector('.ghost-text')?.textContent ?? null;

  function press(key: string) {
    const event = new KeyboardEvent('keydown', {
      key,
      bubbles: true,
      cancelable: true,
    });
    view!.contentDOM.dispatchEvent(event);
    return event.defaultPrevented;
  }

  const firefox = 'Firefox non riesce a trovare il server';

  test('shows ghost text after the cursor', () => {
    createView('Firefox non r', [firefox]);
    expect(ghost()).toBe('iesce');
    expect(view!.state.doc.toString()).toBe('Firefox non r');
    expect(parent.querySelector('.ghost-text')?.ariaHidden).toBe('true');
  });

  test('updates with the candidates', () => {
    createView('Firefox non r', []);
    expect(ghost()).toBeNull();

    view!.dispatch({ effects: setGhostTextCandidates.of([firefox]) });
    expect(ghost()).toBe('iesce');

    view!.dispatch({ effects: setGhostTextCandidates.of([]) });
    expect(ghost()).toBeNull();
  });

  test('accepts ghost text with Tab, one word at a time', () => {
    createView('Firefox non r', [firefox]);

    expect(press('Tab')).toBe(true);
    expect(view!.state.doc.toString()).toBe('Firefox non riesce');
    expect(view!.state.selection.main.head).toBe(18);
    expect(ghost()).toBe(' a');

    press('Tab');
    press('Tab');
    expect(view!.state.doc.toString()).toBe('Firefox non riesce a trovare');
    expect(ghost()).toBe(' il');
  });

  test('accepting ghost text can be undone', () => {
    createView('Firefox non r', [firefox]);
    press('Tab');
    expect(view!.state.doc.toString()).toBe('Firefox non riesce');

    undo(view!);
    expect(view!.state.doc.toString()).toBe('Firefox non r');
  });

  test('leaves Tab alone without ghost text', () => {
    createView('Qualcosa di diverso', [firefox]);
    expect(ghost()).toBeNull();
    expect(press('Tab')).toBe(false);
    expect(view!.state.doc.toString()).toBe('Qualcosa di diverso');
  });

  test('hides ghost text with Escape until the next change', () => {
    createView('Firefox non r', [firefox]);

    expect(press('Escape')).toBe(true);
    expect(ghost()).toBeNull();
    expect(press('Tab')).toBe(false);
    expect(view!.state.doc.toString()).toBe('Firefox non r');

    view!.dispatch({
      changes: { from: 13, insert: 'i' },
      selection: { anchor: 14 },
    });
    expect(ghost()).toBe('esce');
  });

  test('closes the editor popups with Escape before hiding ghost text', () => {
    const onEscape = vi.fn(() => true);
    createView('Firefox non r', [firefox], undefined, onEscape);

    press('Escape');
    expect(onEscape).toHaveBeenCalledTimes(1);
    expect(ghost()).toBe('iesce');
  });

  test('is not shown with a selection', () => {
    createView('Firefox non r', [firefox]);
    view!.dispatch({ selection: { anchor: 8, head: 13 } });
    expect(ghost()).toBeNull();
    expect(press('Tab')).toBe(false);
  });

  test('is shown at the cursor, not only at the end', () => {
    createView('Firefox non r!', [firefox]);
    view!.dispatch({ selection: { anchor: 13 } });
    expect(ghost()).toBe('iesce');
    press('Tab');
    expect(view!.state.doc.toString()).toBe('Firefox non riesce!');
  });

  test('gives way to the placeholder autocomplete', async () => {
    const source = 'Elimina { $count } file';
    createView('Elimina {', [source], source);
    expect(ghost()).toBe(' $count }');

    startCompletion(view!);
    await vi.waitFor(() => {
      expect(parent.querySelector('.cm-tooltip-autocomplete')).not.toBeNull();
    });
    expect(ghost()).toBeNull();
  });
});
