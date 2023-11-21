import * as entities from '~/modules/entities/reducer';
import * as entitieslist from '~/modules/entitieslist/reducer';
import * as project from '~/modules/project/reducer';
import * as resource from '~/modules/resource/reducer';
import * as stats from '~/modules/stats/reducer';
import * as term from '~/modules/terms/reducer';
import * as user from '~/modules/user/reducer';
import * as batchactions from '~/modules/batchactions/reducer';
import * as otherlocales from '~/modules/otherlocales/reducer';
import * as search from '~/modules/search/reducer';
import * as teamcomments from '~/modules/teamcomments/reducer';

// Combine reducers from all modules, using their NAME constant as key.
export const reducer = {
  [entities.ENTITIES]: entities.reducer,
  [entitieslist.ENTITIESLIST]: entitieslist.reducer,
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
