/* @flow */

import EntityAPI from './entity';
import FilterAPI from './filter';
import LocaleAPI from './locale';
import L10nAPI from './l10n';
import MachineryAPI from './machinery';
import ProjectAPI from './project';
import ResourceAPI from './resource';
import TranslationAPI from './translation';
import UserAPI from './user';
import CommentAPI from './comment';

export type {
    Entities,
    Entity,
    EntityTranslation,
    TranslationComment,
    TeamComment,
    TermType,
    TextType,
    MentionType,
    InitialType,
    UsersList,
    MachineryTranslation,
    OtherLocaleTranslations,
    OtherLocaleTranslation,
    SourceType,
} from './types';

export default {
    entity: (new EntityAPI(): EntityAPI),
    comment: (new CommentAPI(): CommentAPI),
    filter: (new FilterAPI(): FilterAPI),
    locale: (new LocaleAPI(): LocaleAPI),
    l10n: (new L10nAPI(): L10nAPI),
    machinery: (new MachineryAPI(): MachineryAPI),
    project: (new ProjectAPI(): ProjectAPI),
    resource: (new ResourceAPI(): ResourceAPI),
    translation: (new TranslationAPI(): TranslationAPI),
    user: (new UserAPI(): UserAPI),
};
