import ftl from '@fluent/dedent';
import { editMessageEntry } from './editMessageEntry';
import { extractAccessKeyCandidates } from './extractAccessKeyCandidates';
import { parseEntry } from './parseEntry';

describe('extractAccessKeyCandidates', () => {
  it('returns an empty list if the message has no label attribute or value', () => {
    const input = ftl`
      title =
        .foo = Bar
        .accesskey = B
      `;
    const message = editMessageEntry(parseEntry(input));
    const res = extractAccessKeyCandidates(message, 'accesskey');

    expect(res).toEqual([]);
  });

  it('returns a list of access keys from the message value', () => {
    const input = ftl`
      title = Candidates
        .accesskey = B
      `;
    const message = editMessageEntry(parseEntry(input));
    const res = extractAccessKeyCandidates(message, 'accesskey');

    expect(res).toEqual(['C', 'a', 'n', 'd', 'i', 't', 'e', 's']);
  });

  it('returns a list of access keys from the label attribute', () => {
    const input = ftl`
      title = Title
        .label = Candidates
        .accesskey = B
        .aria-label = Ignore this
        .value = Ignore this
      `;
    const message = editMessageEntry(parseEntry(input));
    const res = extractAccessKeyCandidates(message, 'accesskey');

    expect(res).toEqual(['C', 'a', 'n', 'd', 'i', 't', 'e', 's']);
  });

  it('returns a list of access keys from the value attribute', () => {
    const input = ftl`
      title =
        .accesskey = B
        .aria-label = Ignore this
        .value = Candidates
      `;
    const message = editMessageEntry(parseEntry(input));
    const res = extractAccessKeyCandidates(message, 'accesskey');

    expect(res).toEqual(['C', 'a', 'n', 'd', 'i', 't', 'e', 's']);
  });

  it('returns a list of access keys from the aria-label attribute', () => {
    const input = ftl`
      title =
        .accesskey = B
        .aria-label = Candidates
      `;
    const message = editMessageEntry(parseEntry(input));
    const res = extractAccessKeyCandidates(message, 'accesskey');

    expect(res).toEqual(['C', 'a', 'n', 'd', 'i', 't', 'e', 's']);
  });

  it('returns a list of access keys from the prefixed label attribute', () => {
    const input = ftl`
      title = Title
        .buttonlabel = Candidates
        .buttonaccesskey = B
        .label = Ignore this
        .value = Ignore this
      `;
    const message = editMessageEntry(parseEntry(input));
    const res = extractAccessKeyCandidates(message, 'buttonaccesskey');

    expect(res).toEqual(['C', 'a', 'n', 'd', 'i', 't', 'e', 's']);
  });

  it('Does not take Placeables into account when generating candidates', () => {
    const input = ftl`
      title = Title
        .label = Candidates { brand }
        .accesskey = B
      `;
    const message = editMessageEntry(parseEntry(input));
    const res = extractAccessKeyCandidates(message, 'accesskey');

    expect(res).toEqual(['C', 'a', 'n', 'd', 'i', 't', 'e', 's']);
  });

  it('returns a list of access keys from all label attribute variants', () => {
    const input = ftl`
      title = Title' +
        .label =
            { PLATFORM() ->
                [windows] Ctrl
               *[other] Cmd
            }
        .accesskey = C
      `;
    const message = editMessageEntry(parseEntry(input));
    const res = extractAccessKeyCandidates(message, 'accesskey');

    expect(res).toEqual(['C', 't', 'r', 'l', 'm', 'd']);
  });
});
