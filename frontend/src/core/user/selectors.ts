import { createSelector } from 'reselect';

import { NAME as LOCALE_NAME } from 'core/locale';
import { NAME as PROJECT_NAME } from 'core/project';

import { NAME } from '.';

import { LocaleState } from 'core/locale';
import { ProjectState } from 'core/project';
import { UserState } from 'core/user';

const userSelector = (state): UserState => state[NAME];
const localeSelector = (state): LocaleState => state[LOCALE_NAME];
const projectSelector = (state): ProjectState => state[PROJECT_NAME];

export function _isTranslator(
    user: UserState,
    locale: LocaleState,
    project: ProjectState,
): boolean {
    const localeProject = locale.code + '-' + project.slug;

    if (!user.isAuthenticated) {
        return false;
    }

    if (user.managerForLocales.indexOf(locale.code) !== -1) {
        return true;
    }

    if (
        Object.prototype.hasOwnProperty.call(
            user.translatorForProjects,
            localeProject,
        )
    ) {
        return user.translatorForProjects[localeProject];
    }

    return user.translatorForLocales.indexOf(locale.code) !== -1;
}

/**
 * Return true if the user has translator permission for the current project
 * and locale.
 */
export const isTranslator: (...args: Array<any>) => any = createSelector(
    userSelector,
    localeSelector,
    projectSelector,
    _isTranslator,
);

export default {
    isTranslator,
};
