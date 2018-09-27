/* @flow */

import EntityAPI from './entity';
import LocaleAPI from './locale';
import TranslationAPI from './translation';
import UserAPI from './user';


export default {
    entity: new EntityAPI(),
    locale: new LocaleAPI(),
    translation: new TranslationAPI(),
    user: new UserAPI(),
};
