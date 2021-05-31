export const UPDATE: 'stats/UPDATE' = 'stats/UPDATE';

export type APIStats = {
    approved: number;
    fuzzy: number;
    warnings: number;
    errors: number;
    unreviewed: number;
    total: number;
};

export type Stats = APIStats & {
    missing: number;
};

export type UpdateAction = {
    readonly type: typeof UPDATE;
    readonly stats: Stats;
};
export function update(stats: APIStats): UpdateAction {
    const newStats: Stats = {
        ...stats,
        missing:
            stats.total -
            stats.approved -
            stats.fuzzy -
            stats.errors -
            stats.warnings,
    };
    return {
        type: UPDATE,
        stats: newStats,
    };
}

export default {
    update,
};
