import type { APIStats } from '~/api/translation';

export const UPDATE_STATS = 'stats/UPDATE';

export type Stats = APIStats & {
  missing: number;
};

export type Action = UpdateAction;

type UpdateAction = {
  readonly type: typeof UPDATE_STATS;
  readonly stats: Stats;
};

export function updateStats(stats: APIStats): UpdateAction {
  const missing =
    stats.total -
    stats.approved -
    stats.pretranslated -
    stats.errors -
    stats.warnings;
  return {
    type: UPDATE_STATS,
    stats: { ...stats, missing },
  };
}
