import { _isTranslator } from './selectors';

describe('isTranslator', () => {
    it('returns false for non-authenticated users', () => {
        expect(
            _isTranslator(
                { isAuthenticated: false },
                { code: 'mylocale' },
                { slug: 'myproject' },
            ),
        ).toBeFalsy();
    });

    it('returns true if user is a manager of the locale', () => {
        expect(
            _isTranslator(
                {
                    isAuthenticated: true,
                    managerForLocales: ['mylocale'],
                    translatorForLocales: [],
                    translatorForProjects: {},
                },
                { code: 'mylocale' },
                { slug: 'myproject' },
            ),
        ).toBeTruthy();
    });

    it('returns true if user is a translator of the locale', () => {
        expect(
            _isTranslator(
                {
                    isAuthenticated: true,
                    managerForLocales: [],
                    translatorForLocales: ['mylocale'],
                    translatorForProjects: {},
                },
                { code: 'mylocale' },
                { slug: 'myproject' },
            ),
        ).toBeTruthy();
    });

    it('returns true if user is a translator for project-locale', () => {
        expect(
            _isTranslator(
                {
                    isAuthenticated: true,
                    managerForLocales: ['localeA'],
                    translatorForLocales: ['localeB'],
                    translatorForProjects: { 'mylocale-myproject': true },
                },
                { code: 'mylocale' },
                { slug: 'myproject' },
            ),
        ).toBeTruthy();
    });
});
