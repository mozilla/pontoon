/* @flow */

import { UPDATE } from './actions';
import type { UpdateAction } from './actions';


type Action =
    | UpdateAction
;

export type UserState = {|
    +isAuthenticated: boolean,
    +id: string,
    +displayName: string,
    +email: string,
    +username: string,
    +managerForLocales: Array<string>,
    +translatorForLocales: Array<string>,
    +translatorForProjects: Array<string>,
|};


const initial: UserState = {
    isAuthenticated: false,
    id: '',
    displayName: '',
    email: '',
    username: '',
    managerForLocales: [],
    translatorForLocales: [],
    translatorForProjects: [],
};

export default function reducer(
    state: UserState = initial,
    action: Action,
): UserState {
    switch (action.type) {
        case UPDATE:
            return {
                isAuthenticated: action.data.is_authenticated,
                id: action.data.id,
                displayName: action.data.display_name,
                email: action.data.email,
                username: action.data.username,
                managerForLocales: action.data.manager_for_locales,
                translatorForLocales: action.data.translator_for_locales,
                translatorForProjects: action.data.translator_for_projects,
            };
        default:
            return state;
    }
}
