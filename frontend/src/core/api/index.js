/* @flow */

import EntityAPI from './entity';
import TranslationAPI from './translation';
import UserAPI from './user';


export default {
    entity: new EntityAPI(),
    translation: new TranslationAPI(),
    user: new UserAPI(),
};
