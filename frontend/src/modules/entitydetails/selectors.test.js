import {
    _getTranslationForSelectedEntity,
    _isReadOnlyEditor,
} from './selectors';


describe('selectors', () => {
    const entities = [
        {
            pk: 1,
            readonly: false,
            translation: [
                {
                    string: 'hello',
                },
            ],
        },
        {
            pk: 2,
            readonly: true,
            translation: [
                {
                    string: 'world',
                },
            ],
        },
        {
            pk: 3,
            readonly: false,
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
            const navigation = {
                entity: 1,
            };
            const user = {
                isAuthenticated: false,
            };
            const res = _isReadOnlyEditor(entities, navigation, user);

            expect(res).toBeTruthy();
        });

        it('returns true if entity read-only', () => {
            const navigation = {
                entity: 2,
            };
            const user = {
                isAuthenticated: true,
            };
            const res = _isReadOnlyEditor(entities, navigation, user);

            expect(res).toBeTruthy();
        });

        it('returns false if entity not read-only and user authenticated', () => {
            const navigation = {
                entity: 1,
            };
            const user = {
                isAuthenticated: true,
            };
            const res = _isReadOnlyEditor(entities, navigation, user);

            expect(res).toBeFalsy();
        });
    });
});
