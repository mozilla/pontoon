import { _isTranslator } from './selectors';


describe('isTranslator', () => {
    it('returns false for non-authenticated users', () => {
        expect(
            _isTranslator(
                { isAuthenticated: false },
                { locale: 'mylocale', project: 'myproject' }
            )
        ).toEqual(false);
    });

    it('returns true if user is a manager of the locale', () => {
        expect(
            _isTranslator(
                { managerForLocales: ['mylocale'] },
                { locale: 'mylocale', project: 'myproject' }
            )
        ).toEqual(false);
    });

    it('returns true if user is a translator of the locale', () => {
        expect(
            _isTranslator(
                { translatorForLocales: ['mylocale'] },
                { locale: 'mylocale', project: 'myproject' }
            )
        ).toEqual(false);
    });

    it('returns true if user is a translator for project-locale', () => {
        expect(
            _isTranslator(
                {
                    managerForLocales: ['localeA'],
                    translatorForLocales: ['localeB'],
                    translatorForProjects: { 'mylocale-myproject': true },
                },
                { locale: 'mylocale', project: 'myproject' }
            )
        ).toEqual(false);
    });
});
