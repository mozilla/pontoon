import type { TeamComment } from '~/api/comment';

import { Action, RECEIVE, REQUEST, TOGGLE_PINNED } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const TEAM_COMMENTS = 'teamcomments';

export type TeamCommentState = {
  readonly fetching: boolean;
  readonly entity: number | null | undefined;
  readonly comments: Array<TeamComment>;
};

function togglePinnedComment(
  state: TeamCommentState,
  pinned: boolean,
  commentId: number,
): Array<TeamComment> {
  return state.comments.map((comment) => {
    if (comment.id !== commentId) {
      return comment;
    }

    return {
      ...comment,
      pinned: pinned,
    };
  });
}

const initialState: TeamCommentState = {
  fetching: false,
  entity: null,
  comments: [],
};

export function reducer(
  state: TeamCommentState = initialState,
  action: Action,
): TeamCommentState {
  switch (action.type) {
    case REQUEST:
      return {
        ...state,
        fetching: true,
        entity: action.entity,
        comments: [],
      };
    case RECEIVE:
      return {
        ...state,
        fetching: false,
        comments: action.comments,
      };
    case TOGGLE_PINNED:
      return {
        ...state,
        comments: togglePinnedComment(state, action.pinned, action.commentId),
      };
    default:
      return state;
  }
}
