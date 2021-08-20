/**
 * Accepted Translation of an Entity, cannot exist outside of the Entity type.
 */
export type EntityTranslation = {
    readonly pk: number;
    readonly string: string | null | undefined;
    readonly approved: boolean;
    readonly fuzzy: boolean;
    readonly rejected: boolean;
    readonly errors: Array<string>;
    readonly warnings: Array<string>;
};

/**
 * Comments pertaining to a translation.
 */
export type TranslationComment = {
    readonly author: string;
    readonly username: string;
    readonly userGravatarUrlSmall: string;
    readonly createdAt: string;
    readonly dateIso: string;
    readonly content: string;
    readonly pinned: boolean;
    readonly id: number;
};

/**
 * Alias to be used for comments pertaining to a Locale
 */
export type TeamComment = TranslationComment;

/**
 * All users for use in mentions suggestions within comments
 */
export type UsersList = {
    gravatar: string;
    name: string;
    url: string;
};

/**
 * Term entry with translation.
 */
export type TermType = {
    readonly text: string;
    readonly partOfSpeech: string;
    readonly definition: string;
    readonly usage: string;
    readonly translation: string;
    readonly entityId: number;
};

/**
 * String that needs to be translated, along with its current metadata,
 * and its currently accepted translations.
 */
export type Entity = {
    readonly pk: number;
    readonly original: string;
    readonly original_plural: string;
    readonly machinery_original: string;
    readonly comment: string;
    readonly group_comment: string;
    readonly resource_comment: string;
    readonly key: string;
    readonly context: string;
    readonly format: string;
    readonly path: string;
    readonly project: Record<string, any>;
    readonly source: Array<Array<string>> | Record<string, any>;
    readonly translation: Array<EntityTranslation>;
    readonly readonly: boolean;
};

/**
 * List of Entity objects.
 */
export type Entities = Array<Entity>;

/*
 * A collection of translations of an entity to a locale other than
 * the currently selected locale.
 */
export type OtherLocaleTranslations = Array<OtherLocaleTranslation>;

/*
 * Translation of an entity in a locale other than the currently selected locale.
 */
export type OtherLocaleTranslation = {
    readonly locale: {
        readonly code: string;
        readonly name: string;
        readonly pk: number;
        readonly direction: string;
        readonly script: string;
    };
    readonly translation: string;
    readonly is_preferred: boolean | null | undefined;
};

/*
 * Translation that comes from a machine (Machine Translation,
 * Translation Memory... ).
 */
export type SourceType =
    | 'concordance-search'
    | 'translation-memory'
    | 'google-translate'
    | 'microsoft-translator'
    | 'systran-translate'
    | 'microsoft-terminology'
    | 'caighdean';
export type MachineryTranslation = {
    sources: Array<SourceType>;
    itemCount?: number;
    original: string;
    translation: string;
    quality?: number;
    projectNames?: Array<string | null | undefined>;
};
