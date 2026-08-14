import type { EntityTranslation } from '~/api/translation';
import type { MessageEntry } from '.';
import { getMessageEntryFormat } from './getMessageEntryFormat';
import type { Entity } from '~/api/entity';

export function messageEntryFromTranslation(
  translation: EntityTranslation,
  entity: Entity,
): MessageEntry;
export function messageEntryFromTranslation(
  translation: EntityTranslation,
  format: string,
  id?: string,
): MessageEntry;
export function messageEntryFromTranslation(
  { value, properties }: EntityTranslation,
  entityOrFormat: string | Entity,
  id: string = '',
): MessageEntry {
  let format;
  if (typeof entityOrFormat === 'string') {
    format = getMessageEntryFormat(entityOrFormat);
  } else {
    format = getMessageEntryFormat(entityOrFormat.format);
    id ||= entityOrFormat.key[0] ?? '';
  }

  if (format === 'fluent' && properties) {
    const attributes = new Map(Object.entries(properties));
    const value_ = Array.isArray(value) && value.length === 0 ? null : value;
    return { format, id, value: value_, attributes };
  }

  return { format, id, value };
}
