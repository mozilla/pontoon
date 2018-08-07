import {
    _getSelectedEntity,
    _getTranslationForSelectedEntity,
} from './selectors';


describe('selectors', () => {
    describe('getTranslationForSelectedEntity', () => {

        const entities = [
            {
                pk: 1,
                translation: [
                    {
                        string: 'hello',
                    },
                ],
            },
            {
                pk: 2,
                translation: [
                    {
                        string: 'world',
                    },
                ],
            },
            {
                pk: 3,
                translation: [
                    {
                        string: 'wat',
                        rejected: true,
                    },
                ],
            },
        ];

        it('returns the correct string', () => {
            const navigation = {
                entity: 2,
            };
            const res = _getTranslationForSelectedEntity(entities, navigation);

            expect(res).toEqual('world');
        });

        it('does not return rejected translations', () => {
            const navigation = {
                entity: 3,
            };
            const res = _getTranslationForSelectedEntity(entities, navigation);

            expect(res).toEqual('');
        });
    });

    describe('getSelectedEntity', () => {
        const entities = [
            {
                pk: 1,
                original: 'hello',
            },
            {
                pk: 2,
                original: 'world',
            },
        ];

        it('returns the selected entity', () => {
            const navigation = {
                entity: 2,
            };
            const res = _getSelectedEntity(entities, navigation);

            expect(res.original).toEqual('world');
        });

        it('returns undefined if the entity is missing', () => {
            const navigation = {
                entity: 3,
            };
            const res = _getSelectedEntity(entities, navigation);

            expect(res).toEqual(undefined);
        });
    });
});
