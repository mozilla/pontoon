/* @flow */

/**
 * Accepted Translation of an Entity, cannot exist outside of the Entity type.
 */
export type EntityTranslation = {|
    +pk: number,
    +string: ?string,
    +approved: boolean,
    +fuzzy: boolean,
    +rejected: boolean,
    +errors: Array<string>,
    +warnings: Array<string>,
|};


/**
 * String that needs to be translated, along with its current metadata,
 * and its currently accepted translations.
 */
export type Entity = {|
    +pk: number,
    +original: string,
    +original_plural: string,
    +machinery_original: string,
    +comment: string,
    +group_comment: string,
    +resource_comment: string,
    +key: string,
    +format: string,
    +path: string,
    +project: Object,
    +source: Array<Array<string>> | Object,
    +translation: Array<EntityTranslation>,
    +readonly: boolean,
|};


/**
 * List of Entity objects.
 */
export type Entities = Array<Entity>;


/*
 * Preferred and Other Translations of an entity in a locale other than
 * the currently selected locale.
 */
export type OtherLocaleTranslations = {|
    +preferred: Array<OtherLocaleTranslation>,
    +other: Array<OtherLocaleTranslation>,
|};


/*
 * Translation of an entity in a locale.
 */
export type OtherLocaleTranslation = {|
    +locale: {|
        +code: string,
        +name: string,
        +pk: number,
        +direction: string,
        +script: string,
    |},
    +translation: string,
|};


/*
 * Translation that comes from a machine (Machine Translation,
 * Translation Memory... ).
 */
type SourceType =
    | 'translation-memory'
    | 'google-translate'
    | 'microsoft-translator'
    | 'microsoft-terminology'
    | 'transvision'
    | 'caighdean'
;

export type MachineryTranslation = {|
    sources: Array<SourceType>,
    itemCount?: number,
    original: string,
    translation: string,
    quality?: number,
|};
