import {
    _getNextEntity,
    _getPreviousEntity,
    _getSelectedEntity,
    _isReadOnlyEditor,
} from './selectors';

describe('selectors', () => {
    describe('getNextEntity', () => {
        const ENTITIES = [{ pk: 1 }, { pk: 2 }, { pk: 3 }];

        it('returns the next entity in the list', () => {
            const params = { entity: 1 };
            const res = _getNextEntity(ENTITIES, params);
            expect(res.pk).toEqual(2);
        });

        it('returns the first entity when the last one is selected', () => {
            const params = { entity: 3 };
            const res = _getNextEntity(ENTITIES, params);
            expect(res.pk).toEqual(1);
        });

        it('returns null when the current entity does not exist', () => {
            const params = { entity: 5 };
            const res = _getNextEntity(ENTITIES, params);
            expect(res).toBeNull();
        });
    });

    describe('getPreviousEntity', () => {
        const ENTITIES = [{ pk: 1 }, { pk: 2 }, { pk: 3 }];

        it('returns the previous entity in the list', () => {
            const params = { entity: 2 };
            const res = _getPreviousEntity(ENTITIES, params);
            expect(res.pk).toEqual(1);
        });

        it('returns the last entity when the first one is selected', () => {
            const params = { entity: 1 };
            const res = _getPreviousEntity(ENTITIES, params);
            expect(res.pk).toEqual(3);
        });

        it('returns null when the current entity does not exist', () => {
            const params = { entity: 5 };
            const res = _getPreviousEntity(ENTITIES, params);
            expect(res).toBeNull();
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

    describe('isReadOnlyEditor', () => {
        it('returns true if user not authenticated', () => {
            const entity = {
                readonly: false,
            };
            const user = {
                isAuthenticated: false,
            };
            const res = _isReadOnlyEditor(entity, user);

            expect(res).toBeTruthy();
        });

        it('returns true if entity read-only', () => {
            const entity = {
                readonly: true,
            };
            const user = {
                isAuthenticated: true,
            };
            const res = _isReadOnlyEditor(entity, user);

            expect(res).toBeTruthy();
        });

        it('returns false if entity not read-only and user authenticated', () => {
            const entity = {
                readonly: false,
            };
            const user = {
                isAuthenticated: true,
            };
            const res = _isReadOnlyEditor(entity, user);

            expect(res).toBeFalsy();
        });
    });
});
