import NProgress from 'nprogress';
import { useCallback, useContext } from 'react';

import { addComment, deleteComment, editComment } from '~/api/comment';
import type { HistoryTranslation } from '~/api/translation';
import { HistoryData } from '~/context/HistoryData';
import { Location } from '~/context/Location';
import { ShowNotification } from '~/context/Notification';
import {
  COMMENT_ADDED,
  COMMENT_DELETED,
  COMMENT_EDITED,
} from '~/modules/notification/messages';
import { useAppDispatch } from '~/hooks';
import { get as getTeamComments } from '~/modules/teamcomments/actions';

export function useAddCommentAndRefresh(
  translation: HistoryTranslation | null,
) {
  const dispatch = useAppDispatch();
  const { entity, locale } = useContext(Location);
  const showNotification = useContext(ShowNotification);
  const { updateHistory } = useContext(HistoryData);

  return useCallback(
    async (comment: string) => {
      NProgress.start();

      await addComment(entity, locale, comment, translation);

      showNotification(COMMENT_ADDED);
      if (translation) {
        updateHistory();
      } else {
        dispatch(getTeamComments(entity, locale));
      }

      NProgress.done();
    },
    [entity, locale, translation, updateHistory],
  );
}

export function useDeleteCommentAndRefresh(
  translation: HistoryTranslation | null,
) {
  const dispatch = useAppDispatch();
  const { entity, locale } = useContext(Location);
  const showNotification = useContext(ShowNotification);
  const { updateHistory } = useContext(HistoryData);

  return useCallback(
    async (commentId: number) => {
      NProgress.start();

      await deleteComment(commentId);

      showNotification(COMMENT_DELETED);

      if (translation) {
        updateHistory();
      } else {
        dispatch(getTeamComments(entity, locale));
      }

      NProgress.done();
    },
    [entity, locale, translation, updateHistory, showNotification],
  );
}

export function useEditCommentAndRefresh(
  translation: HistoryTranslation | null,
) {
  const dispatch = useAppDispatch();
  const { entity, locale } = useContext(Location);
  const showNotification = useContext(ShowNotification);
  const { updateHistory } = useContext(HistoryData);

  return useCallback(
    async (commentId: number, content: string) => {
      NProgress.start();

      await editComment(commentId, content);

      showNotification(COMMENT_EDITED);

      if (translation) {
        updateHistory();
      } else {
        dispatch(getTeamComments(entity, locale));
      }

      NProgress.done();
    },
    [entity, locale, translation, updateHistory, showNotification],
  );
}
