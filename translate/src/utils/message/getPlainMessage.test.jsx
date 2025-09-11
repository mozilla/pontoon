import { getPlainMessage } from './getPlainMessage';
import { parseEntry } from './parseEntry';
import { serializeEntry } from './serializeEntry';
import {describe,it,expect} from "vitest";
describe('getPlainMessage', () => {
  describe('Fluent', () => {
    it('works for an empty string', () => {
      expect(getPlainMessage('', 'fluent')).toEqual('');
    });

    it('works for a null value', () => {
      expect(getPlainMessage(null, 'fluent')).toEqual('');
    });

    it('works for a non-FTL string', () => {
      expect(getPlainMessage('I am inevitable', 'fluent')).toEqual(
        'I am inevitable',
      );
    });

    it('returns the value for a simple Message', () => {
      const message = 'title = Marvel Cinematic Universe';
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('Marvel Cinematic Universe');
    });

    it('returns the value for a multiline Message', () => {
      const message = `summary =
            Heroes
            beat
            the Villain
        `;
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('Heroes\nbeat\nthe Villain');
    });

    it('returns the value for a simple Term', () => {
      const message = '-team-name = Avengers';
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('Avengers');
    });

    it('returns an empty string for an empty literal value in a message', () => {
      const entry = parseEntry('fluent', 'empty = { "" }\n');
      serializeEntry('fluent', entry);
      const res = getPlainMessage(entry, 'fluent');
      expect(res).toEqual('');
    });

    it('returns an empty string for an empty literal value in a term', () => {
      const entry = parseEntry('fluent', '-empty = { "" }\n');
      serializeEntry(entry);
      const res = getPlainMessage(entry, 'fluent');
      expect(res).toEqual('');
    });

    it('returns the attribute when there are no values and an attribute', () => {
      const message = `hawkeye =
            .real-name = Clint Barton
        `;
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('Clint Barton');
    });

    it('returns the value when there is a value and an attribute', () => {
      const message = `ironman-slogan = I am Ironman!
            .attributed-to = Tony Stark
        `;
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('I am Ironman!');
    });

    it('returns the first attribute when there are several', () => {
      const message = `thor =
            .first-movie = Thor
            .second-movie = The Dark World
            .third-movie = Ragnarok
        `;
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('Thor');
    });

    it('returns the default value for plurals 2', () => {
      const message = `key =
        { $number ->
            [1] Simple String
           *[other] Other Simple String
        }`;
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('Other Simple String');
    });

    it('returns the default value for Fluent plural', () => {
      const message = `stones-number =
            Thanos has { $number ->
                [0] no Stones
                [1] 1 Stone
                [6] all the Stones
               *[other] { $number } Stones
            }
        `;
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('Thanos has { $number } Stones');
    });

    it('returns the default value for Fluent selector', () => {
      const message = `who-dies =
            { $who ->
                [female] Black Widow
                [male] Hawkeye
               *[other] Everyone
           } will die
        `;
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('Everyone will die');
    });

    it('returns the default value for a selector in an attribute', () => {
      const message = `ironman =
            .talking-ia = { PLATFORM() ->
                [win] Friday
               *[other] Jarvis
            }
        `;
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('Jarvis');
    });

    it('works with function reference', () => {
      const message = `explore = {
            LINK("Wikipedia", title: "Go to Wikipedia")
        }Read more
        `;
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual(
        '{ LINK("Wikipedia", title: "Go to Wikipedia") }Read more',
      );
    });

    it('works with variable reference', () => {
      const message = 'big-green = { $hulk }';
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('{ $hulk }');
    });

    it('works with message reference', () => {
      const message = 'small-white = { banner }';
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('{ banner }');
    });

    it('works with message reference with attribute', () => {
      const message = 'hero = { ironman.name }';
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('{ ironman.name }');
    });

    it('works with term reference', () => {
      const message = 'team = { -team-name }';
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('{ -team-name }');
    });

    it('works with string literals', () => {
      const message = 'the-end = { "" }'; // #nospoil
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('');
    });

    it('works with number literals', () => {
      const message = 'movies = { 22 }';
      const res = getPlainMessage(message, 'fluent');
      expect(res).toEqual('{ 22 }');
    });
  });

  describe('Unicode MessageFormat', () => {
    it('works for an MF2 string', () => {
      expect(getPlainMessage('{{quoted pattern}}', 'gettext')).toEqual(
        'quoted pattern',
      );
    });

    it('returns the default value for MF2 plural', () => {
      const message = `
      .input {$number :number}
      .match $number
      0 {{Thanos has no Stones}}
      1 {{Thanos has 1 Stone}}
      6 {{Thanos has all the Stones}}
      * {{Thanos has \\{number\\} Stones}}`;
      const res = getPlainMessage(message, 'gettext');
      expect(res).toEqual('Thanos has {number} Stones');
    });
  });
});
