import getSimplePreview from './getSimplePreview';

describe('getSimplePreview', () => {
    it('works for an empty string', () => {
        expect(getSimplePreview('')).toEqual('');
    });

    it('works for a null value', () => {
        expect(getSimplePreview(null)).toEqual('');
    });

    it('works for a non-FTL string', () => {
        expect(getSimplePreview('I am inevitable')).toEqual('I am inevitable');
    });

    it('returns the value for a simple Message', () => {
        const message = 'title = Marvel Cinematic Universe';
        const res = getSimplePreview(message);
        expect(res).toEqual('Marvel Cinematic Universe');
    });

    it('returns the value for a multiline Message', () => {
        const message = `summary =
            Heroes
            beat
            the Villain
        `;
        const res = getSimplePreview(message);
        expect(res).toEqual('Heroes\nbeat\nthe Villain');
    });

    it('returns the value for a simple Term', () => {
        const message = '-team-name = Avengers';
        const res = getSimplePreview(message);
        expect(res).toEqual('Avengers');
    });

    it('returns the attribute when there are no values and an attribute', () => {
        const message = `hawkeye =
            .real-name = Clint Barton
        `;
        const res = getSimplePreview(message);
        expect(res).toEqual('Clint Barton');
    });

    it('returns the value when there is a value and an attribute', () => {
        const message = `ironman-slogan = I am Ironman!
            .attributed-to = Tony Stark
        `;
        const res = getSimplePreview(message);
        expect(res).toEqual('I am Ironman!');
    });

    it('returns the first attribute when there are several', () => {
        const message = `thor =
            .first-movie = Thor
            .second-movie = The Dark World
            .third-movie = Ragnarok
        `;
        const res = getSimplePreview(message);
        expect(res).toEqual('Thor');
    });

    it('returns the default value for plurals 2', () => {
        const message = `key =
        { $number ->
            [1] Simple String
           *[other] Other Simple String
        }`;
        const res = getSimplePreview(message);
        expect(res).toEqual('Other Simple String');
    });

    it('returns the default value for plurals', () => {
        const message = `stones-number =
            Thanos has { $number ->
                [0] no Stones
                [1] 1 Stone
                [6] all the Stones
               *[other] { $number } Stones
            }
        `;
        const res = getSimplePreview(message);
        expect(res).toEqual('Thanos has { $number } Stones');
    });

    it('returns the default value for selectors', () => {
        const message = `who-dies =
            { $who ->
                [female] Black Widow
                [male] Hawkeye
               *[other] Everyone
           } will die
        `;
        const res = getSimplePreview(message);
        expect(res).toEqual('Everyone will die');
    });

    it('returns the default value for a selector in an attribute', () => {
        const message = `ironman =
            .talking-ia = { PLATFORM() ->
                [win] Friday
               *[other] Jarvis
            }
        `;
        const res = getSimplePreview(message);
        expect(res).toEqual('Jarvis');
    });

    it('works with function reference', () => {
        const message = `explore = {
            LINK("Wikipedia", title: "Go to Wikipedia")
        }Read more
        `;
        const res = getSimplePreview(message);
        expect(res).toEqual(
            '{ LINK("Wikipedia", title: "Go to Wikipedia") }Read more',
        );
    });

    it('works with variable reference', () => {
        const message = 'big-green = { $hulk }';
        const res = getSimplePreview(message);
        expect(res).toEqual('{ $hulk }');
    });

    it('works with message reference', () => {
        const message = 'small-white = { banner }';
        const res = getSimplePreview(message);
        expect(res).toEqual('{ banner }');
    });

    it('works with message reference with attribute', () => {
        const message = 'hero = { ironman.name }';
        const res = getSimplePreview(message);
        expect(res).toEqual('{ ironman.name }');
    });

    it('works with term reference', () => {
        const message = 'team = { -team-name }';
        const res = getSimplePreview(message);
        expect(res).toEqual('{ -team-name }');
    });

    it('works with string literals', () => {
        const message = 'the-end = { "" }'; // #nospoil
        const res = getSimplePreview(message);
        expect(res).toEqual('{ "" }');
    });

    it('works with number literals', () => {
        const message = 'movies = { 22 }';
        const res = getSimplePreview(message);
        expect(res).toEqual('{ 22 }');
    });
});
