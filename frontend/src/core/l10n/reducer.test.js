import reducer from './reducer';
import { RECEIVE, REQUEST, SELECT_LOCALES } from './actions';


describe('reducer', () => {
    it('returns the initial state', () => {
        const res = reducer(undefined, {});
        const expected = {
            fetching: false,
            locales: [],
            bundles: [],
        }
        expect(res).toEqual(expected);
    });

    it('handles the REQUEST action', () => {
        const res = reducer({}, { type: REQUEST });
        expect(res.fetching).toEqual(true);
    });

    it('handles the RECEIVE action', () => {
        const initial = {
            fetching: true,
            locales: [],
            bundles: [ { messages: ['hello'] } ],
        }
        const bundles = [ { messages: ['world'] } ];

        const res = reducer(initial, { type: RECEIVE, bundles });

        const expected = {
            fetching: false,
            locales: [],
            bundles,
        };
        expect(res).toEqual(expected);
    });

    it('handles the SELECT_LOCALES action', () => {
        const initial = {
            fetching: true,
            locales: [],
            bundles: [],
        }
        const locales = [ 'kg', 'gn' ];

        const res = reducer(initial, { type: SELECT_LOCALES, locales });

        const expected = {
            fetching: true,
            locales,
            bundles: [],
        };
        expect(res).toEqual(expected);
    });
});
