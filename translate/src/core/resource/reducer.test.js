import reducer from './reducer';
import { RECEIVE, UPDATE } from './actions';

describe('reducer', () => {
    const RESOURCES = [
        {
            path: 'path/to.file',
            approvedStrings: 1,
            stringsWithWarnings: 1,
            totalStrings: 2,
        },
    ];
    const ALL_RESOURCES = {
        path: [],
        approvedStrings: 1,
        stringsWithWarnings: 1,
        totalStrings: 2,
    };

    it('returns the initial state', () => {
        const res = reducer(undefined, {});

        const expected = {
            resources: [],
            allResources: {
                path: 'all-resources',
                approvedStrings: 0,
                stringsWithWarnings: 0,
                totalStrings: 0,
            },
        };

        expect(res).toEqual(expected);
    });

    it('handles the RECEIVE action', () => {
        const res = reducer(
            {},
            {
                type: RECEIVE,
                resources: RESOURCES,
                allResources: ALL_RESOURCES,
            },
        );

        const expected = {
            resources: RESOURCES,
            allResources: ALL_RESOURCES,
        };

        expect(res).toEqual(expected);
    });

    it('handles the UPDATE action', () => {
        const UPDATED_RESOURCES = [
            {
                path: 'path/to.file',
                approvedStrings: 2,
                stringsWithWarnings: 0,
                totalStrings: 2,
            },
        ];
        const UPDATED_ALL_RESOURCES = {
            path: [],
            approvedStrings: 2,
            stringsWithWarnings: 0,
            totalStrings: 2,
        };

        const res = reducer(
            {
                resources: RESOURCES,
                allResources: ALL_RESOURCES,
            },
            {
                type: UPDATE,
                resourcePath: 'path/to.file',
                approvedStrings: 2,
                stringsWithWarnings: 0,
            },
        );

        const expected = {
            resources: UPDATED_RESOURCES,
            allResources: UPDATED_ALL_RESOURCES,
        };

        expect(res).toEqual(expected);
    });
});
