import { fluent } from 'core/utils';

import { _existingTranslation } from './selectors';

const EDITOR = {
    initialTranslation: 'something',
};

const EDITOR_FLUENT = {
    initialTranslation: fluent.parser.parseEntry('msg = something'),
};

const ENTITY = {
    format: 'po',
};

const ENTITY_FLUENT = {
    original: 'msg = Allez Morty !',
    format: 'ftl',
};

const ACTIVE_TRANSLATION = { pk: 1 };

const HISTORY = {
    translations: [
        {
            pk: 12,
            string: 'I was there before',
        },
        {
            pk: 98,
            string: 'hello, world!',
        },
        {
            pk: 10010,
            string: '',
        },
    ],
};

const HISTORY_FLUENT = {
    translations: [
        {
            pk: 12,
            string: 'msg = I like { -brand }',
        },
        {
            pk: 98,
            string: 'msg = hello, world!',
        },
        {
            pk: 431,
            string: 'msg = Come on Morty!\n',
        },
    ],
};

describe('sameExistingTranslation', () => {
    it('finds identical initial/active translation', () => {
        expect(
            _existingTranslation(
                { ...EDITOR, translation: EDITOR.initialTranslation },
                ACTIVE_TRANSLATION,
                HISTORY,
                ENTITY,
            ),
        ).toEqual(ACTIVE_TRANSLATION);
    });

    it('finds identical Fluent initial/active translation', () => {
        expect(
            _existingTranslation(
                {
                    ...EDITOR_FLUENT,
                    translation: EDITOR_FLUENT.initialTranslation,
                },
                ACTIVE_TRANSLATION,
                HISTORY_FLUENT,
                ENTITY_FLUENT,
            ),
        ).toEqual(ACTIVE_TRANSLATION);
    });

    it('finds empty initial/active translation', () => {
        expect(
            _existingTranslation(
                { translation: '', initialTranslation: '' },
                ACTIVE_TRANSLATION,
                HISTORY,
                ENTITY,
            ),
        ).toEqual(ACTIVE_TRANSLATION);
    });

    it('finds identical translation in history', () => {
        expect(
            _existingTranslation(
                { ...EDITOR, translation: HISTORY.translations[0].string },
                ACTIVE_TRANSLATION,
                HISTORY,
                ENTITY,
            ),
        ).toEqual(HISTORY.translations[0]);

        expect(
            _existingTranslation(
                { ...EDITOR, translation: HISTORY.translations[1].string },
                ACTIVE_TRANSLATION,
                HISTORY,
                ENTITY,
            ),
        ).toEqual(HISTORY.translations[1]);
    });

    it('finds identical Fluent translation in history', () => {
        expect(
            _existingTranslation(
                {
                    ...EDITOR_FLUENT,
                    translation: fluent.flattenMessage(
                        fluent.parser.parseEntry(
                            HISTORY_FLUENT.translations[0].string,
                        ),
                    ),
                },
                ACTIVE_TRANSLATION,
                HISTORY_FLUENT,
                ENTITY_FLUENT,
            ),
        ).toEqual(HISTORY_FLUENT.translations[0]);

        expect(
            _existingTranslation(
                {
                    ...EDITOR_FLUENT,
                    translation: fluent.flattenMessage(
                        fluent.parser.parseEntry(
                            HISTORY_FLUENT.translations[1].string,
                        ),
                    ),
                },
                ACTIVE_TRANSLATION,
                HISTORY_FLUENT,
                ENTITY_FLUENT,
            ),
        ).toEqual(HISTORY_FLUENT.translations[1]);
    });

    it('finds empty translation in history', () => {
        expect(
            _existingTranslation(
                { ...EDITOR, translation: '' },
                ACTIVE_TRANSLATION,
                HISTORY,
                ENTITY,
            ),
        ).toEqual(HISTORY.translations[2]);
    });

    it('finds a Fluent translation in history from a simplified Fluent string', () => {
        expect(
            _existingTranslation(
                { initialTranslation: '', translation: 'Come on Morty!' },
                ACTIVE_TRANSLATION,
                HISTORY_FLUENT,
                ENTITY_FLUENT,
            ),
        ).toEqual(HISTORY_FLUENT.translations[2]);
    });
});
