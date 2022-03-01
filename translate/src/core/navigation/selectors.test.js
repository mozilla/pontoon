import { getNavigationParams } from './selectors';

describe('selectors', () => {
    describe('getNavigationParams', () => {
        it('correctly parses the pathname', () => {
            const pathname = '/kg/waterwolf/path/to/RESOURCE.po/';
            const search = '';

            const fakeState = {
                router: {
                    location: {
                        pathname,
                        search,
                    },
                },
            };
            const res = getNavigationParams(fakeState);

            expect(res.locale).toEqual('kg');
            expect(res.project).toEqual('waterwolf');
            expect(res.resource).toEqual('path/to/RESOURCE.po');
        });

        it('correctly parses the query string', () => {
            const pathname = '/kg/waterwolf/path/';
            const search = '?string=42';

            const fakeState = {
                router: {
                    location: {
                        pathname,
                        search,
                    },
                },
            };
            const res = getNavigationParams(fakeState);

            expect(res.entity).toEqual(42);
        });
    });
});
