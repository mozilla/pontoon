import {
    _getPluralForm,
    _getTranslationForSelectedEntity,
    _getTranslationStringForSelectedEntity,
} from './selectors';

describe('getPluralForm', () => {
    it('returns the plural form', () => {
        expect(_getPluralForm(3, null)).toEqual(3);
        expect(_getPluralForm(-1, null)).toEqual(-1);
        expect(_getPluralForm(-1, { original_plural: '' })).toEqual(-1);
    });

    it('corrects the plural number', () => {
        expect(
            _getPluralForm(-1, { original_plural: 'I have a plural!' }),
        ).toEqual(0);
    });
});

const ENTITIES = [
    {
        translation: [
            {
                string: 'world',
            },
        ],
    },
    {
        translation: [
            {
                string: 'wat',
                rejected: true,
            },
        ],
    },
];

describe('getTranslationForSelectedEntity', () => {
    it('returns the correct string', () => {
        const entity = ENTITIES[0];
        const res = _getTranslationForSelectedEntity(entity, -1);

        expect(res).toEqual({ string: 'world' });
    });

    it('does not return rejected translations', () => {
        const entity = ENTITIES[1];
        const res = _getTranslationForSelectedEntity(entity, -1);

        expect(res).toEqual(null);
    });
});

describe('getTranslationStringForSelectedEntity', () => {
    it('returns the correct string', () => {
        const entity = ENTITIES[0];
        const res = _getTranslationStringForSelectedEntity(entity, -1);

        expect(res).toEqual('world');
    });

    it('does not return rejected translations', () => {
        const entity = ENTITIES[1];
        const res = _getTranslationStringForSelectedEntity(entity, -1);

        expect(res).toEqual('');
    });
});
