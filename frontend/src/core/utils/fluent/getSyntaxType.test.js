import getSyntaxType from './getSyntaxType';
import parser from './parser';

describe('getSyntaxType', () => {
    it('returns "simple" for a string with simple value', () => {
        const input = 'my-entry = Hello!';
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('simple');
    });

    it('returns "simple" for a string with multiline value', () => {
        const input = `
my-entry =
    Multi
    line
    value.`;
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('simple');
    });

    it('returns "simple" for a string with a reference to a built-in function', () => {
        const input =
            'my-entry = Today is { DATETIME($date, month: "long", year: "numeric", day: "numeric") }';
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('simple');
    });

    it('returns "simple" for a string with a Term', () => {
        const input = '-my-entry = Hello!';
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('simple');
    });

    it('returns "simple" for a string with a TermReference', () => {
        const input = 'my-entry = Term { -term } Reference';
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('simple');
    });

    it('returns "simple" for a string with a MessageReference', () => {
        const input = 'my-entry = { my_id }';
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('simple');
    });

    it('returns "simple" for a string with a MessageReference with attribute', () => {
        const input = 'my-entry = { my_id.title }';
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('simple');
    });

    it('returns "simple" for a string with a StringExpression', () => {
        const input = 'my-entry = { "" }';
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('simple');
    });

    it('returns "simple" for a string with a NumberExpression', () => {
        const input = 'my-entry = { 5 }';
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

    it('returns "rich" for a string with no value and two attributes', () => {
        const input = `
my-entry =
    .an-atribute = Hello!
    .another-atribute = World!`;
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('rich');
    });

    it('returns "rich" for a string with a select expression', () => {
        const input = `
my-entry =
    { PLATFORM() ->
        [variant] Hello!
       *[another-variant] World!
    }`;
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('rich');
    });

    it('returns "rich" for a string with a double select expression in attribute', () => {
        const input = `
my-entry =
    .label =
        { PLATFORM() ->
            [macos] Choose
           *[other] Browse
        }
    .accesskey =
        { PLATFORM() ->
            [macos] e
           *[other] o
        }`;
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('rich');
    });

    it('returns "rich" for a string with multiple select expressions and surrounding text', () => {
        const input = `
my-entry =
    There { $num ->
        [one] is one email
       *[other] are many emails
    } for { $gender ->
       *[masculine] him
        [feminine] her
    }`;
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('rich');
    });

    it('returns "complex" for a string with nested select expressions', () => {
        const input = `
my-entry =
    { $gender ->
       *[masculine]
            { $num ->
                [one] There is one email for her
               *[other] There are many emails for her
            }
        [feminine]
            { $num ->
                [one] There is one email for him
               *[other] There are many emails for him
            }
    }`;
        const message = parser.parseEntry(input);

        expect(getSyntaxType(message)).toEqual('complex');
    });
});
