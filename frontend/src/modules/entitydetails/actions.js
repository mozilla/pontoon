/* @flow */

import api from 'core/api';

import { actions as entitiesActions } from 'modules/entitieslist';


export function sendTranslation(
    entity: number,
    translation: string,
    locale: string,
    original: string,
    pluralForm: number,
    forceSuggestions: boolean,
): Function {
    return async dispatch => {
        const content = await api.translation.updateTranslation(
            entity,
            translation,
            locale,
            pluralForm,
            original,
            forceSuggestions,
        );

        if (content.same) {
            // The translation that was provided is the same as an existing
            // translation for that entity.
            // Show an error.
            console.error('Same Translation Error');
        }
        else if (content.type === 'added' || content.type === 'updated') {
            dispatch(
                entitiesActions.updateEntityTranslation(
                    entity,
                    pluralForm,
                    content.translation
                )
            );
        }
    }
}

export default {
    sendTranslation,
};
