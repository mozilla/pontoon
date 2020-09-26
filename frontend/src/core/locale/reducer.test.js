import reducer from './reducer';
import { RECEIVE, REQUEST } from './actions';

describe('reducer', () => {
    it('returns the initial state', () => {
        const res = reducer(undefined, {});
        const expected = {
            code: '',
            name: '',
            cldrPlurals: [],
            pluralRule: '',
            direction: '',
            script: '',
            googleTranslateCode: '',
            msTranslatorCode: '',
            systranTranslateCode: '',
            msTerminologyCode: '',
            transvision: false,
            localizations: [],
            fetching: false,
        };
        expect(res).toEqual(expected);
    });

    it('handles the REQUEST action', () => {
        const res = reducer({}, { type: REQUEST });
        expect(res.fetching).toEqual(true);
    });

    it('handles the RECEIVE action', () => {
        const LOCALE = { code: 'kg' };
        const res = reducer({}, { type: RECEIVE, locale: LOCALE });
        const expected = {
            ...LOCALE,
            fetching: false,
        };
        expect(res).toEqual(expected);
    });
});
