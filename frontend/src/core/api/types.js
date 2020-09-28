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
 * Comments pertaining to a translation.
 */
export type TranslationComment = {|
    +author: string,
    +username: string,
    +userGravatarUrlSmall: string,
    +createdAt: string,
    +dateIso: string,
    +content: string,
    +pinned: boolean,
    +id: number,
|};

/**
 * Alias to be used for comments pertaining to a Locale
 */
export type TeamComment = TranslationComment;

/**
 * Types used within Slate editor for comments
 */
export type TextType = {|
    text: string,
|};

export type MentionType = {|
    type: string,
    character: string,
    url: string,
    children: Array<TextType>,
|};

export type InitialType = {|
    type: string,
    children: Array<TextType>,
|};

/**
 * All users for use in mentions suggestions within comments
 */
export type UsersList = {|
    gravatar: string,
    name: string,
    url: string,
    display: string,
|};

/**
 * Term entry with translation.
 */
export type TermType = {|
    +text: string,
    +partOfSpeech: string,
    +definition: string,
    +usage: string,
    +translation: string,
    +entityId: number,
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
 * A collection of translations of an entity to a locale other than
 * the currently selected locale.
 */
export type OtherLocaleTranslations = {|
    +preferred: Array<OtherLocaleTranslation>,
    +other: Array<OtherLocaleTranslation>,
|};

/*
 * Translation of an entity in a locale other than the currently selected locale.
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
export type SourceType =
    | 'translation-memory'
    | 'google-translate'
    | 'microsoft-translator'
    | 'systran-translate'
    | 'microsoft-terminology'
    | 'transvision'
    | 'caighdean';

export type MachineryTranslation = {|
    sources: Array<SourceType>,
    itemCount?: number,
    original: string,
    translation: string,
    quality?: number,
|};
