import type { Entity } from '~/api/entity';
import type { Locale } from '~/context/Locale';
import type { MessageEntry } from '.';
import { getEmptyMessageEntry } from './getEmptyMessage';
import { getMessageEntryFormat } from './getMessageEntryFormat';
import { messageEntryFromTranslation } from './fromTranslation';
import { createMessageEntry } from './createMessageEntry';

export function messageEntryFromEntity(entity: Entity): MessageEntry {
  const format = getMessageEntryFormat(entity.format);
  const id = entity.key[0] ?? '';
  return createMessageEntry(format, id, entity.value, entity.properties);
}

export function messageEntryFromEntityTranslation(
  entity: Entity,
): MessageEntry | null;
export function messageEntryFromEntityTranslation(
  entity: Entity,
  locale: Locale,
): MessageEntry;
export function messageEntryFromEntityTranslation(
  entity: Entity,
  locale?: Locale,
): MessageEntry | null {
  const { translation } = entity;

  if (!translation || translation.status === 'rejected') {
    if (!locale) {
      return null;
    }
    const orig = messageEntryFromEntity(entity);
    return getEmptyMessageEntry(orig, locale);
  }

  return messageEntryFromTranslation(translation, entity);
}
