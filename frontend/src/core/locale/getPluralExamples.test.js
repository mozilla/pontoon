import getPluralExamples from './getPluralExamples';

describe('getPluralExamples', () => {
    it('returns a map of Slovenian plural examples', () => {
        const locale = {
            cldrPlurals: [1, 2, 3, 5],
            pluralRule:
                '(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3)',
        };
        const res = getPluralExamples(locale);
        const expected = {
            1: 1,
            2: 2,
            3: 3,
            5: 0,
        };
        expect(res).toEqual(expected);
    });

    it('prevents infinite loop if locale plurals are not configured properly', () => {
        const spy = jest.spyOn(console, 'error').mockImplementation(() => {});
        const locale = {
            cldrPlurals: [0, 1, 2, 3, 4, 5],
            pluralRule: '(n != 1)',
        };
        try {
            const res = getPluralExamples(locale);
            const expected = { 0: 1, 1: 2 };
            expect(res).toEqual(expected);
            expect(spy).toHaveBeenCalledWith(
                'Unable to generate plural examples.',
            );
        } finally {
            spy.mockRestore();
        }
    });
});
