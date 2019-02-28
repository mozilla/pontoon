/* @flow */

import { createSelector } from 'reselect';

import * as user from 'core/user';
import * as otherlocales from 'modules/otherlocales';

import api from 'core/api';

import type { LocalesState } from '.';
import type { UserState } from 'core/user';


const otherLocalesSelector = (state): LocalesState => state[otherlocales.NAME];
const userSelector = (state): UserState => state[user.NAME];


export function _getOrderedOtherLocales(
    otherlocales: LocalesState,
    user: UserState,
): Array<api.types.OtherLocaleTranslation> {
    const translations = otherlocales.translations;

    if (!user.isAuthenticated) {
        return translations;
    }

    const preferredLocales = user.preferredLocales.reverse();

    return translations.sort((a, b) => {
        let indexA = preferredLocales.indexOf(a.code);
        let indexB = preferredLocales.indexOf(b.code);

        if (indexA === -1 && indexB === -1) {
            return a.code > b.code ? 1 : 0;
        }
        else if (indexA < indexB) {
            return 1;
        }
        else if (indexA > indexB) {
            return -1;
        }
        else {
            return 0;
        }
    });
}


/**
 * Returns ordered list of locales. The list starts with user's prefered
 * locales (if any) in order as they are defined. The remaining locales
 * follow in the given (alphabetic) order.
 */
export const getOrderedOtherLocales: Function = createSelector(
    otherLocalesSelector,
    userSelector,
    _getOrderedOtherLocales
);


export function _getPreferredLocalesCount(
    otherlocales: LocalesState,
    user: UserState,
): number {
    if (!user.isAuthenticated) {
        return 0;
    }

    return otherlocales.translations.reduce((count, item) => {
        if (user.preferredLocales.indexOf(item.code) > -1) {
            return count + 1;
        }
        return count;
    }, 0);
}


/**
 * Return number of user's prefered locales in the list of given translations
 * from other locales.
 */
export const getPreferredLocalesCount: Function = createSelector(
    otherLocalesSelector,
    userSelector,
    _getPreferredLocalesCount
);


export default {
    getOrderedOtherLocales,
    getPreferredLocalesCount,
};
