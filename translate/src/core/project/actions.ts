import api from '~/core/api';

import type { AppDispatch } from '~/store';

export const RECEIVE = 'project/RECEIVE';
export const REQUEST = 'project/REQUEST';

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

export type Action = ReceiveAction | RequestAction;

/** Notify that project data is being fetched.  */
type RequestAction = {
  readonly type: typeof REQUEST;
};

/** Receive project data.  */
type ReceiveAction = {
  readonly type: typeof RECEIVE;
  readonly slug: string;
  readonly name: string;
  readonly info: string;
  readonly tags: Array<Tag>;
};

/**
 * Get data about the current project.
 */
export const getProject = (slug: string) => async (dispatch: AppDispatch) => {
  // When 'all-projects' are selected, we do not fetch data.
  if (slug !== 'all-projects') {
    dispatch({ type: REQUEST });
    const results = await api.project.get(slug);
    const { info, name, slug: slug_, tags } = results.data.project as Project;
    dispatch({
      type: RECEIVE,
      slug: slug_,
      name: name,
      info: info,
      tags: tags.sort((a, b) => b.priority - a.priority),
    });
  }
};
