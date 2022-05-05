import * as editor from '~/core/editor';
import * as entities from '~/core/entities/reducer';
import * as notification from '~/core/notification';
import * as project from '~/core/project/reducer';
import * as resource from '~/core/resource/reducer';
import * as stats from '~/core/stats/reducer';
import * as term from '~/core/term';
import * as user from '~/core/user';
import * as batchactions from '~/modules/batchactions/reducer';
import * as history from '~/modules/history';
import * as machinery from '~/modules/machinery';
import * as otherlocales from '~/modules/otherlocales';
import * as search from '~/modules/search';
import * as teamcomments from '~/modules/teamcomments';
import * as unsavedchanges from '~/modules/unsavedchanges';

// Combine reducers from all modules, using their NAME constant as key.
export const reducer = {
  // Core modules
  [editor.NAME]: editor.reducer,
  [entities.NAME]: entities.reducer,
  [notification.NAME]: notification.reducer,
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
};
