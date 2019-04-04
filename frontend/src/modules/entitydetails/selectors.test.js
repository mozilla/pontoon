import {
    _getTranslationForSelectedEntity,
    _isReadOnlyEditor,
} from './selectors';


describe('selectors', () => {
    describe('getTranslationForSelectedEntity', () => {
        const entities = [
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

        it('returns the correct string', () => {
            const entity = entities[0];
            const res = _getTranslationForSelectedEntity(entity, -1);

            expect(res).toEqual('world');
        });

        it('does not return rejected translations', () => {
            const entity = entities[1];
            const res = _getTranslationForSelectedEntity(entity, -1);

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
