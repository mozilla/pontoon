import ftl from '@fluent/dedent';

import { parseEntry } from './parseEntry';

describe('parseEntry', () => {
  it('flattens values surrounding a select expression and select expression variants', () => {
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
    const entry = parseEntry(input);
    expect(entry).toEqual({
      id: 'my-entry',
      value: {
        type: 'select',
        declarations: [
          {
            type: 'input',
            name: 'num',
            value: {
              type: 'expression',
              arg: { type: 'variable', name: 'num' },
              functionRef: { type: 'function', name: 'number' },
            },
          },
          {
            type: 'input',
            name: 'gender',
            value: {
              type: 'expression',
              arg: { type: 'variable', name: 'gender' },
              functionRef: { type: 'function', name: 'string' },
            },
          },
        ],
        selectors: [
          { type: 'variable', name: 'num' },
          { type: 'variable', name: 'gender' },
        ],
        variants: [
          {
            keys: [
              { type: 'literal', value: 'one' },
              { type: '*', value: 'masculine' },
            ],
            value: ['There is one email for { $awesome } him'],
          },
          {
            keys: [
              { type: 'literal', value: 'one' },
              { type: 'literal', value: 'feminine' },
            ],
            value: ['There is one email for { $awesome } her'],
          },
          {
            keys: [
              { type: '*', value: 'other' },
              { type: '*', value: 'masculine' },
            ],
            value: ['There are { $num } emails for { $awesome } him'],
          },
          {
            keys: [
              { type: '*', value: 'other' },
              { type: 'literal', value: 'feminine' },
            ],
            value: ['There are { $num } emails for { $awesome } her'],
          },
        ],
      },
    });
  });
});
