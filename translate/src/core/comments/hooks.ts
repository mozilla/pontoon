import NProgress from 'nprogress';
import { useCallback, useContext } from 'react';

import { addComment } from '~/api/comment';
import type { HistoryTranslation } from '~/api/translation';
import { HistoryData } from '~/context/HistoryData';
import { Location } from '~/context/Location';
import { addNotification } from '~/core/notification/actions';
import { notificationMessages } from '~/core/notification/messages';
import { useAppDispatch } from '~/hooks';
import { get as getTeamComments } from '~/modules/teamcomments/actions';

export function useAddCommentAndRefresh(
  translation: HistoryTranslation | null,
) {
  const dispatch = useAppDispatch();
  const { entity, locale } = useContext(Location);
  const { updateHistory } = useContext(HistoryData);

  return useCallback(
    async (comment: string) => {
      NProgress.start();

      await addComment(entity, locale, comment, translation);

      dispatch(addNotification(notificationMessages.COMMENT_ADDED));
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
