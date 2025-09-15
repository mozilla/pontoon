import { requiresSourceView } from './requiresSourceView';
import { parseEntry } from './parseEntry';

describe('requiresSourceEditor', () => {
  const expTrue = [
    `my-entry =
      { NUMBER($totalHours) ->
          [one] { $totalHours } hour
         *[other] { $totalHours } hours
      } is achievable in just over { NUMBER($periodMonths) ->
          [one] { $periodMonths } month
         *[other] { $periodMonths } months
      } if { NUMBER($people) ->
          [one] { $people } person
         *[other] { $people } people
      } record { NUMBER($clipsPerDay) ->
          [one] { $clipsPerDay } clip
         *[other] { $clipsPerDay } clips
      } a day.`,
  ];
  for (const input of expTrue) {
    it(`returns true for ${JSON.stringify(input)}`, () => {
      const entry = parseEntry('fluent', input);
      expect(requiresSourceView(entry)).toEqual(true);
    });
  }

  const expFalse = [
    'my-entry = Hello!',
    `my-entry =
      Multi
      line
      value.`,
    'my-entry = Today is { DATETIME($date, month: "long", year: "numeric", day: "numeric") }',
    '-my-entry = Hello!',
    'my-entry = Term { -term } Reference',
    'my-entry = { my_id }',
    'my-entry = { my_id.title }',
    'my-entry = { "" }',
    'my-entry = { 5 }',
    'my-entry = \n    .an-atribute = Hello!',
    'my-entry = World\n    .an-atribute = Hello!',
    `my-entry =
    .an-atribute = Hello!
    .another-atribute = World!`,
    `my-entry =
      { PLATFORM() ->
          [variant] Hello!
        *[another-variant] World!
      }`,
    `my-entry =
      .label =
          { PLATFORM() ->
              [macos] Choose
             *[other] Browse
          }
      .accesskey =
          { PLATFORM() ->
              [macos] e
             *[other] o
          }`,
    `my-entry =
      There { $num ->
          [one] is one email
         *[other] are many emails
      } for { $gender ->
         *[masculine] him
          [feminine] her
      }`,
    `my-entry =
      { $gender ->
         *[masculine]
              { $num ->
                  [one] There is one email for him
                 *[other] There are many emails for him
              }
          [feminine]
              { $num ->
                  [one] There is one email for her
                 *[other] There are many emails for her
              }
      }`,
  ];
  for (const input of expFalse) {
    it(`returns false for ${JSON.stringify(input)}`, () => {
      const entry = parseEntry('fluent', input);
      expect(requiresSourceView(entry)).toEqual(false);
    });
  }
});
