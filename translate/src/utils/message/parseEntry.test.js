import ftl from '@fluent/dedent';

import { parseEntry } from './parseEntry';

describe('parseEntry:fluent', () => {
  it('simple value', () => {
    const res = parseEntry('fluent', 'title = My Title');
    expect(res).toEqual({ format: 'fluent', id: 'title', value: ['My Title'] });
  });

  it('attribute', () => {
    const res = parseEntry('fluent', 'title =\n  .foo = Bar');
    expect(res).toEqual({
      format: 'fluent',
      id: 'title',
      value: null,
      attributes: new Map([['foo', ['Bar']]]),
    });
  });

  it('select expression', () => {
    const input = ftl`
      my-entry =
          { PLATFORM() ->
              [variant] Hello!
             *[another-variant] World!
          }
      `;
    const res = parseEntry('fluent', input);
    expect(res).toEqual({
      format: 'fluent',
      id: 'my-entry',
      value: {
        decl: { _1: { fn: 'platform' } },
        sel: ['_1'],
        alt: [
          { keys: ['variant'], pat: ['Hello!'] },
          { keys: [{ '*': 'another-variant' }], pat: ['World!'] },
        ],
      },
    });
  });

  it('placeholder in value', () => {
    const res = parseEntry('fluent', 'title = My { $awesome } Title');
    expect(res).toEqual({
      format: 'fluent',
      id: 'title',
      value: ['My { $awesome } Title'],
    });
  });

  it('placeholder in attribute', () => {
    const res = parseEntry('fluent', 'title =\n  .foo = Bar {-foo} Baz');
    expect(res).toEqual({
      format: 'fluent',
      id: 'title',
      value: null,
      attributes: new Map([['foo', ['Bar { -foo } Baz']]]),
    });
  });

  it('value and attributes', () => {
    const input = ftl`
      batman = The { $dark } Knight
          .weapon = Brain and { -wayne-enterprise }
          .history = Lost { 2 } parents, has { 1 } "$alfred"
      `;
    const res = parseEntry('fluent', input);
    expect(res).toEqual({
      format: 'fluent',
      id: 'batman',
      value: ['The { $dark } Knight'],
      attributes: new Map([
        ['weapon', ['Brain and { -wayne-enterprise }']],
        ['history', ['Lost { 2 } parents, has { 1 } "$alfred"']],
      ]),
    });
  });

  it('term', () => {
    const res = parseEntry(
      'fluent',
      '-term = My { $awesome } term\n .attr = { "" }',
    );
    expect(res).toEqual({
      format: 'fluent',
      id: '-term',
      value: ['My { $awesome } term'],
      attributes: new Map([['attr', ['']]]),
    });
  });

  it('multiple select expressions', () => {
    const input = ftl`
      my-entry =
          There { NUMBER($num) ->
              [one] is one email
             *[other] are { $num } emails
          } for { $awesome } { $gender ->
             *[masculine] him
              [feminine] her
          }
      `;
    const entry = parseEntry('fluent', input);
    expect(entry).toEqual({
      format: 'fluent',
      id: 'my-entry',
      value: {
        decl: {
          num_1: { $: 'num', fn: 'number' },
          gender: { $: 'gender', fn: 'string' },
        },
        sel: ['num_1', 'gender'],
        alt: [
          {
            keys: ['one', { '*': 'masculine' }],
            pat: ['There is one email for { $awesome } him'],
          },
          {
            keys: ['one', 'feminine'],
            pat: ['There is one email for { $awesome } her'],
          },
          {
            keys: [{ '*': 'other' }, { '*': 'masculine' }],
            pat: ['There are { $num } emails for { $awesome } him'],
          },
          {
            keys: [{ '*': 'other' }, 'feminine'],
            pat: ['There are { $num } emails for { $awesome } her'],
          },
        ],
      },
    });
  });
});
