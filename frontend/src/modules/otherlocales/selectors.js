
/* @flow */

import { createSelector } from 'reselect';

import type { LocalesState } from '.';
import type { UserState } from 'core/user';


const otherLocalesSelector = (state): LocalesState => state.otherlocales;
const userSelector = (state): UserState => state.user;


export function _getOrderedOtherLocales(
    otherlocales: LocalesState,
    user: UserState,
): Array {
    const translations = otherlocales.translations;

    if (!user.isAuthenticated) {
        return translations;
    }

    const preferredLocales = user.preferredLocales.reverse();

    return translations.sort((a, b) => {
        let indexA = preferredLocales.indexOf(a.code);
        let indexB = preferredLocales.indexOf(b.code);

        if (indexA === -1 && indexB === -1) {
            return a > b;
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


export default {
    getOrderedOtherLocales,
};
