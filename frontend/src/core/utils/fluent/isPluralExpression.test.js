import isPluralExpression from './isPluralExpression';
import parser from './parser';

describe('isPluralExpression', () => {
    it('returns false for elements that are not select expressions', () => {
        const input = 'my-entry = Hello!';
        const message = parser.parseEntry(input);
        const element = message.value.elements[0];

        expect(isPluralExpression(element.expression)).toBeFalsy();
    });

    it('returns true if all variant keys are CLDR plurals', () => {
        const input = `
my-entry =
    { $num ->
        [one] Hello!
       *[two] World!
    }`;
        const message = parser.parseEntry(input);
        const element = message.value.elements[0];

        expect(isPluralExpression(element.expression)).toBeTruthy();
    });

    it('returns true if all variant keys are numbers', () => {
        const input = `
my-entry =
    { $num ->
        [1] Hello!
       *[2] World!
    }`;
        const message = parser.parseEntry(input);
        const element = message.value.elements[0];

        expect(isPluralExpression(element.expression)).toBeTruthy();
    });

    it('returns true if one variant key is a CLDR plural and the other is a number', () => {
        const input = `
my-entry =
    { $num ->
        [one] Hello!
       *[1] World!
    }`;
        const message = parser.parseEntry(input);
        const element = message.value.elements[0];

        expect(isPluralExpression(element.expression)).toBeTruthy();
    });

    it('returns false if one variant key is a CLDR plural and the other is neither a CLDR plural nor a number', () => {
        const input = `
my-entry =
    { $num ->
        [one] Hello!
       *[variant] World!
    }`;
        const message = parser.parseEntry(input);
        const element = message.value.elements[0];

        expect(isPluralExpression(element.expression)).toBeFalsy();
    });

    it('returns false if at least one variant key is neither a CLDR plural nor a number', () => {
        const input = `
my-entry =
    { $num ->
        [variant] Hello!
       *[another-variant] World!
    }`;
        const message = parser.parseEntry(input);
        const element = message.value.elements[0];

        expect(isPluralExpression(element.expression)).toBeFalsy();
    });
});
