import extractAccessKeyCandidates from './extractAccessKeyCandidates';
import flattenMessage from './flattenMessage';
import parser from './parser';

describe('extractAccessKeyCandidates', () => {
    it('returns null if the message has no attributes', () => {
        const message = flattenMessage(parser.parseEntry('title = Title'));
        const res = extractAccessKeyCandidates(message);

        expect(res).toEqual(null);
    });

    it('returns null if the message has no accesskey attribute', () => {
        const input = 'title =' + '\n    .foo = Bar';
        const message = flattenMessage(parser.parseEntry(input));
        const res = extractAccessKeyCandidates(message);

        expect(res).toEqual(null);
    });

    it('returns null if the message has no label attribute or value', () => {
        const input = 'title =' + '\n    .foo = Bar' + '\n    .accesskey = B';
        const message = flattenMessage(parser.parseEntry(input));
        const res = extractAccessKeyCandidates(message);

        expect(res).toEqual(null);
    });

    it('returns a list of access keys from the message value', () => {
        const input = 'title = Candidates' + '\n    .accesskey = B';
        const message = flattenMessage(parser.parseEntry(input));
        const res = extractAccessKeyCandidates(message);

        expect(res).toEqual(['C', 'a', 'n', 'd', 'i', 't', 'e', 's']);
    });

    it('returns a list of access keys from the label attribute', () => {
        const input =
            'title = Title' +
            '\n    .label = Candidates' +
            '\n    .accesskey = B';
        const message = flattenMessage(parser.parseEntry(input));
        const res = extractAccessKeyCandidates(message);

        expect(res).toEqual(['C', 'a', 'n', 'd', 'i', 't', 'e', 's']);
    });

    it('Does not take Placeables into account when generating candidates', () => {
        const input =
            'title = Title' +
            '\n    .label = Candidates { brand }' +
            '\n    .accesskey = B';
        const message = flattenMessage(parser.parseEntry(input));
        const res = extractAccessKeyCandidates(message);

        expect(res).toEqual(['C', 'a', 'n', 'd', 'i', 't', 'e', 's']);
    });

    it('returns a list of access keys from all label attribute variants', () => {
        const input =
            'title = Title' +
            '\n    .label =' +
            '\n        { PLATFORM() ->' +
            '\n            [windows] Ctrl' +
            '\n           *[other] Cmd' +
            '\n        }' +
            '\n    .accesskey = C';
        const message = flattenMessage(parser.parseEntry(input));
        const res = extractAccessKeyCandidates(message);

        expect(res).toEqual(['C', 't', 'r', 'l', 'm', 'd']);
    });
});
