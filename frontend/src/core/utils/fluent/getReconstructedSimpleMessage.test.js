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
        expect(res).toEqual('spoilers =\n    .who-dies = Qui meurt ?');
    });

    it('returns indented content for a multiline simple message', () => {
        const original = 'time-travel = They discovered Time Travel';
        const translation = 'Ils ont inventé le\nvoyage temporel';
        const res = getReconstructedSimpleMessage(original, translation);
        expect(res).toEqual('time-travel =\n    Ils ont inventé le\n    voyage temporel');
    });

    it('returns indented content for a multiline single attribute', () => {
        const original = 'slow-walks =\n    .title = They walk in slow motion';
        const translation = 'Ils se déplacent\nen mouvement lents';
        const res = getReconstructedSimpleMessage(original, translation);
        expect(res).toEqual('slow-walks =\n    .title =\n        Ils se déplacent\n        en mouvement lents');
    });

    it('adds the leading dash to the id of Term messages', () => {
        const original = '-my-term = My Term';
        const translation = 'Mon Terme';
        const res = getReconstructedSimpleMessage(original, translation);
        expect(res).toEqual('-my-term = Mon Terme');
    });
});
