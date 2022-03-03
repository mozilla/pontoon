import { RECEIVE, REQUEST, TOGGLE_PINNED } from './actions';

import type { TeamComment } from '~/core/api';
import type {
  ReceiveAction,
  RequestAction,
  TogglePinnedAction,
} from './actions';

type Action = ReceiveAction | RequestAction | TogglePinnedAction;

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

export default function reducer(
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
