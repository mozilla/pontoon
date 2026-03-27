import type { Entity } from '~/api/entity';
import { parseEntry } from '~/utils/message/parseEntry';

/**
 * Return a string identifier for the given entity, suitable for use in an
 * LLM prompt.
 *
 * For Fluent entities, the identifier includes the attribute name or "value"
 * to help the LLM infer context:
 *   - `message-id.value`        — entity has a value
 *   - `message-id.attr-name`    — entity doesn't have a value but has an attribute
 *
 * For all other formats, returns the first key element as-is.
 *
 * Returns `undefined` if no key is available.
 */
export function getEntityStringId(entity: Entity): string | undefined {
  const id = entity.key[0];
  if (!id) {
    return undefined;
  }

  if (entity.format !== 'fluent') {
    return id;
  }

  const parsed = parseEntry('fluent', entity.machinery_original);
  if (!parsed) {
    return id;
  }

  if (parsed.value) {
    return `${id}.value`;
  }

  if (parsed.attributes) {
    const firstAttrName = parsed.attributes.keys().next().value;
    if (firstAttrName) {
      return `${id}.${firstAttrName}`;
    }
  }

  return id;
}
