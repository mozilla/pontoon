import { requiresSourceView } from './requiresSourceView';
import { parseEntry } from './parseEntry';

describe('requiresSourceEditor', () => {
  it('returns true for a string with no value', () => {
    const input = 'my-entry =';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(true);
  });

  it('returns true for a missing brace', () => {
    const input = 'my-entry = { $foo';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(true);
  });

  it('returns true for a missing brace in an attribute', () => {
    const input = 'my-entry = foo\n  .attr = { $bar';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(true);
  });

  it('returns false for a string with simple value', () => {
    const input = 'my-entry = Hello!';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with multiline value', () => {
    const input = `
my-entry =
    Multi
    line
    value.`;
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with a reference to a built-in function', () => {
    const input =
      'my-entry = Today is { DATETIME($date, month: "long", year: "numeric", day: "numeric") }';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with a Term', () => {
    const input = '-my-entry = Hello!';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with a TermReference', () => {
    const input = 'my-entry = Term { -term } Reference';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with a MessageReference', () => {
    const input = 'my-entry = { my_id }';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with a MessageReference with attribute', () => {
    const input = 'my-entry = { my_id.title }';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with a StringExpression', () => {
    const input = 'my-entry = { "" }';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with a NumberExpression', () => {
    const input = 'my-entry = { 5 }';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with a single simple attribute', () => {
    const input = 'my-entry = \n    .an-atribute = Hello!';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with value and attributes', () => {
    const input = 'my-entry = World\n    .an-atribute = Hello!';
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with no value and two attributes', () => {
    const input = `
my-entry =
    .an-atribute = Hello!
    .another-atribute = World!`;
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with a select expression', () => {
    const input = `
my-entry =
    { PLATFORM() ->
        [variant] Hello!
       *[another-variant] World!
    }`;
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with a double select expression in attribute', () => {
    const input = `
my-entry =
    .label =
        { PLATFORM() ->
            [macos] Choose
           *[other] Browse
        }
    .accesskey =
        { PLATFORM() ->
            [macos] e
           *[other] o
        }`;
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with multiple select expressions and surrounding text', () => {
    const input = `
my-entry =
    There { $num ->
        [one] is one email
       *[other] are many emails
    } for { $gender ->
       *[masculine] him
        [feminine] her
    }`;
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns false for a string with nested select expressions', () => {
    const input = `
my-entry =
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
    }`;
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(false);
  });

  it('returns true for a string with excessive select expressions', () => {
    const input = `
my-entry =
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
    } a day.
`;
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(true);
  });

  it('returns true for a string with an unsupported selector', () => {
    const input = `
my-entry =
    { FOO() ->
        [foo] FOO
       *[other] BAR
    }`;
    const message = parseEntry(input);

    expect(requiresSourceView(message)).toEqual(true);
  });
});
