import {
    _getSelectedEntity,
} from './selectors';


describe('selectors', () => {
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
