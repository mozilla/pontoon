import getReconstructedSimpleMessage from './getReconstructedSimpleMessage';


describe('getReconstructedSimpleMessage', () => {
    it('returns the correct value for a simple message', () => {
        const original = 'title = Marvel Cinematic Universe';
        const translation = 'Univers cinématographique Marvel';
        const res = getReconstructedSimpleMessage(original, translation);
        expect(res).toEqual('title = Univers cinématographique Marvel');
    });

    it('returns the correct value for a single attribute', () => {
        const original = 'spoilers =\n    .who-dies = Who dies?';
        const translation = 'Qui meurt ?';
        const res = getReconstructedSimpleMessage(original, translation);
        expect(res).toEqual('spoilers =\n\t.who-dies = Qui meurt ?');
    });
});
