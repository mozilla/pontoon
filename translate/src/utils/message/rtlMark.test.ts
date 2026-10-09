import { buildMessageEntry } from './buildMessageEntry';
import { editMessageEntry } from './editMessageEntry';
import { parseEntry } from './parseEntry';
import {
  LRM,
  RLM,
  addRtlMark,
  addRtlMarks,
  hasAddedRtlMark,
  needsRtlMark,
  removeRtlMark,
} from './rtlMark';

const FSI = String.fromCharCode(0x2068);
const PDI = String.fromCharCode(0x2069);

describe('needsRtlMark', () => {
  it.each([
    ['{ $name } را باز کنید', true],
    ['Firefox را باز کنید', true],
    ['%1$s فایل', true],
    ['<a>Firefox</a> را باز کنید', true],
    ['<a href="x">{ $name }</a> را باز کنید', true],
    [`${FSI}فایرفاکس${PDI} Firefox متن`, true],
  ])('needs a mark: %s', (text, expected) => {
    expect(needsRtlMark(text)).toBe(expected);
  });

  it.each([
    ['فایرفاکس را باز کنید', 'starts with RTL'],
    ['123 فایل', 'digits are not strong'],
    ['Open Firefox', 'no RTL content'],
    ['<a title="Firefox">فایرفاکس</a> را باز کنید', 'markup is skipped'],
    ['<br/>فایرفاکس', 'self-closing markup is skipped'],
    [`${FSI}Firefox${PDI} را باز کنید`, 'isolates are skipped'],
    [`${FSI}Firefox را باز کنید`, 'unterminated isolate'],
    [`${LRM}Firefox را باز کنید`, 'explicit LRM'],
    [`${RLM}Firefox را باز کنید`, 'explicit RLM'],
    ['', 'empty'],
  ])('does not need a mark: %s (%s)', (text) => {
    expect(needsRtlMark(text)).toBe(false);
  });
});

describe('addRtlMark & removeRtlMark', () => {
  it('round-trips added marks', () => {
    const text = '{ $name } را باز کنید';
    expect(addRtlMark(text)).toBe(RLM + text);
    expect(removeRtlMark(addRtlMark(text))).toBe(text);
  });

  it('keeps marks that would not be added back', () => {
    for (const text of [`${RLM}Firefox`, `${RLM}فایرفاکس`, 'Firefox']) {
      expect(removeRtlMark(text)).toBe(text);
      expect(addRtlMark(removeRtlMark(text))).toBe(text);
    }
  });
});

describe('RLM in the editor', () => {
  const field = (value: string) => ({
    id: '',
    name: '',
    keys: [],
    labels: [],
    handle: { current: { value } } as any,
  });

  it('adds an RLM when building RTL messages', () => {
    const base = parseEntry('fluent', 'key = x')!;
    const opts = { escapeHTML: null, trim: true, rtl: true };

    const res = buildMessageEntry(base, [field('{ $name } را باز کنید')], opts);
    expect(res?.value).toEqual([RLM, { $: 'name' }, ' را باز کنید']);

    const ltr = buildMessageEntry(base, [field('{ $name } را باز کنید')]);
    expect(ltr?.value).toEqual([{ $: 'name' }, ' را باز کنید']);
  });

  it('adds an RLM to each pattern that needs one', () => {
    const source = parseEntry(
      'fluent',
      'key =\n    { $n ->\n        [one] one\n       *[other] other\n    }\n    .title = x\n',
    )!;
    const opts = { escapeHTML: null, trim: true, rtl: true };
    const fields = editMessageEntry(source, undefined, { rtl: true });
    fields[0].handle.current.setValue('{ $n } فایل');
    fields[1].handle.current.setValue('فایل‌ها');
    fields[2].handle.current.setValue('Firefox عنوان');

    const res = buildMessageEntry(source, fields, opts)!;
    const [one, other] = (res.value as any).alt;
    expect(one.pat[0]).toBe(RLM);
    expect(other.pat[0]).toBe('فایل‌ها');
    expect(res.attributes?.get('title')).toEqual([RLM + 'Firefox عنوان']);
  });

  it('hides the RLM in the editor, and keeps the message unchanged', () => {
    const source = parseEntry('fluent', 'key = { $name } open')!;
    const target = parseEntry('fluent', `key = ${RLM}{ $name } را باز کنید`)!;
    const opts = { escapeHTML: null, trim: true, rtl: true };

    const fields = editMessageEntry(source, target, { rtl: true });
    expect(fields[0].handle.current.value).toBe('{ $name } را باز کنید');
    expect(buildMessageEntry(target, fields, opts)).toEqual(target);

    const ltrFields = editMessageEntry(source, target);
    expect(ltrFields[0].handle.current.value).toBe(
      `${RLM}{ $name } را باز کنید`,
    );
  });
});

describe('RLM in Fluent source', () => {
  const source = [
    'key =',
    '    { $n ->',
    '        [one] { $n } فایل',
    '       *[other] فایل‌ها',
    '    }',
    '    .title = Firefox عنوان',
    '',
  ].join('\n');

  it('adds an RLM to each pattern that needs one', () => {
    const entry = addRtlMarks(parseEntry('fluent', source)!);
    const [one, other] = (entry.value as any).alt;
    expect(one.pat[0]).toBe(RLM);
    expect(other.pat).toEqual(['فایل‌ها']);
    expect(entry.attributes?.get('title')).toEqual([RLM + 'Firefox عنوان']);
    expect(hasAddedRtlMark(entry)).toBe(true);
  });

  it('is idempotent', () => {
    const once = addRtlMarks(parseEntry('fluent', source)!);
    const twice = addRtlMarks(structuredClone(once));
    expect(twice).toEqual(once);
  });

  it('detects when no mark is added', () => {
    const entry = addRtlMarks(parseEntry('fluent', 'key = فایل { $n }')!);
    expect(hasAddedRtlMark(entry)).toBe(false);
  });
});
