import { _getCurrentLocaleData } from './selectors';


describe('getCurrentLocaleData', () => {
    it('returns null when data is missing', () => {
        expect(
            _getCurrentLocaleData({}, {})
        ).toBeNull();

        expect(
            _getCurrentLocaleData({'kg': { code: 'kg' }}, {})
        ).toBeNull();

        expect(
            _getCurrentLocaleData({'kg': { code: 'kg' }}, { locale: 'kr' })
        ).toBeNull();
    });

    it('returns the correct locale', () => {
        const LOCALES = {
            'kr': { code: 'kr' },
            'kg': { code: 'kg' },
            'un': { code: 'un' },
        };

        expect(
            _getCurrentLocaleData(LOCALES, { locale: 'kr' })
        ).toEqual(LOCALES['kr']);
    });
});
