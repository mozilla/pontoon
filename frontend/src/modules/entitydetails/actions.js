/* @flow */

import api from 'core/api';

import { actions as entitiesActions } from 'modules/entitieslist';


export function suggest(
    entity: number,
    translation: string,
    locale: string,
    original: string,
): Function {
    return async dispatch => {
        const content = await api.translation.updateTranslation(
            entity,
            translation,
            locale,
            '0',  // plural_form
            original,
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
                    content.translation
                )
            );
        }
    }
}

export default {
    suggest,
};
