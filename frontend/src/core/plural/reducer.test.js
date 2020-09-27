import reducer from './reducer';
import { RESET, SELECT } from './actions';

describe('reducer', () => {
    it('returns the initial state', () => {
        const res = reducer(undefined, {});
        const expected = {
            pluralForm: -1,
        };
        expect(res).toEqual(expected);
    });

    it('handles the SELECT action', () => {
        const res = reducer({}, { type: SELECT, pluralForm: 2 });
        expect(res).toEqual({ pluralForm: 2 });
    });

    it('handles the RESET action', () => {
        const res = reducer({}, { type: RESET });
        expect(res).toEqual({ pluralForm: -1 });
    });
});
