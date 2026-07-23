import type { Message } from '@mozilla/l10n';
import type { Entity } from '~/api/entity';
import type { Locale } from '~/context/Locale';
import type { MessageEntry } from '.';
import { getEmptyMessageEntry } from './getEmptyMessage';
import { getMessageEntryFormat } from './getMessageEntryFormat';
import { messageEntryFromTranslation } from './fromTranslation';

/**
 * Build a {@link MessageEntry} from a `(value, properties)` data model, the JSON
 * shape entities and composed Machinery suggestions are delivered in — no
 * source string to parse.
 */
export function messageEntryFromValue(
  format: MessageEntry['format'],
  id: string,
  value: Message,
  properties?: Record<string, Message>,
): MessageEntry {
  if (format === 'fluent' && properties) {
    const attributes = new Map(Object.entries(properties));
    const value_ = Array.isArray(value) && value.length === 0 ? null : value;
    return { format, id, value: value_, attributes };
  } else {
    return { format, id, value };
  }
}

export function messageEntryFromEntity(entity: Entity): MessageEntry {
  const format = getMessageEntryFormat(entity.format);
  const id = entity.key[0] ?? '';
  return messageEntryFromValue(format, id, entity.value, entity.properties);
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
