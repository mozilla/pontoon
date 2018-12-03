/* @flow */

/*
 * Translation of an entity in a locale other than the currently selected.
 */
export type OtherLocaleTranslation = {|
    +code: string,
    +locale: string,
    +direction: string,
    +script: string,
    +translation: string,
|};
