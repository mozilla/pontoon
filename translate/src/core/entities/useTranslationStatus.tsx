import { useMemo } from 'react';
import { Entity } from '~/api/entity';

type TranslationStatus =
  | 'errors'
  | 'warnings'
  | 'approved'
  | 'pretranslated'
  | 'partial'
  | 'missing';

export function useTranslationStatus({
  translation,
}: Entity): TranslationStatus {
  return useMemo(() => {
    let errors = false;
    let warnings = false;
    let approved = 0;
    let pretranslated = 0;

    for (const tx of translation) {
      if (tx.approved || tx.pretranslated || tx.fuzzy) {
        if (tx.errors.length) {
          errors = true;
        } else if (tx.warnings.length) {
          warnings = true;
        } else if (tx.approved) {
          approved += 1;
        } else if (tx.pretranslated) {
          pretranslated += 1;
        }
      }
    }

    if (errors) {
      return 'errors';
    }
    if (warnings) {
      return 'warnings';
    }
    if (approved === translation.length) {
      return 'approved';
    }
    if (pretranslated === translation.length) {
      return 'pretranslated';
    }
    if (approved > 0 || pretranslated > 0) {
      return 'partial';
    }
    return 'missing';
  }, [translation]);
}
