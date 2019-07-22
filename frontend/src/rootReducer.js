/* @flow */

import { combineReducers } from 'redux';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import * as lightbox from 'core/lightbox';
import * as locales from 'core/locales';
import * as l10n from 'core/l10n';
import * as notification from 'core/notification';
import * as plural from 'core/plural';
import * as project from 'core/project';
import * as resource from 'core/resource';
import * as stats from 'core/stats';
import * as user from 'core/user';
import * as history from 'modules/history';
import * as machinery from 'modules/machinery';
import * as otherlocales from 'modules/otherlocales';
import * as unsavedchanges from 'modules/unsavedchanges';


// Combine reducers from all modules, using their NAME constant as key.
export default combineReducers({
    // Core modules
    [editor.NAME]: editor.reducer,
    [entities.NAME]: entities.reducer,
    [lightbox.NAME]: lightbox.reducer,
    [locales.NAME]: locales.reducer,
    [l10n.NAME]: l10n.reducer,
    [notification.NAME]: notification.reducer,
    [plural.NAME]: plural.reducer,
    [project.NAME]: project.reducer,
    [resource.NAME]: resource.reducer,
    [stats.NAME]: stats.reducer,
    [user.NAME]: user.reducer,
    // Application modules
    [history.NAME]: history.reducer,
    [machinery.NAME]: machinery.reducer,
    [otherlocales.NAME]: otherlocales.reducer,
    [unsavedchanges.NAME]: unsavedchanges.reducer,
});
