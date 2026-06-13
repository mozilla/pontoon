import { describe, expect, it } from 'vitest';
import type { Entity } from '~/api/entity';
import type { Locale } from '~/context/Locale';
import {
  messageEntryFromEntity,
  messageEntryFromEntityTranslation,
} from './fromEntity';

describe('messageEntryFromEntity', () => {
  it('android entry', () => {
    const entity = {
      format: 'android',
      key: ['id'],
      value: ['VALUE ', { $: 'x' }],
      translation: { value: ['TRANS ', { $: 'x' }] },
    } as Entity;
    expect(messageEntryFromEntity(entity)).toEqual({
      format: 'android',
      id: 'id',
      value: ['VALUE ', { $: 'x' }],
    });
  });

  it('fluent entry with attributes', () => {
    const entity = {
      format: 'fluent',
      key: ['id'],
      value: ['VALUE ', { $: 'x' }],
      properties: { a: ['ATTR A'], b: ['ATTR B'] },
    } as unknown as Entity;
    expect(messageEntryFromEntity(entity)).toEqual({
      format: 'fluent',
      id: 'id',
      value: ['VALUE ', { $: 'x' }],
      attributes: new Map([
        ['a', ['ATTR A']],
        ['b', ['ATTR B']],
      ]),
    });
  });
});

describe('messageEntryFromEntityTranslation', () => {
  it('android entry with translation', () => {
    const entity = {
      format: 'android',
      key: ['id'],
      value: ['VALUE ', { $: 'x' }],
      translation: { status: 'approved', value: ['TRANS ', { $: 'x' }] },
    };
    const locale = { code: 'sl' } as Locale;

    expect(messageEntryFromEntityTranslation(entity as Entity)).toEqual({
      format: 'android',
      id: 'id',
      value: ['TRANS ', { $: 'x' }],
    });

    entity.translation.status = 'rejected';
    expect(messageEntryFromEntityTranslation(entity as Entity, locale)).toEqual(
      { format: 'android', id: 'id', value: [] },
    );
  });

  it('fluent entry with attributes and no translation', () => {
    const entity = {
      format: 'fluent',
      key: ['id'],
      value: ['VALUE ', { $: 'x' }],
      properties: { a: ['ATTR A'], b: ['ATTR B'] },
    } as unknown as Entity;
    const locale = { code: 'sl' } as Locale;
    expect(messageEntryFromEntityTranslation(entity)).toBeNull();
    expect(messageEntryFromEntityTranslation(entity, locale)).toEqual({
      format: 'fluent',
      id: 'id',
      value: [],
      attributes: new Map([
        ['a', []],
        ['b', []],
      ]),
    });
  });
});
