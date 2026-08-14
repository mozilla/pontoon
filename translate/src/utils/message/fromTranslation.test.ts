import { describe, expect, it } from 'vitest';
import type { Entity } from '~/api/entity';
import type { EntityTranslation } from '~/api/translation';
import { messageEntryFromTranslation } from './fromTranslation';

describe('messageEntryFromTranslation', () => {
  it('android entry', () => {
    const translation = { value: ['TRANS ', { $: 'x' }] } as EntityTranslation;
    expect(messageEntryFromTranslation(translation, 'android')).toEqual({
      format: 'android',
      id: '',
      value: ['TRANS ', { $: 'x' }],
    });
  });

  it('fluent translation with attributes', () => {
    const translation = {
      value: ['VALUE ', { $: 'x' }],
      properties: {
        a: ['ATTR A'],
        b: ['ATTR B'],
      },
    } as unknown as EntityTranslation;
    const exp = {
      format: 'fluent',
      id: '',
      value: ['VALUE ', { $: 'x' }],
      attributes: new Map([
        ['a', ['ATTR A']],
        ['b', ['ATTR B']],
      ]),
    };
    expect(messageEntryFromTranslation(translation, 'fluent')).toEqual(exp);
    expect(
      messageEntryFromTranslation(translation, {
        format: 'fluent',
        key: ['id'],
      } as Entity),
    ).toEqual({ ...exp, id: 'id' });
  });
});
