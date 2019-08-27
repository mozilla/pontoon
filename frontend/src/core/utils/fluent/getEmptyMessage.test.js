import getEmptyMessage from './getEmptyMessage';
import parser from './parser';


describe('getEmptyMessage', () => {
    it('empties a simple value', () => {
        const source = parser.parseEntry('my-message = Some value');
        const message = getEmptyMessage(source);

        expect(message.value.elements[0].value).toEqual('');
    });

    it('empties a single simple attribute', () => {
        const source = parser.parseEntry('my-message =\n    .my-attr = Hello');
        const message = getEmptyMessage(source);

        expect(message.attributes[0].id.name).toEqual('my-attr');
        expect(message.attributes[0].value.elements[0].value).toEqual('');
    });

    it('empties both value and attributes', () => {
        const source = parser.parseEntry('my-message = Some value\n    .my-attr = Hello');
        const message = getEmptyMessage(source);

        expect(message.value.elements[0].value).toEqual('');
        expect(message.attributes[0].id.name).toEqual('my-attr');
        expect(message.attributes[0].value.elements[0].value).toEqual('');
    });

    it('empties several attributes', () => {
        const source = parser.parseEntry('my-message =\n    .my-attr = Hello\n    .title = Title');
        const message = getEmptyMessage(source);

        expect(message.attributes[0].id.name).toEqual('my-attr');
        expect(message.attributes[0].value.elements[0].value).toEqual('');
        expect(message.attributes[1].id.name).toEqual('title');
        expect(message.attributes[1].value.elements[0].value).toEqual('');
    });
});
