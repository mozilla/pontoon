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
    if (translation) {
      const { status } = translation;
      if (
        status === 'approved' ||
        status === 'pretranslated' ||
        status === 'fuzzy'
      ) {
        if (translation.errors.length) {
          return 'errors';
        } else if (translation.warnings.length) {
          return 'warnings';
        } else if (status === 'approved') {
          return 'approved';
        } else if (status === 'pretranslated') {
          return 'pretranslated';
        }
      }
    }
    return 'missing';
  }, [translation]);
}
