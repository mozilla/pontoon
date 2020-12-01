/* @flow */

import { useSelector } from 'react-redux';

import * as entities from 'core/entities';
import * as plural from 'core/plural';

import useUpdateTranslation from './useUpdateTranslation';

/**
 * Return a function to copy the original translation into the editor.
 */
export default function useCopyOriginalIntoEditor() {
    const updateTranslation = useUpdateTranslation();

    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );
    const pluralForm = useSelector((state) =>
        plural.selectors.getPluralForm(state),
    );

    return () => {
        if (entity) {
            if (pluralForm === -1 || pluralForm === 0) {
                updateTranslation(entity.original);
            } else {
                updateTranslation(entity.original_plural);
            }
        }
    };
}
