/* @flow */

import { createSelector } from 'reselect';

import * as navigation from 'core/navigation';

import { NAME } from '.';

import type { Navigation } from 'core/navigation';
import type { Locale, LocalesState } from '.';


const localesSelector = (state): LocalesState => state[NAME].locales;


export function _getCurrentLocaleData(
    locales: LocalesState,
    parameters: Navigation
): ?Locale {
    if (locales && parameters.locale && locales[parameters.locale]) {
        return locales[parameters.locale];
    }
    return null;
}


/**
 * Return metadata about the currently selected locale.
 */
export const getCurrentLocaleData: Function = createSelector(
    localesSelector,
    navigation.selectors.getNavigation,
    _getCurrentLocaleData
);


export default {
    getCurrentLocaleData,
};
