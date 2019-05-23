import reducer from './reducer';
import { RECEIVE, UPDATE } from './actions';


describe('reducer', () => {
    const RESOURCES = [{
        path: 'path/to.file',
        approvedStrings: 1,
        stringsWithWarnings: 1,
        totalStrings: 2,
    }, {
        path: [],
        approvedStrings: 1,
        stringsWithWarnings: 1,
        totalStrings: 2,
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
            approvedStrings: 2,
            stringsWithWarnings: 0,
            totalStrings: 2,
        }, {
            path: [],
            approvedStrings: 2,
            stringsWithWarnings: 0,
            totalStrings: 2,
        }];

        const res = reducer(
            {
                resources: RESOURCES,
            },
            {
                type: UPDATE,
                resourcePath: 'path/to.file',
                approvedStrings: 2,
                stringsWithWarnings: 0,
            }
        );

        const expected = {
            resources: UPDATED_RESOURCES,
        };

        expect(res).toEqual(expected);
    });
});
