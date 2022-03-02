import isSimpleSingleAttributeMessage from './isSimpleSingleAttributeMessage';
import parser from './parser';

describe('isSimpleSingleAttributeMessage', () => {
    it('returns true for a string with a single attribute', () => {
        const input = 'my-entry =\n    .an-atribute = Hello!';
        const message = parser.parseEntry(input);

        expect(isSimpleSingleAttributeMessage(message)).toEqual(true);
    });

    it('returns false for string with text', () => {
        const input = 'my-entry = Something\n    .an-atribute = Hello!';
        const message = parser.parseEntry(input);

        expect(isSimpleSingleAttributeMessage(message)).toEqual(false);
    });

    it('returns false for string with several attributes', () => {
        const input =
            'my-entry =\n    .an-atribute = Hello!\n    .two-attrites = World!';
        const message = parser.parseEntry(input);

        expect(isSimpleSingleAttributeMessage(message)).toEqual(false);
    });
});
