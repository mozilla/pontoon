import getSyntaxType from './getSyntaxType';
import parser from './parser';


describe('getSyntaxType', () => {
    it('returns "simple" for a string with simple value', () => {
        const input = 'my-entry = Hello!';
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('simple');
    });

    it('returns "simple" for a string with a single simple attribute', () => {
        const input = 'my-entry = \n    .an-atribute = Hello!';
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('simple');
    });

    it('returns "rich" for a string with value and attributes', () => {
        const input = 'my-entry = World\n    .an-atribute = Hello!';
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('rich');
    });

    it('returns "complex" for a string with a selector', () => {
        const input = 'my-entry = Hello { $who -> \n    [world] World\n    [you] You }';
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('complex');
    });
});
