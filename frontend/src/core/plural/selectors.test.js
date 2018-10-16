import { _getPluralForm } from './selectors';


describe('getPluralForm', () => {
    it('returns the plural form', () => {
        expect(_getPluralForm(3, null)).toEqual(3);
        expect(_getPluralForm(-1, null)).toEqual(-1);
        expect(_getPluralForm(-1, { original_plural: '' })).toEqual(-1);
    });

    it('corrects the plural number', () => {
        expect(
            _getPluralForm(-1, { original_plural: 'I have a plural!' })
        ).toEqual(0);
    });
});
