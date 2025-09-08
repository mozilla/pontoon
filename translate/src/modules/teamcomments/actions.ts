import {
  fetchTeamComments,
  setCommentPinned,
  TeamComment,
} from '~/api/comment';
import type { AppDispatch } from '~/store';

export const RECEIVE = 'comments/RECEIVE';
export const REQUEST = 'comments/REQUEST';
export const TOGGLE_PINNED = 'comments/TOGGLE_PINNED';

export type Action = ReceiveAction | RequestAction | TogglePinnedAction;

export type ReceiveAction = {
  readonly type: typeof RECEIVE;
  readonly comments: Array<TeamComment>;
};

export type RequestAction = {
  readonly type: typeof REQUEST;
  readonly entity: number;
};
export function request(entity: number): RequestAction {
  return {
    type: REQUEST,
    entity,
  };
}

export type TogglePinnedAction = {
  readonly type: typeof TOGGLE_PINNED;
  readonly pinned: boolean;
  readonly commentId: number;
};
export function togglePinned(
  pinned: boolean,
  commentId: number,
): TogglePinnedAction {
  return {
    type: TOGGLE_PINNED,
    pinned,
    commentId,
  };
}

export function get(entity: number, locale: string) {
  return async (dispatch: AppDispatch) => {
    // request() must be called separately to prevent
    // re-rendering of the component on addComment()

    const comments = await fetchTeamComments(entity, locale);
    dispatch({ type: RECEIVE, comments });
  };
}

export function togglePinnedStatus(pinned: boolean, commentId: number) {
  return async (dispatch: AppDispatch) => {
    await setCommentPinned(commentId, pinned);
    dispatch(togglePinned(pinned, commentId));
  };
}
