import { useAppSelector } from 'hooks';
import * as entities from 'core/entities';
import * as plural from 'core/plural';

import useUpdateTranslation from './useUpdateTranslation';

/**
 * Return a function to copy the original translation into the editor.
 */
export default function useCopyOriginalIntoEditor(): () => void {
    const updateTranslation = useUpdateTranslation();

    const entity = useAppSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );
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
