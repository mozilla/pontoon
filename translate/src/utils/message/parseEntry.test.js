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
        declarations: [],
        selectors: [
          {
            type: 'expression',
            name: 'NUMBER',
            operand: { type: 'variable', name: 'num' },
          },
          { type: 'variable', name: 'gender' },
        ],
        variants: [
          {
            keys: [
              { type: 'nmtoken', value: 'one' },
              { type: 'nmtoken', value: 'feminine' },
            ],
            value: {
              body: [
                {
                  type: 'text',
                  value: 'There is one email for { $awesome } her',
                },
              ],
            },
          },
          {
            keys: [
              { type: 'nmtoken', value: 'one' },
              { type: '*', value: 'masculine' },
            ],
            value: {
              body: [
                {
                  type: 'text',
                  value: 'There is one email for { $awesome } him',
                },
              ],
            },
          },
          {
            keys: [
              { type: '*', value: 'other' },
              { type: 'nmtoken', value: 'feminine' },
            ],
            value: {
              body: [
                {
                  type: 'text',
                  value: 'There are { $num } emails for { $awesome } her',
                },
              ],
            },
          },
          {
            keys: [
              { type: '*', value: 'other' },
              { type: '*', value: 'masculine' },
            ],
            value: {
              body: [
                {
                  type: 'text',
                  value: 'There are { $num } emails for { $awesome } him',
                },
              ],
            },
          },
        ],
      },
    });
  });
});
