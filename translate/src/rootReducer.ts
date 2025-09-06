import * as entities from '../src/modules/entities/reducer';
import * as project from '../src/modules/project/reducer';
import * as resource from '../src/modules/resource/reducer';
import * as stats from '../src/modules/stats/reducer';
import * as term from '../src/modules/terms/reducer';
import * as user from '../src/modules/user/reducer';
import * as batchactions from '../src/modules/batchactions/reducer';
import * as otherlocales from '../src/modules/otherlocales/reducer';
import * as search from '../src/modules/search/reducer';
import * as teamcomments from '../src/modules/teamcomments/reducer';

// Combine reducers from all modules, using their NAME constant as key.
export const reducer = {
  [entities.ENTITIES]: entities.reducer,
  [project.PROJECT]: project.reducer,
  [resource.RESOURCE]: resource.reducer,
  [stats.STATS]: stats.reducer,
  [user.USER]: user.reducer,
  [batchactions.BATCHACTIONS]: batchactions.reducer,
  [otherlocales.OTHERLOCALES]: otherlocales.reducer,
  [search.SEARCH]: search.reducer,
  [teamcomments.TEAM_COMMENTS]: teamcomments.reducer,
  [term.TERM]: term.reducer,
};
