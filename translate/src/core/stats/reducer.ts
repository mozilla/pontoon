import { UPDATE_STATS } from './actions';

import type { Action, Stats } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const STATS = 'stats';

const initial: Stats = {
  approved: 0,
  pretranslated: 0,
  warnings: 0,
  errors: 0,
  missing: 0,
  unreviewed: 0,
  total: 0,
};

export function reducer(state: Stats = initial, action: Action): Stats {
  switch (action.type) {
    case UPDATE_STATS:
      return {
        ...action.stats,
      };
    default:
      return state;
  }
}
