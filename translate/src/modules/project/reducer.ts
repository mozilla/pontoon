import type { Tag } from '~/api/project';

import { Action, RECEIVE, REQUEST } from './actions';
import { LocaleOption } from '~/api/other-locales';

// Name of this module.
// Used as the key to store this module's reducer.
export const PROJECT = 'project';

export type ProjectState = {
  readonly fetching: boolean;
  readonly slug: string;
  readonly name: string;
  readonly info: string;
  readonly tags: Tag[];
  readonly locales: LocaleOption[];
};

const initial: ProjectState = {
  fetching: false,
  slug: '',
  name: '',
  info: '',
  tags: [],
  locales: [],
};

export function reducer(
  state: ProjectState = initial,
  action: Action,
): ProjectState {
  switch (action.type) {
    case REQUEST:
      return {
        ...state,
        fetching: true,
        slug: action.slug,
        locales: [],
      };
    case RECEIVE:
      return {
        ...state,
        fetching: false,
        slug: action.slug,
        name: action.name,
        info: action.info,
        tags: action.tags,
        locales: action.locales,
      };
    default:
      return state;
  }
}
