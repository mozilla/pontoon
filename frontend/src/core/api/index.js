/* @flow */

import TranslationAPI from './translation';
import EntityAPI from './entity';


export default {
    entity: new EntityAPI(),
    translation: new TranslationAPI(),
}
