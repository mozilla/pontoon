import { describe, expect, it } from 'vitest';

import { getPlainMessage } from './getPlainMessage';
import { parseEntry } from './parseEntry';
import type { MessageEntry } from '.';

describe('getPlainMessage', () => {
  describe('Fluent', () => {
    it('works for an empty pattern', () => {
      expect(getPlainMessage({ format: 'fluent', id: '', value: [] })).toEqual(
        '',
      );
    });

    it('returns the value for a simple Message', () => {
      const entry = parseEntry('fluent', 'title = Marvel Cinematic Universe')!;
      const res = getPlainMessage(entry);
      expect(res).toEqual('Marvel Cinematic Universe');
    });

    it('returns the value for a multiline Message', () => {
      const entry = parseEntry(
        'fluent',
        `summary =
            Heroes
            beat
            the Villain
        `,
      )!;
      const res = getPlainMessage(entry);
      expect(res).toEqual('Heroes\nbeat\nthe Villain');
    });

    it('returns the value for a simple Term', () => {
      const entry = parseEntry('fluent', '-team-name = Avengers')!;
      const res = getPlainMessage(entry);
      expect(res).toEqual('Avengers');
    });

    it('returns an empty string for an empty literal value in a message', () => {
      const entry = parseEntry('fluent', 'empty = { "" }\n')!;
      expect(getPlainMessage(entry)).toEqual('');
    });

    it('returns an empty string for an empty literal value in a term', () => {
      const entry = parseEntry('fluent', '-empty = { "" }\n')!;
      expect(getPlainMessage(entry)).toEqual('');
    });

    it('returns the attribute when there are no values and an attribute', () => {
      const entry = parseEntry(
        'fluent',
        `hawkeye =
            .real-name = Clint Barton
        `,
      )!;
      expect(getPlainMessage(entry)).toEqual('Clint Barton');
    });

    it('returns the value when there is a value and an attribute', () => {
      const entry = parseEntry(
        'fluent',
        `ironman-slogan = I am Ironman!
            .attributed-to = Tony Stark
        `,
      )!;
      expect(getPlainMessage(entry)).toEqual('I am Ironman!');
    });

    it('returns the first attribute when there are several', () => {
      const entry = parseEntry(
        'fluent',
        `thor =
            .first-movie = Thor
            .second-movie = The Dark World
            .third-movie = Ragnarok
        `,
      )!;
      expect(getPlainMessage(entry)).toEqual('Thor');
    });

    it('returns the default value for plurals 2', () => {
      const entry = parseEntry(
        'fluent',
        `key =
        { $number ->
            [1] Simple String
           *[other] Other Simple String
        }`,
      )!;
      expect(getPlainMessage(entry)).toEqual('Other Simple String');
    });

    it('returns the default value for Fluent plural', () => {
      const entry = parseEntry(
        'fluent',
        `stones-number =
            Thanos has { $number ->
                [0] no Stones
                [1] 1 Stone
                [6] all the Stones
               *[other] { $number } Stones
            }
        `,
      )!;
      expect(getPlainMessage(entry)).toEqual('Thanos has { $number } Stones');
    });

    it('returns the default value for Fluent selector', () => {
      const entry = parseEntry(
        'fluent',
        `who-dies =
            { $who ->
                [female] Black Widow
                [male] Hawkeye
               *[other] Everyone
           } will die
        `,
      )!;
      expect(getPlainMessage(entry)).toEqual('Everyone will die');
    });

    it('returns the default value for a selector in an attribute', () => {
      const entry = parseEntry(
        'fluent',
        `ironman =
            .talking-ia = { PLATFORM() ->
                [win] Friday
               *[other] Jarvis
            }
        `,
      )!;
      expect(getPlainMessage(entry)).toEqual('Jarvis');
    });

    it('works with function reference', () => {
      const entry = parseEntry(
        'fluent',
        `explore = {
            LINK("Wikipedia", title: "Go to Wikipedia")
        }Read more
        `,
      )!;
      expect(getPlainMessage(entry)).toEqual(
        '{ LINK("Wikipedia", title: "Go to Wikipedia") }Read more',
      );
    });

    it('works with variable reference', () => {
      const entry = parseEntry('fluent', 'big-green = { $hulk }')!;
      expect(getPlainMessage(entry)).toEqual('{ $hulk }');
    });

    it('works with message reference', () => {
      const entry = parseEntry('fluent', 'small-white = { banner }')!;
      expect(getPlainMessage(entry)).toEqual('{ banner }');
    });

    it('works with message reference with attribute', () => {
      const entry = parseEntry('fluent', 'hero = { ironman.name }')!;
      expect(getPlainMessage(entry)).toEqual('{ ironman.name }');
    });

    it('works with term reference', () => {
      const entry = parseEntry('fluent', 'team = { -team-name }')!;
      expect(getPlainMessage(entry)).toEqual('{ -team-name }');
    });

    it('works with string literals', () => {
      const entry = parseEntry('fluent', 'the-end = { "" }')!;
      expect(getPlainMessage(entry)).toEqual('');
    });

    it('works with number literals', () => {
      const entry = parseEntry('fluent', 'movies = { 22 }')!;
      expect(getPlainMessage(entry)).toEqual('{ 22 }');
    });
  });

  describe('Unicode MessageFormat', () => {
    it('works for an MF2 string', () => {
      const entry = parseEntry('webext', '{{quoted pattern}}')!;
      expect(getPlainMessage(entry)).toEqual('quoted pattern');
    });

    it('returns the default value for MF2 plural', () => {
      const message = `
      .input {$number :number}
      .match $number
      0 {{Thanos has no Stones}}
      1 {{Thanos has 1 Stone}}
      6 {{Thanos has all the Stones}}
      * {{Thanos has \\{number\\} Stones}}`;
      const entry = parseEntry('webext', message)!;
      expect(getPlainMessage(entry)).toEqual('Thanos has {number} Stones');
    });

    it('strips Android <xliff:g> wrappers', () => {
      const message =
        '{$vendor :xliff:g id=vendor example=Xiaomi @translate=no @source=|%1$s|} additional settings';
      const entry = parseEntry('android', message)!;
      expect(getPlainMessage(entry)).toEqual('%1$s additional settings');
    });

    it('message entry value with MF2 placeholder fallback', () => {
      const entry: MessageEntry = {
        format: 'android',
        id: '',
        value: ['a = ', { $: 'b' }],
      };
      expect(getPlainMessage(entry)).toEqual('a = {$b}');
    });

    it('open/close tags', () => {
      const message =
        'Go to {#a href=open-account}Create password{/a} in settings.';
      const entry = parseEntry('android', message)!;
      expect(getPlainMessage(entry)).toEqual(
        'Go to <a href="open-account">Create password</a> in settings.',
      );
    });
  });
});
