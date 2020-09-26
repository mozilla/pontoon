import {
    getComplexFromRich,
    getComplexFromSimple,
    getRichFromComplex,
    getSimpleFromComplex,
} from './convertSyntax';

import getEmptyMessage from './getEmptyMessage';
import parser from './parser';

describe('getComplexFromRich', () => {
    it('converts rich translation to complex', () => {
        // Input is a Fluent AST.
        const current = parser.parseEntry('title = Mon titre');
        const original = 'title = My title';
        const initial = 'title = Mien titre';

        const res = getComplexFromRich(current, original, initial);

        expect(res[0]).toEqual('title = Mon titre\n');
    });

    it('returns the correct initial translation when one is provided', () => {
        const current = parser.parseEntry('title = Mon titre');
        const original = 'title = My title';
        const initial = 'title = Mien titre';

        const res = getComplexFromRich(current, original, initial);

        expect(res[1]).toEqual('title = Mien titre');
    });

    it('returns the correct initial translation when none exist', () => {
        const current = parser.parseEntry('title = Mon titre');
        const original = 'title = My title';
        // Initial is empty, there's no active translation.
        const initial = '';

        const res = getComplexFromRich(current, original, initial);

        expect(res[1]).toEqual('title = \n');
    });
});

describe('getComplexFromSimple', () => {
    it('converts simple translation to complex', () => {
        const current = 'Mon titre';
        const original = 'title = My title';
        const initial = 'title = Mien titre';

        const res = getComplexFromSimple(current, original, initial);

        expect(res[0]).toEqual('title = Mon titre\n');
    });

    it('returns the correct initial translation when one is provided', () => {
        const current = 'Mon titre';
        const original = 'title = My title';
        const initial = 'title = Mien titre';

        const res = getComplexFromSimple(current, original, initial);

        expect(res[1]).toEqual('title = Mien titre');
    });

    it('returns the correct initial translation when none exist', () => {
        const current = 'Mon titre';
        const original = 'title = My title';
        // Initial is empty, there's no active translation.
        const initial = '';

        const res = getComplexFromSimple(current, original, initial);

        expect(res[1]).toEqual('title = \n');
    });
});

describe('getRichFromComplex', () => {
    it('converts complex translation to rich', () => {
        const current = 'title = Mon titre';
        const original = 'title = My title';
        const initial = 'title = Mien titre';

        const res = getRichFromComplex(current, original, initial);

        expect(res[0]).toEqual(parser.parseEntry('title = Mon titre\n'));
    });

    it('returns the correct initial translation when one is provided', () => {
        const current = 'title = Mon titre';
        const original = 'title = My title';
        const initial = 'title = Mien titre';

        const res = getRichFromComplex(current, original, initial);

        expect(res[1]).toEqual(parser.parseEntry('title = Mien titre'));
    });

    it('returns the correct initial translation when none exist', () => {
        const current = 'title = Mon titre';
        const original = 'title = My title';
        // Initial is empty, there's no active translation.
        const initial = '';

        const res = getRichFromComplex(current, original, initial);

        expect(res[1]).toEqual(getEmptyMessage(parser.parseEntry('title = a')));
    });
});

describe('getSimpleFromComplex', () => {
    it('converts complex translation to simple', () => {
        const current = 'title = Mon titre';
        const original = 'title = My title';
        const initial = 'title = Mien titre';

        const res = getSimpleFromComplex(current, original, initial);

        expect(res[0]).toEqual('Mon titre');
    });

    it('returns the correct initial translation when one is provided', () => {
        const current = 'title = Mon titre';
        const original = 'title = My title';
        const initial = 'title = Mien titre';

        const res = getSimpleFromComplex(current, original, initial);

        expect(res[1]).toEqual('Mien titre');
    });

    it('returns the correct initial translation when none exist', () => {
        const current = 'title = Mon titre';
        const original = 'title = My title';
        // Initial is empty, there's no active translation.
        const initial = '';

        const res = getSimpleFromComplex(current, original, initial);

        expect(res[1]).toEqual('');
    });
});
