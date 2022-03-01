import { ReactLocalization } from '@fluent/react';

import reducer from './reducer';
import { RECEIVE, REQUEST } from './actions';

describe('reducer', () => {
    it('returns the initial state', () => {
        const res = reducer(undefined, {});
        const expected = {
            fetching: false,
            localization: new ReactLocalization([]),
        };
        expect(res).toEqual(expected);
    });

    it('handles the REQUEST action', () => {
        const res = reducer({}, { type: REQUEST });
        expect(res.fetching).toEqual(true);
    });

    it('handles the RECEIVE action', () => {
        const initial = {
            fetching: true,
            localization: new ReactLocalization([]),
        };
        const localization = new ReactLocalization([]);

        const res = reducer(initial, { type: RECEIVE, localization });

        const expected = {
            fetching: false,
            localization,
        };
        expect(res).toEqual(expected);
    });
});
