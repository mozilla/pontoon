import { UPDATE } from './actions';

import type { UpdateAction, Stats } from './actions';

type Action = UpdateAction;

const initial: Stats = {
    approved: 0,
    fuzzy: 0,
    warnings: 0,
    errors: 0,
    missing: 0,
    unreviewed: 0,
    total: 0,
};

export default function reducer(state: Stats = initial, action: Action): Stats {
    switch (action.type) {
        case UPDATE:
            return {
                ...action.stats,
            };
        default:
            return state;
    }
}
