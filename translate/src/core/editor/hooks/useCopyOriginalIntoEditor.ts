import { useSelectedEntity } from '~/core/entities/hooks';
import { usePluralForm } from '~/context/PluralForm';

import { useUpdateTranslation } from './useUpdateTranslation';

/**
 * Return a function to copy the original translation into the editor.
 */
export function useCopyOriginalIntoEditor(): () => void {
  const updateTranslation = useUpdateTranslation();

  const entity = useSelectedEntity();
  const { pluralForm } = usePluralForm(entity);

  return () => {
    if (entity) {
      if (pluralForm === -1 || pluralForm === 0) {
        updateTranslation(entity.original, 'original');
      } else {
        updateTranslation(entity.original_plural, 'original');
      }
    }
  };
}
