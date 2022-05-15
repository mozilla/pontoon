import * as entities from '~/core/entities/reducer';
import * as notification from '~/core/notification/reducer';
import * as project from '~/core/project/reducer';
import * as resource from '~/core/resource/reducer';
import * as stats from '~/core/stats/reducer';
import * as term from '~/core/term/reducer';
import * as user from '~/core/user/reducer';
import * as batchactions from '~/modules/batchactions/reducer';
import * as history from '~/modules/history/reducer';
import * as otherlocales from '~/modules/otherlocales/reducer';
import * as search from '~/modules/search/reducer';
import * as teamcomments from '~/modules/teamcomments/reducer';

// Combine reducers from all modules, using their NAME constant as key.
export const reducer = {
  // Core modules
  [entities.ENTITIES]: entities.reducer,
  [notification.NOTIFICATION]: notification.reducer,
  [project.PROJECT]: project.reducer,
  [resource.RESOURCE]: resource.reducer,
  [stats.STATS]: stats.reducer,
  [user.USER]: user.reducer,
  // Application modules
  [batchactions.BATCHACTIONS]: batchactions.reducer,
  [history.HISTORY]: history.reducer,
  [otherlocales.OTHERLOCALES]: otherlocales.reducer,
  [search.SEARCH]: search.reducer,
  [teamcomments.TEAM_COMMENTS]: teamcomments.reducer,
  [term.TERM]: term.reducer,
};
