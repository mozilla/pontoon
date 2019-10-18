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
    +comment: string,
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
        title: {
            string: string,
            id: string,
        },
        count?: number,
    |}>,
    original: string,
    translation: string,
    quality?: number,
|};
