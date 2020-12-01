/* @flow */

import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';

import * as entities from 'core/entities';
import * as plural from 'core/plural';

import { actions } from '..';
import useUpdateTranslation from './useUpdateTranslation';

/**
 * Hook to update the editor content whenever the entity changes.
 */
export default function useLoadTranslation() {
    const dispatch = useDispatch();

    const updateTranslation = useUpdateTranslation();

    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );
    const pluralForm = useSelector((state) =>
        plural.selectors.getPluralForm(state),
    );
    const activeTranslationString = useSelector((state) =>
        plural.selectors.getTranslationStringForSelectedEntity(state),
    );

    React.useEffect(() => {
        dispatch(actions.setInitialTranslation(activeTranslationString));
        updateTranslation(activeTranslationString, 'entities-list');
    }, [
        entity,
        pluralForm,
        activeTranslationString,
        updateTranslation,
        dispatch,
    ]);
}
