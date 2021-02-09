import flattenMessage from './flattenMessage';
import parser from './parser';

describe('flattenMessage', () => {
    it('does not modify value with single element', () => {
        const message = parser.parseEntry('title = My Title');
        const res = flattenMessage(message);

        expect(res.value.elements).toHaveLength(1);
        expect(res.value.elements[0].value).toEqual('My Title');
    });

    it('does not modify attributes with single element', () => {
        const message = parser.parseEntry('title =\n    .foo = Bar');
        const res = flattenMessage(message);

        expect(res.attributes).toHaveLength(1);
        expect(res.attributes[0].value.elements).toHaveLength(1);
        expect(res.attributes[0].value.elements[0].value).toEqual('Bar');
    });

    it('does not modify value with a single select expression', () => {
        const input =
            'my-entry =' +
            '\n    { PLATFORM() ->' +
            '\n        [variant] Hello!' +
            '\n       *[another-variant] World!' +
            '\n    }';
        const message = parser.parseEntry(input);
        const res = flattenMessage(message);

        expect(res.value.elements).toHaveLength(1);
        expect(
            res.value.elements[0].expression.variants[0].value.elements[0]
                .value,
        ).toEqual('Hello!');
        expect(
            res.value.elements[0].expression.variants[1].value.elements[0]
                .value,
        ).toEqual('World!');
    });

    it('flattens a value with several elements', () => {
        const message = parser.parseEntry('title = My { $awesome } Title');

        expect(message.value.elements).toHaveLength(3);

        const res = flattenMessage(message);

        expect(res.value.elements).toHaveLength(1);
        expect(res.value.elements[0].value).toEqual('My { $awesome } Title');
    });

    it('flattens an attribute with several elements', () => {
        const message = parser.parseEntry(
            'title =\n    .foo = Bar { -foo } Baz',
        );

        expect(message.attributes[0].value.elements).toHaveLength(3);

        const res = flattenMessage(message);

        expect(res.attributes).toHaveLength(1);
        expect(res.attributes[0].value.elements).toHaveLength(1);
        expect(res.attributes[0].value.elements[0].value).toEqual(
            'Bar { -foo } Baz',
        );
    });

    it('flattens value and attributes', () => {
        const input =
            'batman = The { $dark } Knight' +
            '\n    .weapon = Brain and { -wayne-enterprise }' +
            '\n    .history = Lost { 2 } parents, has { 1 } "$alfred"';
        const message = parser.parseEntry(input);

        expect(message.value.elements).toHaveLength(3);
        expect(message.attributes[0].value.elements).toHaveLength(2);
        expect(message.attributes[1].value.elements).toHaveLength(5);

        const res = flattenMessage(message);

        expect(res.value.elements).toHaveLength(1);
        expect(res.value.elements[0].value).toEqual('The { $dark } Knight');

        expect(res.attributes).toHaveLength(2);

        expect(res.attributes[0].value.elements).toHaveLength(1);
        expect(res.attributes[0].value.elements[0].value).toEqual(
            'Brain and { -wayne-enterprise }',
        );

        expect(res.attributes[1].value.elements).toHaveLength(1);
        expect(res.attributes[1].value.elements[0].value).toEqual(
            'Lost { 2 } parents, has { 1 } "$alfred"',
        );
    });

    it('flattens values surrounding a select expression and select expression variants', () => {
        const input =
            'my-entry =' +
            '\n    There { $num ->' +
            '\n        [one] is one email' +
            '\n       *[other] are { $num } emails' +
            '\n    } for { $awesome } { $gender ->' +
            '\n       *[masculine] him' +
            '\n        [feminine] her' +
            '\n    }';
        const message = parser.parseEntry(input);
        const res = flattenMessage(message);

        expect(res.value.elements).toHaveLength(4);

        expect(res.value.elements[0].value).toEqual('There ');

        expect(
            res.value.elements[1].expression.variants[0].value.elements[0]
                .value,
        ).toEqual('is one email');
        expect(
            res.value.elements[1].expression.variants[1].value.elements[0]
                .value,
        ).toEqual('are { $num } emails');

        expect(res.value.elements[2].value).toEqual(' for { $awesome } ');

        expect(
            res.value.elements[3].expression.variants[0].value.elements[0]
                .value,
        ).toEqual('him');
        expect(
            res.value.elements[3].expression.variants[1].value.elements[0]
                .value,
        ).toEqual('her');
    });
});
