/* @flow */

import api from 'core/api';

import { actions as navActions } from 'core/navigation';
import { actions as entitiesActions } from 'modules/entitieslist';

import type { DbEntity } from 'modules/entitieslist';


export function sendTranslation(
    entity: number,
    translation: string,
    locale: string,
    original: string,
    pluralForm: number,
    forceSuggestions: boolean,
    nextEntity: ?DbEntity,
    router: Object,
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

            if (nextEntity && nextEntity.pk !== entity) {
                // The change did work, we want to move on to the next Entity.
                dispatch(navActions.updateEntity(router, nextEntity.pk.toString()));
            }
        }
    }
}

export default {
    sendTranslation,
};
