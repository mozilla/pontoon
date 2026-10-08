import { LocaleOption } from '~/api/other-locales';
import { fetchProject, Tag } from '~/api/project';
import type { AppDispatch } from '~/store';

export const RECEIVE = 'project/RECEIVE';
export const REQUEST = 'project/REQUEST';

export type Action = ReceiveAction | RequestAction;

/** Notify that project data is being fetched.  */
type RequestAction = {
  readonly type: typeof REQUEST;
  readonly slug: string;
};

/** Receive project data.  */
type ReceiveAction = {
  readonly type: typeof RECEIVE;
  readonly slug: string;
  readonly name: string;
  readonly info: string;
  readonly isDbProject: boolean;
  readonly tags: Tag[];
  readonly locales: LocaleOption[];
};

/**
 * Get data about the current project.
 */
export const getProject = (slug: string) => async (dispatch: AppDispatch) => {
  // When 'all-projects' are selected, we do not fetch data.
  dispatch({ type: REQUEST, slug });
  if (slug !== 'all-projects') {
    const {
      info,
      name,
      slug: slug_,
      is_db_project,
      tags,
      locales,
    } = await fetchProject(slug);
    dispatch({
      type: RECEIVE,
      slug: slug_,
      name: name,
      info: info,
      isDbProject: is_db_project,
      tags: tags.sort((a, b) => b.priority - a.priority),
      locales: locales,
    });
  }
};
