import {
    _getTranslationForSelectedEntity,
    _isReadOnlyEditor,
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
