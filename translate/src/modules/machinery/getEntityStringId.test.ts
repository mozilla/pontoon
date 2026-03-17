import { getEntityStringId } from './getEntityStringId';
import type { Entity } from '~/api/entity';

function makeEntity(overrides: Partial<Entity>): Entity {
  return {
    pk: 1,
    key: [],
    original: '',
    machinery_original: '',
    comment: '',
    group_comment: '',
    resource_comment: '',
    meta: [],
    format: '',
    path: '',
    project: {},
    translation: undefined,
    readonly: false,
    isSibling: false,
    date_created: '',
    ...overrides,
  };
}

describe('getEntityStringId', () => {
  it('returns undefined when entity has no key', () => {
    const entity = makeEntity({ key: [] });
    expect(getEntityStringId(entity)).toBeUndefined();
  });

  it('returns the key as-is for non-Fluent formats', () => {
    const entity = makeEntity({ key: ['my-string'], format: 'gettext' });
    expect(getEntityStringId(entity)).toBe('my-string');
  });

  it('returns key for Fluent entity when source does not parse', () => {
    const entity = makeEntity({
      key: ['msg-id'],
      format: 'fluent',
      machinery_original: 'not valid ftl !!!',
    });
    expect(getEntityStringId(entity)).toBe('msg-id');
  });

  it('appends .value for a Fluent entity with a value', () => {
    const entity = makeEntity({
      key: ['msg-id'],
      format: 'fluent',
      machinery_original: 'msg-id = Hello\n',
    });
    expect(getEntityStringId(entity)).toBe('msg-id.value');
  });

  it('appends the attribute name for a Fluent entity with only attributes', () => {
    const entity = makeEntity({
      key: ['msg-id'],
      format: 'fluent',
      machinery_original: 'msg-id =\n    .aria-label = Close\n',
    });
    expect(getEntityStringId(entity)).toBe('msg-id.aria-label');
  });

  it('prefers value over attributes when a Fluent entity has both', () => {
    const entity = makeEntity({
      key: ['msg-id'],
      format: 'fluent',
      machinery_original: 'msg-id = Hello\n    .aria-label = Close\n',
    });
    expect(getEntityStringId(entity)).toBe('msg-id.value');
  });
});
