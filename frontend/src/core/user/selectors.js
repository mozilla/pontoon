/* @flow */

import { createSelector } from 'reselect';

import * as navigation from 'core/navigation';

import { NAME } from '.';

import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';

const userSelector = (state): UserState => state[NAME];

export function _isTranslator(
    user: UserState,
    parameters: NavigationParams,
): boolean {
    const locale = parameters.locale;
    const project = parameters.project;
    const localeProject = locale + '-' + project;

    if (!user.isAuthenticated) {
        return false;
    }

    if (user.managerForLocales.indexOf(locale) !== -1) {
        return true;
    }

    if (user.translatorForProjects.hasOwnProperty(localeProject)) {
        return user.translatorForProjects[localeProject];
    }

    return user.translatorForLocales.indexOf(locale) !== -1;
}

/**
 * Return true if the user has translator permission for the current project
 * and locale.
 */
export const isTranslator: Function = createSelector(
    userSelector,
    navigation.selectors.getNavigationParams,
    _isTranslator,
);

export default {
    isTranslator,
};
