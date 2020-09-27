import getReconstructedMessage from './getReconstructedMessage';
import parser from './parser';
import serializer from './serializer';

describe('getReconstructedMessage', () => {
    it('returns the correct value for a simple message', () => {
        const original = 'title = Marvel Cinematic Universe';
        const translation = 'Univers cinématographique Marvel';
        const res = getReconstructedMessage(original, translation);
        const expected = parser.parseEntry(
            'title = Univers cinématographique Marvel',
        );
        expect(res).toEqual(expected);
    });

    it('returns the correct value for a single attribute', () => {
        const original = 'spoilers =\n    .who-dies = Who dies?';
        const translation = 'Qui meurt ?';
        const res = getReconstructedMessage(original, translation);
        const expected = parser.parseEntry(
            'spoilers =\n    .who-dies = Qui meurt ?',
        );
        expect(res).toEqual(expected);
    });

    it('returns indented content for a multiline simple message', () => {
        const original = 'time-travel = They discovered Time Travel';
        const translation = 'Ils ont inventé le\nvoyage temporel';
        const res = getReconstructedMessage(original, translation);
        const expected = parser.parseEntry(
            'time-travel =\n    Ils ont inventé le\n    voyage temporel',
        );
        expect(res).toEqual(expected);
    });

    it('returns indented content for a multiline single attribute', () => {
        const original = 'slow-walks =\n    .title = They walk in slow motion';
        const translation = 'Ils se déplacent\nen mouvement lents';
        const res = getReconstructedMessage(original, translation);
        const expected = parser.parseEntry(
            'slow-walks =\n    .title =\n        Ils se déplacent\n        en mouvement lents',
        );
        expect(res).toEqual(expected);
    });

    it('adds the leading dash to the id of Term messages', () => {
        const original = '-my-term = My Term';
        const translation = 'Mon Terme';
        const res = getReconstructedMessage(original, translation);
        const expected = parser.parseEntry('-my-term = Mon Terme');
        expect(res).toEqual(expected);
    });

    it('empties all but the first text element', () => {
        const original =
            'stark = Tony Stark\n    .hero = IronMan\n    .hair = black';
        const translation = 'Anthony Stark';
        const res = getReconstructedMessage(original, translation);

        expect(res.value.elements[0].value).toEqual('Anthony Stark');
        expect(res.attributes).toHaveLength(0);
    });

    it('does not duplicate terms in content', () => {
        const original = 'with-term = I am { -term }';
        const translation = 'Je suis { -term }';
        const res = getReconstructedMessage(original, translation);

        expect(serializer.serializeEntry(res)).toEqual(
            'with-term = Je suis { -term }\n',
        );
    });
});
