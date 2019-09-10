import getEmptyMessage from './getEmptyMessage';
import parser from './parser';


describe('getEmptyMessage', () => {
    it('empties a simple value', () => {
        const source = parser.parseEntry('my-message = Some value');
        const message = getEmptyMessage(source);

        expect(message.value.elements[0].value).toEqual('');
        expect(message.value.elements).toHaveLength(1);
    });

    it('empties a value with multiple elements', () => {
        const source = parser.parseEntry('my-message = Hello { $small } World');
        const message = getEmptyMessage(source);

        expect(message.value.elements[0].value).toEqual('');
        expect(message.value.elements).toHaveLength(1);
    });

    it('empties a single simple attribute', () => {
        const source = parser.parseEntry('my-message =\n    .my-attr = Hello');
        const message = getEmptyMessage(source);

        expect(message.attributes[0].id.name).toEqual('my-attr');

        expect(message.attributes[0].value.elements[0].value).toEqual('');
        expect(message.attributes[0].value.elements).toHaveLength(1);
    });

    it('empties both value and attributes', () => {
        const source = parser.parseEntry('my-message = Some value\n    .my-attr = Hello');
        const message = getEmptyMessage(source);

        expect(message.value.elements[0].value).toEqual('');
        expect(message.value.elements).toHaveLength(1);

        expect(message.attributes[0].id.name).toEqual('my-attr');
        expect(message.attributes[0].value.elements[0].value).toEqual('');
        expect(message.attributes[0].value.elements).toHaveLength(1);
    });

    it('empties several attributes', () => {
        const source = parser.parseEntry('my-message =\n    .my-attr = Hello\n    .title = Title');
        const message = getEmptyMessage(source);

        expect(message.attributes[0].id.name).toEqual('my-attr');
        expect(message.attributes[0].value.elements[0].value).toEqual('');
        expect(message.attributes[0].value.elements).toHaveLength(1);

        expect(message.attributes[1].id.name).toEqual('title');
        expect(message.attributes[1].value.elements[0].value).toEqual('');
        expect(message.attributes[1].value.elements).toHaveLength(1);
    });

    it('empties a select expression', () => {
        const input = `
my-entry =
    { PLATFORM() ->
        [variant] Hello!
       *[another-variant] { reference } World!
    }`;
        const source = parser.parseEntry(input);
        const message = getEmptyMessage(source);

        expect(message.value.elements[0].expression.variants[0].value.elements[0].value).toEqual('');
        expect(message.value.elements[0].expression.variants[0].value.elements).toHaveLength(1);

        expect(message.value.elements[0].expression.variants[1].value.elements[0].value).toEqual('');
        expect(message.value.elements[0].expression.variants[1].value.elements).toHaveLength(1);
   });
});
