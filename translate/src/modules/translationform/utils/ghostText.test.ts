import { startCompletion } from '@codemirror/autocomplete';
import { undo } from '@codemirror/commands';
import { EditorState } from '@codemirror/state';
import { EditorView } from '@codemirror/view';

import { parseEntry } from '~/utils/message';

import { getExtensions } from './editFieldExtensions';
import { findGhostText, ghostText, setGhostTextCandidates } from './ghostText';

describe('findGhostText', () => {
  const segmenter = new Intl.Segmenter('it', { granularity: 'word' });
  const find = (before: string, candidates: string[]) =>
    findGhostText(before, candidates, segmenter);

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

  test('does not suggest the next word after the middle of a word', () => {
    // 'icona' is within 'pericona' and 'sull'icona'
    expect(find('Una pericona di ', ["Fai clic sull'icona di sistema"])).toBe(
      '',
    );
    // 'salva' is within 'Aprisalva'
    expect(find('Aprisalva il ', ['salva il file'])).toBe('');
  });

  test('suggests the next word after enough whole words', () => {
    const candidate = "Fai clic sull'icona di sistema e poi chiudi";
    expect(find('Una pericona di sistema e ', [candidate])).toBe('poi');
  });

  test('uses the first aligned occurrence of the match', () => {
    expect(find('cerc', ['Ricerca o cerca nel web'])).toBe('a');
    const candidate = 'Riapri la scheda o apri la finestra';
    expect(find('apri la ', [candidate])).toBe('finestra');
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

  test('uses the earlier candidate on a tie, even with nothing to suggest', () => {
    expect(find('Elimina', ['Elimina tutto', 'Eliminare tutto'])).toBe('');
    expect(find('Elimina', ['Eliminare tutto', 'Elimina tutto'])).toBe('re');
  });

  test('does not fall back to a shorter match', () => {
    const before = 'Hai { $count } nuovi messaggi';
    const shorter = 'Hai { $count } messaggi nuovi';
    expect(find(before, [shorter])).toBe(' nuovi');
    expect(find(before, ['Hai { $count } nuovi messaggi', shorter])).toBe('');
  });

  test('keeps placeholders and tags together', () => {
    const fluent = 'Elimina { $count } file';
    expect(find('Elimina ', [fluent])).toBe('{ $count }');
    expect(find('Elimina { $co', [fluent])).toBe('unt }');
    expect(find('Elimina { $count } ', [fluent])).toBe('file');

    const html = 'Fai clic su <strong>Salva</strong> per continuare';
    expect(find('Fai clic su ', [html])).toBe('<strong>Salva</strong>');
    expect(find('Fai clic su <strong>', [html])).toBe('Salva</strong>');
  });

  test('does not continue past the end of the line', () => {
    const multiline = 'Prima riga \nSeconda riga';
    expect(find('Prima riga', [multiline])).toBe('');
    expect(find('Prima riga \nSec', [multiline])).toBe('onda');
  });

  test('uses word segmentation for languages without spaces', () => {
    const ja = new Intl.Segmenter('ja', { granularity: 'word' });
    // この | ファイル | を | 開く
    expect(findGhostText('このファイ', ['このファイルを開く'], ja)).toBe('ル');
  });

  describe('counts a CJK letter as two characters', () => {
    test('in Japanese', () => {
      const ja = new Intl.Segmenter('ja', { granularity: 'word' });
      const jaFind = (before: string) => findGhostText(before, [jaFailed], ja);
      // サーバー | へ | の | 接続 | に | 失敗 | しま | した | 。 | ネットワーク | 設定 | を | 確認 | …
      const jaFailed =
        'サーバーへの接続に失敗しました。ネットワーク設定を確認してください。';
      expect(jaFind('への接続')).toBe('に');
      expect(jaFind('接続に失敗')).toBe('しま');
      expect(jaFind('ネットワーク')).toBe('設定');
      expect(jaFind('接続')).toBe('');
      expect(jaFind('設定を')).toBe('');
      expect(jaFind('を確認')).toBe('');
      expect(jaFind('設定を確認')).toBe('し');
      expect(jaFind('定を確認')).toBe('');
      expect(jaFind('ました。')).toBe('');
      expect(jaFind('しました。')).toBe('ネットワーク');
    });

    test('in Chinese', () => {
      const zh = new Intl.Segmenter('zh', { granularity: 'word' });
      const zhFind = (before: string) =>
        findGhostText(before, ['无法连接到服务器'], zh);
      // 无法 | 连接 | 到 | 服务器
      expect(zhFind('无法连接')).toBe('到');
      expect(zhFind('连接')).toBe('');
      expect(zhFind('无法连')).toBe('接');
      expect(zhFind('无连')).toBe('');
    });

    test('in Korean', () => {
      const ko = new Intl.Segmenter('ko', { granularity: 'word' });
      const koFind = (before: string) =>
        findGhostText(before, ['서버에 연결할 수 없습니다'], ko);
      expect(koFind('연결할 수')).toBe(' 없습니다');
      expect(koFind('에 연')).toBe('결할');
      expect(koFind('결할 ')).toBe('');
    });

    test('but not a Thai letter', () => {
      const th = new Intl.Segmenter('th', { granularity: 'word' });
      // เปิด | ไฟล์ | ␣ | แล้ว | ปิด
      const thFind = (before: string) =>
        findGhostText(before, ['เปิดไฟล์ แล้วปิด'], th);
      expect(thFind('ไฟล์ ')).toBe('');
      expect(thFind('เปิดไฟล์ ')).toBe('แล้ว');
    });
  });

  describe('accepts a word with the punctuation attached to it', () => {
    test('leaving the space for the next word', () => {
      const candidate = 'Open the advanced reader';
      expect(find('Open the adv', [candidate])).toBe('anced');
      expect(find('Open the advanced', [candidate])).toBe(' reader');
      expect(find('Open the advanced ', [candidate])).toBe('reader');
    });

    test('with closing punctuation', () => {
      const candidate = 'Salva il file, poi chiudi.';
      expect(find('Salva il fi', [candidate])).toBe('le,');
      expect(find('Salva il file', [candidate])).toBe(',');
      expect(find('Salva il file,', [candidate])).toBe(' poi');
      expect(find('Salva il file, poi chiu', [candidate])).toBe('di.');
    });

    test('with opening punctuation', () => {
      const candidate = 'Fai clic su «Salva» per continuare';
      expect(find('Fai clic su', [candidate])).toBe(' «Salva»');
      expect(find('Fai clic su ', [candidate])).toBe('«Salva»');
      expect(find('¿Quieres ', ['¿Quieres continuar?'])).toBe('continuar?');
    });

    test('with no-break spaces, which join what is around them', () => {
      const fr = 'Voulez-vous continuer\u202f?';
      expect(find('Voulez-vous contin', [fr])).toBe('uer\u202f?');
      const quote = 'Il dit «\u00a0Bonjour\u00a0» à tous';
      expect(find('Il dit «\u00a0Bon', [quote])).toBe('jour\u00a0»');
      const km = 'Distanza di 100\u00a0km circa';
      expect(find('Distanza di 1', [km])).toBe('00\u00a0km');
    });

    test('with hyphenated words as one word', () => {
      expect(find('Voul', ['Voulez-vous continuer\u202f?'])).toBe('ez-vous');
      expect(find('Invia una e', ['Invia una e-mail'])).toBe('-mail');
    });

    test('one word at a time in languages without spaces', () => {
      const ja = new Intl.Segmenter('ja', { granularity: 'word' });
      const jaFind = (before: string) =>
        findGhostText(before, ['ファイル、フォルダを開く。'], ja);
      // ファイル | 、 | フォルダ | を | 開く | 。
      expect(jaFind('ファイル、フォ')).toBe('ルダ');
      expect(jaFind('ファイル、フォルダを開')).toBe('く。');

      const zh = new Intl.Segmenter('zh', { granularity: 'word' });
      // 打开 | 文件 | ， | 然后 | 关闭 | 。
      expect(findGhostText('打开文件，然', ['打开文件，然后关闭。'], zh)).toBe(
        '后',
      );

      const th = new Intl.Segmenter('th', { granularity: 'word' });
      // เปิด | ไฟล์ | ␣ | แล้ว | ปิด
      expect(findGhostText('เปิดไฟ', ['เปิดไฟล์ แล้วปิด'], th)).toBe('ล์');
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
      locale = 'it',
    }: {
      source?: string;
      onEscape?: () => boolean;
      locale?: string;
    } = {},
  ) {
    const entry = parseEntry('fluent', `key = ${source}`)!;
    const ref = { current: { onEscape } };
    const extensions = [
      getExtensions(entry, ref as any, doc),
      ghostText(locale),
    ];
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
    createView('Firefox non r', [firefox], { onEscape });

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

  test('is only shown at the end of the content', () => {
    createView('Firefox non r!', [firefox]);
    view!.dispatch({ selection: { anchor: 13 } });
    expect(ghost()).toBeNull();
    expect(press('Tab')).toBe(false);

    createView('Firefox non riesce il server', [firefox]);
    view!.dispatch({ selection: { anchor: 18 } });
    expect(ghost()).toBeNull();
  });

  test('is not shown at the end of a line with text below it', () => {
    const candidate = 'Prima riga completa\nSeconda riga';
    createView('Prima riga\nSeconda', [candidate], { source: 'Prima riga' });
    expect(ghost()).toBe(' riga');

    view!.dispatch({ selection: { anchor: 10 } });
    expect(ghost()).toBeNull();
  });

  test('is hidden after Backspace until the next change', () => {
    createView('Firefox non ri', [firefox]);
    expect(ghost()).toBe('esce');

    press('Backspace');
    expect(view!.state.doc.toString()).toBe('Firefox non r');
    expect(ghost()).toBeNull();
    expect(press('Tab')).toBe(false);

    view!.dispatch({ effects: setGhostTextCandidates.of([firefox]) });
    expect(ghost()).toBeNull();

    view!.dispatch({
      changes: { from: 13, insert: 'i' },
      selection: { anchor: 14 },
      userEvent: 'input.type',
    });
    expect(ghost()).toBe('esce');
  });

  test('is hidden after Delete until the next change', () => {
    createView('Firefox non rix', [firefox]);
    view!.dispatch({ selection: { anchor: 14 } });

    press('Delete');
    expect(view!.state.doc.toString()).toBe('Firefox non ri');
    expect(ghost()).toBeNull();

    view!.dispatch({
      changes: { from: 14, insert: 'e' },
      selection: { anchor: 15 },
      userEvent: 'input.type',
    });
    expect(ghost()).toBe('sce');
  });

  test('gives way to the placeholder autocomplete', async () => {
    const source = 'Elimina { $count } file';
    createView('Elimina {', [source], { source });
    expect(ghost()).toBe(' $count }');

    startCompletion(view!);
    await vi.waitFor(() => {
      expect(parent.querySelector('.cm-tooltip-autocomplete')).not.toBeNull();
    });
    expect(ghost()).toBeNull();
  });

  describe('with an IME', () => {
    // サーバー | へ | の | 接続 | に | 失敗 | しま | した | 。 | …
    const jaFailed =
      'サーバーへの接続に失敗しました。ネットワーク設定を確認してください。';

    beforeAll(() => {
      Range.prototype.getClientRects = () => [] as unknown as DOMRectList;
    });
    afterAll(() => {
      delete (Range.prototype as Partial<Range>).getClientRects;
    });

    async function compose(text: string) {
      const { contentDOM, state } = view!;
      view!.focus();
      contentDOM.dispatchEvent(new CompositionEvent('compositionstart'));
      const { node } = view!.domAtPos(state.selection.main.head);
      const textNode = node as Text;
      textNode.data += text;
      document.getSelection()!.collapse(textNode, textNode.length);
      await vi.waitFor(() => expect(view!.composing).toBe(true));
      return textNode;
    }

    test('shows ghost text while composing', async () => {
      createView('エラー：', [jaFailed], { locale: 'ja' });
      expect(ghost()).toBeNull();

      const composed = await compose('への接続');
      expect(view!.state.doc.toString()).toBe('エラー：への接続');
      expect(ghost()).toBe('に');

      expect(composed.isConnected).toBe(true);
      expect(composed.data).toBe('エラー：への接続');
    });

    test('leaves Tab and Escape to the IME while composing', async () => {
      createView('エラー：', [jaFailed], { locale: 'ja' });
      await compose('への接続');

      expect(press('Tab')).toBe(false);
      expect(press('Escape')).toBe(false);
      expect(view!.state.doc.toString()).toBe('エラー：への接続');
      expect(ghost()).toBe('に');
    });
  });
});
