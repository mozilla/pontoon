import { describe, expect, it } from 'vitest';

import { keysToCamelCase } from './keysToCamelCase';

describe('keysToCamelCase', () => {
  it('renames snake_case keys, recursively', () => {
    expect(
      keysToCamelCase([{ user_name: 'a', comments: [{ date_iso: 'b' }] }]),
    ).toEqual([{ userName: 'a', comments: [{ dateIso: 'b' }] }]);
  });

  it('leaves the message data model alone', () => {
    const value = [
      { $: 'date', fn: 'shortdate', attr: { 'fluent-fn': 'SHORTDATE' } },
    ];
    const properties = { 'my-attr': [{ $: 'my-var' }] };
    const res = keysToCamelCase([{ approved_date: 'x', value, properties }]);
    expect(res).toEqual([{ approvedDate: 'x', value, properties }]);
  });
});
