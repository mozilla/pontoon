import { combineReducers } from 'redux';
import { connectRouter } from 'connected-react-router';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import * as lightbox from 'core/lightbox';
import * as locale from 'core/locale';
import * as l10n from 'core/l10n';
import * as notification from 'core/notification';
import * as plural from 'core/plural';
import * as project from 'core/project';
import * as resource from 'core/resource';
import * as stats from 'core/stats';
import * as term from 'core/term';
import * as user from 'core/user';
import * as batchactions from 'modules/batchactions';
import * as history from 'modules/history';
import * as machinery from 'modules/machinery';
import * as otherlocales from 'modules/otherlocales';
import * as search from 'modules/search';
import * as teamcomments from 'modules/teamcomments';
import * as unsavedchanges from 'modules/unsavedchanges';

// Combine reducers from all modules, using their NAME constant as key.
export default (browserHistory: any): any =>
    combineReducers({
        // System modules
        router: connectRouter(browserHistory),
        // Core modules
        [editor.NAME]: editor.reducer,
        [entities.NAME]: entities.reducer,
        [lightbox.NAME]: lightbox.reducer,
        [locale.NAME]: locale.reducer,
        [l10n.NAME]: l10n.reducer,
        [notification.NAME]: notification.reducer,
        [plural.NAME]: plural.reducer,
        [project.NAME]: project.reducer,
        [resource.NAME]: resource.reducer,
        [stats.NAME]: stats.reducer,
        [user.NAME]: user.reducer,
        // Application modules
        [batchactions.NAME]: batchactions.reducer,
        [history.NAME]: history.reducer,
        [machinery.NAME]: machinery.reducer,
        [otherlocales.NAME]: otherlocales.reducer,
        [search.NAME]: search.reducer,
        [teamcomments.NAME]: teamcomments.reducer,
        [term.NAME]: term.reducer,
        [unsavedchanges.NAME]: unsavedchanges.reducer,
    });
