import { RECEIVE, REQUEST } from './actions';

import type { Action, Tag } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME = 'project';

export type ProjectState = {
  readonly fetching: boolean;
  readonly slug: string;
  readonly name: string;
  readonly info: string;
  readonly tags: Array<Tag>;
};

const initial: ProjectState = {
  fetching: false,
  slug: '',
  name: '',
  info: '',
  tags: [],
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
      };
    case RECEIVE:
      return {
        ...state,
        fetching: false,
        slug: action.slug,
        name: action.name,
        info: action.info,
        tags: action.tags,
      };
    default:
      return state;
  }
}
