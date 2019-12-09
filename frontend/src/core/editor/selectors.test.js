import {
    _existingTranslation,
} from './selectors';


const EDITOR = {
    initialTranslation: 'something',
};

const ACTIVE_TRANSLATION = { pk: 1, string: 'something' };

const HISTORY = {
    translations: [
        {
            pk: 12,
            string: 'I was there before',
            approved: false,
        },
        {
            pk: 98,
            string: 'hello, world!',
            approved: true,
        }
    ],
};


describe('sameExistingTranslation', () => {
    it('finds identical initial/active translation', () => {
        expect(_existingTranslation(
            { ...EDITOR, translation: EDITOR.initialTranslation },
            ACTIVE_TRANSLATION,
            HISTORY,
        )).toEqual(ACTIVE_TRANSLATION);
    });

    it('finds identical translation in history', () => {
        expect(_existingTranslation(
            { ...EDITOR, translation: HISTORY.translations[0].string },
            ACTIVE_TRANSLATION,
            HISTORY,
        )).toEqual(HISTORY.translations[0]);
    });

    it('misses identical but approved translation in history', () => {
        expect(_existingTranslation(
            { ...EDITOR, translation: HISTORY.translations[1].string },
            ACTIVE_TRANSLATION,
            HISTORY,
        )).toEqual(HISTORY.translations[1]);
    });
});
