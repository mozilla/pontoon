import type { Entity, EntityTranslation } from '~/core/api';
import { useAppSelector } from '~/hooks';

/**
 * Return the plural form to use for the given entity.
 *
 * If the entity has a plural form, and the current plural form is -1,
 * this will correctly return 0 instead of -1. In all other cases, return
 * the plural form as stored in the state.
 */
export function usePluralForm(entity: Entity | undefined): number {
  const pf = useAppSelector((state) => state.plural.pluralForm);
  return pf === -1 && entity?.original_plural ? 0 : pf;
}

/**
 * Return the active translation for the given entity and current plural form.
 *
 * The active translation is either the approved one, the fuzzy one, or the
 * most recent non-rejected one.
 */
export function useTranslationForEntity(
  entity: Entity | undefined,
): EntityTranslation | undefined {
  let pf = usePluralForm(entity);
  if (pf === -1) pf = 0;
  const tx = entity?.translation[pf];
  return tx && !tx.rejected ? tx : undefined;
}
