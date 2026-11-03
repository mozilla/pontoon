import { startCompletion } from '@codemirror/autocomplete';
import { undo } from '@codemirror/commands';
import { EditorState } from '@codemirror/state';
import { EditorView } from '@codemirror/view';

import type { MachineryAutocomplete } from '~/api/user';
import { parseEntry } from '~/utils/message';

import { getExtensions } from './editFieldExtensions';
import {
  findGhostText,
  ghostText,
  setGhostTextCandidates,
  setGhostTextMode,
} from './ghostText';

describe('findGhostText', () => {
  const segmenter = new Intl.Segmenter('it', { granularity: 'word' });
  const find = (before: string, candidates: string[], after = '') =>
    findGhostText(before, after, candidates, segmenter);
  const findFull = (before: string, candidates: string[]) =>
    findGhostText(before, '', candidates, segmenter, true);

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
    expect(find('Firefox non r', [firefox])).toBe('iesce ');
    expect(find('Impossibile trov', [firefox])).toBe('are ');
  });

  test('completes a word at the start of the content', () => {
    expect(find('Salv', ['Salva il file'])).toBe('a ');
  });

  test('completes a word at the start of the candidate', () => {
    expect(find('Apri salv', ['salva il file'])).toBe('a ');
  });

  test('does not complete a word from its middle', () => {
    // 'icon' is within 'sull'icona'
    expect(find('Una pericon', ["Fai clic sull'icona"])).toBe('');
    // 'salv' is within 'Aprisalv'
    expect(find('Aprisalv', ['salva il file'])).toBe('');
  });

  test('suggests the next word for a good match', () => {
    expect(find('Firefox non riesce', [firefox])).toBe(' a ');
    expect(find('Firefox non riesce ', [firefox])).toBe('a ');
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

  test('uses the earlier candidate on a tie, even with nothing to suggest', () => {
    expect(find('Elimina', ['Elimina tutto', 'Eliminare tutto'])).toBe('');
    expect(find('Elimina', ['Eliminare tutto', 'Elimina tutto'])).toBe('re ');
  });

  test('does not fall back to a shorter match', () => {
    const before = 'Hai { $count } nuovi messaggi';
    const shorter = 'Hai { $count } messaggi nuovi';
    expect(find(before, [shorter])).toBe(' nuovi');
    expect(find(before, ['Hai { $count } nuovi messaggi', shorter])).toBe('');
  });

  test('keeps placeholders and tags together', () => {
    const fluent = 'Elimina { $count } file';
    expect(find('Elimina ', [fluent])).toBe('{ $count } ');
    expect(find('Elimina { $co', [fluent])).toBe('unt } ');
    expect(find('Elimina { $count } ', [fluent])).toBe('file');

    const html = 'Fai clic su <strong>Salva</strong> per continuare';
    expect(find('Fai clic su ', [html])).toBe('<strong>Salva</strong> ');
    expect(find('Fai clic su <strong>', [html])).toBe('Salva</strong> ');
  });

  test('does not continue past the end of the line', () => {
    const multiline = 'Prima riga \nSeconda riga';
    expect(find('Prima riga', [multiline])).toBe('');
    expect(find('Prima riga \nSec', [multiline])).toBe('onda ');
  });

  test('does not suggest anything in the middle of a word', () => {
    expect(find('Salva il ', ['Salva il file'], 'file')).toBe('');
  });

  test('does not repeat what is already after the cursor', () => {
    expect(find('Salva il', ['Salva il file'], ' file')).toBe('');
    expect(find('Salva il', ['Salva il file'], ' documento')).toBe(' file');
    const candidates = ['Salva il file', 'Salva il documento'];
    expect(find('Salva il', candidates, ' file')).toBe('');
  });

  test('uses word segmentation for languages without spaces', () => {
    const ja = new Intl.Segmenter('ja', { granularity: 'word' });
    // この | ファイル | を | 開く
    expect(findGhostText('このファイ', '', ['このファイルを開く'], ja)).toBe(
      'ル',
    );
  });

  describe('accepts a word with the space after it', () => {
    test('so that the next word can be typed', () => {
      expect(find('Firefox non r', [firefox])).toBe('iesce ');
      expect(find('Firefox non riesce ', [firefox])).toBe('a ');
    });

    test('but adds no space that the candidate does not have', () => {
      expect(find('Firefox non riesce a trovare il ser', [firefox])).toBe(
        'ver',
      );
    });

    test('with the punctuation attached to the word', () => {
      const candidate = 'Salva il file, poi chiudi.';
      expect(find('Salva il fi', [candidate])).toBe('le, ');
      expect(find('Salva il file', [candidate])).toBe(', ');
      expect(find('Salva il file, poi chiu', [candidate])).toBe('di.');
    });

    test('with opening punctuation before the next word', () => {
      const candidate = 'Fai clic su «Salva» per continuare';
      expect(find('Fai clic su ', [candidate])).toBe('«Salva» ');
      expect(find('¿Quieres ', ['¿Quieres continuar?'])).toBe('continuar?');
    });

    test('with no-break spaces, which join what is around them', () => {
      const fr = 'Voulez-vous continuer\u202f?';
      expect(find('Voulez-vous contin', [fr])).toBe('uer\u202f?');
      const quote = 'Il dit «\u00a0Bonjour\u00a0» à tous';
      expect(find('Il dit «\u00a0Bon', [quote])).toBe('jour\u00a0» ');
      const km = 'Distanza di 100\u00a0km circa';
      expect(find('Distanza di 1', [km])).toBe('00\u00a0km ');
    });

    test('with hyphenated words as one word', () => {
      expect(find('Voul', ['Voulez-vous continuer\u202f?'])).toBe('ez-vous ');
      expect(find('Invia una e', ['Invia una e-mail'])).toBe('-mail');
    });

    test('one word at a time in languages without spaces', () => {
      const ja = new Intl.Segmenter('ja', { granularity: 'word' });
      const jaFind = (before: string) =>
        findGhostText(before, '', ['ファイル、フォルダを開く。'], ja);
      // ファイル | 、 | フォルダ | を | 開く | 。
      expect(jaFind('ファイル、フォ')).toBe('ルダ');
      expect(jaFind('ファイル、フォルダを開')).toBe('く。');

      const zh = new Intl.Segmenter('zh', { granularity: 'word' });
      // 打开 | 文件 | ， | 然后 | 关闭 | 。
      expect(
        findGhostText('打开文件，然', '', ['打开文件，然后关闭。'], zh),
      ).toBe('后');

      const th = new Intl.Segmenter('th', { granularity: 'word' });
      // เปิด | ไฟล์ | ␣ | แล้ว | ปิด
      expect(findGhostText('เปิดไฟ', '', ['เปิดไฟล์ แล้วปิด'], th)).toBe('ล์ ');
    });

    test('keeping the spacing and punctuation already after the cursor', () => {
      expect(find('Firefox non r', [firefox], ' a trovare')).toBe('iesce');
      expect(find('Firefox non', [firefox], ' a trovare')).toBe(' riesce');
      expect(find('Salva il fi', ['Salva il file, poi'], ', poi')).toBe('le');
      expect(find('Salva il file', ['Salva il file, poi'], ' poi')).toBe('');
    });
  });

  describe('full continuation', () => {
    test('suggests the rest of the candidate', () => {
      expect(findFull('Firefox non r', [firefox])).toBe(
        'iesce a trovare il server',
      );
      expect(findFull('Firefox non riesce ', [firefox])).toBe(
        'a trovare il server',
      );
    });

    test('only when word by word would suggest something', () => {
      expect(findFull('Un fi', ['Il file'])).toBe('');
      expect(findFull('Apri il', ['Apri il file'])).toBe('');
      expect(findFull('Una pericon', ["Fai clic sull'icona"])).toBe('');
      expect(findFull('Salva il file.', ['Salva il file.'])).toBe('');
    });

    test('continues onto further lines', () => {
      const multiline = 'Prima riga \r\nSeconda riga';
      expect(findFull('Prima riga', [multiline])).toBe(' \nSeconda riga');
    });
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
    {
      source = doc,
      onEscape = () => false,
      mode,
    }: {
      source?: string;
      onEscape?: () => boolean;
      mode?: MachineryAutocomplete;
    } = {},
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
    if (mode) {
      view.dispatch({ effects: setGhostTextMode.of(mode) });
    }
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
    expect(ghost()).toBe('iesce ');
    expect(view!.state.doc.toString()).toBe('Firefox non r');
    expect(parent.querySelector('.ghost-text')?.ariaHidden).toBe('true');
  });

  test('updates with the candidates', () => {
    createView('Firefox non r', []);
    expect(ghost()).toBeNull();

    view!.dispatch({ effects: setGhostTextCandidates.of([firefox]) });
    expect(ghost()).toBe('iesce ');

    view!.dispatch({ effects: setGhostTextCandidates.of([]) });
    expect(ghost()).toBeNull();
  });

  test('accepts ghost text with Tab, one word at a time', () => {
    createView('Firefox non r', [firefox]);

    expect(press('Tab')).toBe(true);
    expect(view!.state.doc.toString()).toBe('Firefox non riesce ');
    expect(view!.state.selection.main.head).toBe(19);
    expect(ghost()).toBe('a ');

    press('Tab');
    press('Tab');
    expect(view!.state.doc.toString()).toBe('Firefox non riesce a trovare ');
    expect(ghost()).toBe('il ');
  });

  test('accepting ghost text can be undone', () => {
    createView('Firefox non r', [firefox]);
    press('Tab');
    expect(view!.state.doc.toString()).toBe('Firefox non riesce ');

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
    expect(ghost()).toBe('esce ');
  });

  test('closes the editor popups with Escape before hiding ghost text', () => {
    const onEscape = vi.fn(() => true);
    createView('Firefox non r', [firefox], { onEscape });

    press('Escape');
    expect(onEscape).toHaveBeenCalledTimes(1);
    expect(ghost()).toBe('iesce ');
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

  test('is not shown when off', () => {
    createView('Firefox non r', [firefox], { mode: 'off' });
    expect(ghost()).toBeNull();
    expect(press('Tab')).toBe(false);

    view!.dispatch({ effects: setGhostTextMode.of('word') });
    expect(ghost()).toBe('iesce ');
  });

  test('accepts the full continuation at the end of the content', () => {
    createView('Firefox non r', [firefox], { mode: 'full' });
    expect(ghost()).toBe('iesce a trovare il server');

    press('Tab');
    expect(view!.state.doc.toString()).toBe(firefox);
    expect(ghost()).toBeNull();
  });

  test('accepts a full continuation over several lines', () => {
    const candidate = 'Prima riga\nSeconda riga';
    createView('Prima r', [candidate], { mode: 'full' });
    expect(ghost()).toBe('iga\nSeconda riga');

    press('Tab');
    expect(view!.state.doc.toString()).toBe(candidate);
    expect(view!.state.doc.lines).toBe(2);
  });

  test('completes word by word before other text, even in full mode', () => {
    createView('Firefox non r!', [firefox], { mode: 'full' });
    view!.dispatch({ selection: { anchor: 13 } });
    expect(ghost()).toBe('iesce');
  });

  test('gives way to the placeholder autocomplete', async () => {
    const source = 'Elimina { $count } file';
    createView('Elimina {', [source], { source });
    expect(ghost()).toBe(' $count } ');

    startCompletion(view!);
    await vi.waitFor(() => {
      expect(parent.querySelector('.cm-tooltip-autocomplete')).not.toBeNull();
    });
    expect(ghost()).toBeNull();
  });
});
