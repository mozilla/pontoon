import {
    _getOrderedOtherLocales,
    _getPreferredLocalesCount,
} from './selectors';


describe('selectors', () => {
    const OTHERLOCALES = {
        translations: [
            { code: 'al' },
            { code: 'bl' },
            { code: 'cl' },
        ],
    };

    const USER = {
        isAuthenticated: true,
        preferredLocales: [
            'xl',
            'yl',
            'zl',
            'bl',
        ],
    };

    const NON_AUTHENTICATED_USER = {
        isAuthenticated: false,
    };

    describe('getOrderedOtherLocales', () => {
        it("returns user's prefered locales before remaining locales", () => {
            const res = _getOrderedOtherLocales(OTHERLOCALES, USER);
            expect(res).toEqual([
                { code: 'bl' },
                { code: 'al' },
                { code: 'cl' },
            ]);
        });

        it('returns locales in default order for non-authenticated users', () => {
            const res = _getOrderedOtherLocales(OTHERLOCALES, NON_AUTHENTICATED_USER);
            expect(res).toEqual(OTHERLOCALES.translations);
        });
    });

    describe('_getPreferredLocalesCount', () => {
        USER.isAuthenticated = true;

        it("returns number of user's prefered locales within given locales", () => {
            const res = _getPreferredLocalesCount(OTHERLOCALES, USER);
            expect(res).toEqual(1);
        });

        it('returns 0 for non-authenticated users', () => {
            const res = _getPreferredLocalesCount(OTHERLOCALES, NON_AUTHENTICATED_USER);
            expect(res).toEqual(0);
        });
    });
});
