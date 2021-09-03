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
    UsersList,
    MachineryTranslation,
    OtherLocaleTranslations,
    OtherLocaleTranslation,
    SourceType,
} from './types';

export default {
    comment: new CommentAPI() as CommentAPI,
    entity: new EntityAPI() as EntityAPI,
    filter: new FilterAPI() as FilterAPI,
    l10n: new L10nAPI() as L10nAPI,
    locale: new LocaleAPI() as LocaleAPI,
    machinery: new MachineryAPI() as MachineryAPI,
    project: new ProjectAPI() as ProjectAPI,
    resource: new ResourceAPI() as ResourceAPI,
    translation: new TranslationAPI() as TranslationAPI,
    user: new UserAPI() as UserAPI,
    uxaction: new UxActionAPI() as UxActionAPI,
};
