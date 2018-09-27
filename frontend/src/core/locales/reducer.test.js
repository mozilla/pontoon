import reducer from './reducer';
import { RECEIVE, REQUEST } from './actions';


describe('reducer', () => {
    it('returns the initial state', () => {
        const res = reducer(undefined, {});
        const expected = {
            fetching: false,
            locales: {},
        }
        expect(res).toEqual(expected);
    });

    it('handles the REQUEST action', () => {
        const res = reducer({}, { type: REQUEST });
        expect(res.fetching).toEqual(true);
    });

    it('handles the RECEIVE action', () => {
        const LOCALES = { 'kg': { code: 'kg' } };
        const res = reducer({}, { type: RECEIVE, locales: LOCALES });
        const expected = {
            fetching: false,
            locales: LOCALES,
        };
        expect(res).toEqual(expected);
    });
});
