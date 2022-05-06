import { fetchProject, Tag } from '~/api/project';
import type { AppDispatch } from '~/store';

export const RECEIVE = 'project/RECEIVE';
export const REQUEST = 'project/REQUEST';

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
  readonly tags: Tag[];
};

/**
 * Get data about the current project.
 */
export const getProject = (slug: string) => async (dispatch: AppDispatch) => {
  // When 'all-projects' are selected, we do not fetch data.
  if (slug !== 'all-projects') {
    dispatch({ type: REQUEST });
    const { info, name, slug: slug_, tags } = await fetchProject(slug);
    dispatch({
      type: RECEIVE,
      slug: slug_,
      name: name,
      info: info,
      tags: tags.sort((a, b) => b.priority - a.priority),
    });
  }
};
