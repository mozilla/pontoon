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


/*
 * Translation that comes from a machine (Machine Translation,
 * Translation Memory... ).
 */
export type MachineryTranslation = {|
    source: string,
    url: string,
    title: string,
    original: string,
    translation: string,
    quality?: string,
    count?: number,
|};
