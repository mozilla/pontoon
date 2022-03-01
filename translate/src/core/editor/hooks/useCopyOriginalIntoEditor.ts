import { useSelectedEntity } from '~/core/entities/hooks';
import * as plural from '~/core/plural';
import { useAppSelector } from '~/hooks';

import useUpdateTranslation from './useUpdateTranslation';

/**
 * Return a function to copy the original translation into the editor.
 */
export default function useCopyOriginalIntoEditor(): () => void {
  const updateTranslation = useUpdateTranslation();

  const entity = useSelectedEntity();
  const pluralForm = useAppSelector((state) =>
    plural.selectors.getPluralForm(state),
  );

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
