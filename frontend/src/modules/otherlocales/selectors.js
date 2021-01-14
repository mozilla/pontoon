/* @flow */

import { createSelector } from 'reselect';

import type { OtherLocaleTranslation, OtherLocaleTranslations } from 'core/api';

import { NAME } from '.';

const otherLocalesSelector = (state): string => state[NAME].translations;

/**
 * Return the Entity that follows the current one in the list.
 */

function _flattenOtherLocales(
    otherLocales: OtherLocaleTranslations,
): Array<OtherLocaleTranslation> {
    if (!otherLocales) {
        return [];
    }

    let result = [];
    if (otherLocales.preferred) {
        otherLocales.preferred.forEach((translation) => {
            result.push(translation);
        });
    }

    if (otherLocales.other) {
        otherLocales.other.forEach((translation) => {
            result.push(translation);
        });
    }

    return result;
}

/**
 * Return the Entity that preceeds the current one in the list.
 */
export const getTranslationsFlatList: Function = createSelector(
    otherLocalesSelector,
    _flattenOtherLocales,
);

export default {
    getTranslationsFlatList,
};
