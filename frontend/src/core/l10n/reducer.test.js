import reducer from './reducer';
import { RECEIVE, REQUEST } from './actions';


describe('reducer', () => {
    it('returns the initial state', () => {
        const res = reducer(undefined, {});
        const expected = {
            fetching: false,
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
            bundles: [ { messages: ['hello'] } ],
        }
        const bundle = { messages: ['world'] };

        const res = reducer(initial, { type: RECEIVE, bundle });

        const expected = {
            fetching: false,
            bundles: [ { messages: ['hello'] }, bundle ],
        };
        expect(res).toEqual(expected);
    });
});
