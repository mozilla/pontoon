/* @flow */

import { default as TranslationAPI } from './translation';
import { default as EntityAPI } from './entity';


export default {
    entity: new EntityAPI(),
    translation: new TranslationAPI(),
}
