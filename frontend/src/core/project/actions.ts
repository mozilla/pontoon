import api from 'core/api';

export const RECEIVE: 'project/RECEIVE' = 'project/RECEIVE';
export const REQUEST: 'project/REQUEST' = 'project/REQUEST';

export type Tag = {
    readonly slug: string;
    readonly name: string;
    readonly priority: number;
};

type Project = {
    slug: string;
    name: string;
    info: string;
    tags: Array<Tag>;
};

/**
 * Notify that project data is being fetched.
 */
export type RequestAction = {
    readonly type: typeof REQUEST;
};
export function request(): RequestAction {
    return {
        type: REQUEST,
    };
}

/**
 * Receive project data.
 */
export type ReceiveAction = {
    readonly type: typeof RECEIVE;
    readonly slug: string;
    readonly name: string;
    readonly info: string;
    readonly tags: Array<Tag>;
};
export function receive(project: Project): ReceiveAction {
    return {
        type: RECEIVE,
        slug: project.slug,
        name: project.name,
        info: project.info,
        tags: project.tags,
    };
}

/**
 * Get data about the current project.
 */
export function get(slug: string): (...args: Array<any>) => any {
    return async (dispatch) => {
        // When 'all-projects' are selected, we do not fetch data.
        if (slug === 'all-projects') {
            return;
        }
        dispatch(request());
        const results = await api.project.get(slug);
        dispatch(receive(results.data.project));
    };
}

export default {
    get,
    receive,
    request,
};
