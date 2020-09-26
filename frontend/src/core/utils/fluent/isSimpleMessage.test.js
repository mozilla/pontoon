import isSimpleMessage from './isSimpleMessage';
import parser from './parser';

describe('isSimpleMessage', () => {
    it('returns true for a string with simple text', () => {
        const input = 'my-entry = Hello!';
        const message = parser.parseEntry(input);

        expect(isSimpleMessage(message)).toEqual(true);
    });

    it('returns false for string with text and an attribute', () => {
        const input = 'my-entry = Something\n    .an-atribute = Hello!';
        const message = parser.parseEntry(input);

        expect(isSimpleMessage(message)).toEqual(false);
    });

    it('returns false for string with no text and an attribute', () => {
        const input = 'my-entry =\n    .an-atribute = Hello!';
        const message = parser.parseEntry(input);

        expect(isSimpleMessage(message)).toEqual(false);
    });
});
