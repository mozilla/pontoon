import reducer from './reducer';
import { RECEIVE, UPDATE } from './actions';


describe('reducer', () => {
    const RESOURCES = [{
        path: 'path/to.file',
        approved_strings: 1,
        strings_with_warnings: 1,
        total_strings: 2,
    }, {
        path: [],
        approved_strings: 1,
        strings_with_warnings: 1,
        total_strings: 2,
    }];

    it('returns the initial state', () => {
        const res = reducer(undefined, {});

        const expected = {
            resources: [],
        }

        expect(res).toEqual(expected);
    });

    it('handles the RECEIVE action', () => {
        const res = reducer(
            {},
            {
                type: RECEIVE,
                resources: RESOURCES,
            }
        );

        const expected = {
            resources: RESOURCES,
        };

        expect(res).toEqual(expected);
    });

    it('handles the UPDATE action', () => {
        const UPDATED_RESOURCES = [{
            path: 'path/to.file',
            approved_strings: 2,
            strings_with_warnings: 0,
            total_strings: 2,
        }, {
            path: [],
            approved_strings: 2,
            strings_with_warnings: 0,
            total_strings: 2,
        }];

        const res = reducer(
            {
                resources: RESOURCES,
            },
            {
                type: UPDATE,
                resource_path: 'path/to.file',
                approved_strings: 2,
                strings_with_warnings: 0,
            }
        );

        const expected = {
            resources: UPDATED_RESOURCES,
        };

        expect(res).toEqual(expected);
    });
});
