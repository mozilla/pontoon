import {
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
            const res = _getTranslationForSelectedEntity(entities, navigation, -1);

            expect(res).toEqual('world');
        });

        it('does not return rejected translations', () => {
            const navigation = {
                entity: 3,
            };
            const res = _getTranslationForSelectedEntity(entities, navigation, -1);

            expect(res).toEqual('');
        });
    });
});
