/* @flow */

import EntityAPI from './entity';
import LocaleAPI from './locale';
import L10nAPI from './l10n';
import TranslationAPI from './translation';
import UserAPI from './user';

import * as types from './types';


export default {
    entity: new EntityAPI(),
    locale: new LocaleAPI(),
    l10n: new L10nAPI(),
    translation: new TranslationAPI(),
    user: new UserAPI(),
    types,
};
