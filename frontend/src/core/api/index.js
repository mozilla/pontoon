/* @flow */

import EntityAPI from './entity';
import LocaleAPI from './locale';
import L10nAPI from './l10n';
import MachineryAPI from './machinery';
import ProjectAPI from './project';
import ResourceAPI from './resource';
import TranslationAPI from './translation';
import UserAPI from './user';


export type {
    Entities,
    Entity,
    EntityTranslation,
    MachineryTranslation,
    OtherLocaleTranslation,
} from './types';


export default {
    entity: new EntityAPI(),
    locale: new LocaleAPI(),
    l10n: new L10nAPI(),
    machinery: new MachineryAPI(),
    project: new ProjectAPI(),
    resource: new ResourceAPI(),
    translation: new TranslationAPI(),
    user: new UserAPI(),
};
