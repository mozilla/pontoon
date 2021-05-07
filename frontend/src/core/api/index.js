/* @flow */

import CommentAPI from './comment';
import EntityAPI from './entity';
import FilterAPI from './filter';
import L10nAPI from './l10n';
import LocaleAPI from './locale';
import MachineryAPI from './machinery';
import ProjectAPI from './project';
import ResourceAPI from './resource';
import TranslationAPI from './translation';
import UserAPI from './user';
import UxActionAPI from './uxaction';

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
    comment: (new CommentAPI(): CommentAPI),
    entity: (new EntityAPI(): EntityAPI),
    filter: (new FilterAPI(): FilterAPI),
    l10n: (new L10nAPI(): L10nAPI),
    locale: (new LocaleAPI(): LocaleAPI),
    machinery: (new MachineryAPI(): MachineryAPI),
    project: (new ProjectAPI(): ProjectAPI),
    resource: (new ResourceAPI(): ResourceAPI),
    translation: (new TranslationAPI(): TranslationAPI),
    user: (new UserAPI(): UserAPI),
    uxaction: (new UxActionAPI(): UxActionAPI),
};
