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
    sources: Array<{|
        type: string,
        url: string,
        title: string,
        count?: number,
    |}>,
    original: string,
    translation: string,
    quality?: number,
|};
