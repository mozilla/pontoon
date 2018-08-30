/* @flow */

import { actions as entitiesActions } from 'modules/entitieslist';


export function suggest(
    entity: number,
    translation: string,
    locale: string,
    original: string,
) {
    return async (dispatch: Function): Promise<void> => {
        // Fetch entities from backend.
        const url = new URL('/update/', window.location.origin);
        const payload = new URLSearchParams();
        payload.append('entity', entity.toString());
        payload.append('translation', translation);
        payload.append('locale', locale);
        payload.append('plural_form', '0');
        payload.append('original', original);

        // Get the CSRF value.
        let csrfToken = '';
        const rootElt = document.getElementById('root');
        if (rootElt) {
            csrfToken = rootElt.dataset.csrfToken;
        }
        payload.append('csrfmiddlewaretoken', csrfToken);

        const headers = new Headers();
        headers.append('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
        headers.append('X-Requested-With', 'XMLHttpRequest');
        headers.append('X-CSRFToken', csrfToken);

        const requestParams = {
            method: 'POST',
            credentials: 'same-origin',
            headers: headers,
            body: payload,
        };

        const response = await fetch(url, requestParams);
        const content = await response.json();

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
