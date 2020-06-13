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
    entity: new EntityAPI(),
    comment: new CommentAPI(),
    filter: new FilterAPI(),
    locale: new LocaleAPI(),
    l10n: new L10nAPI(),
    machinery: new MachineryAPI(),
    project: new ProjectAPI(),
    resource: new ResourceAPI(),
    translation: new TranslationAPI(),
    user: new UserAPI(),
};
