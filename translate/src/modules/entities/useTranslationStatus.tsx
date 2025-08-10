import { useMemo } from 'react';
import { Entity } from '~/api/entity';

type TranslationStatus =
  | 'errors'
  | 'warnings'
  | 'approved'
  | 'pretranslated'
  | 'missing';

export function useTranslationStatus({
  translation,
}: Entity): TranslationStatus {
  return useMemo(() => {
    if (
      translation &&
      (translation.approved || translation.pretranslated || translation.fuzzy)
    ) {
      if (translation.errors.length) {
        return 'errors';
      } else if (translation.warnings.length) {
        return 'warnings';
      } else if (translation.approved) {
        return 'approved';
      } else if (translation.pretranslated) {
        return 'pretranslated';
      }
    }
    return 'missing';
  }, [translation]);
}
