import NProgress from 'nprogress';
import { useCallback, useContext } from 'react';

import { addComment } from '../../../src/api/comment';
import type { HistoryTranslation } from '../../../src/api/translation';
import { HistoryData } from '../../../src/context/HistoryData';
import { Location } from '../../../src/context/Location';
import { ShowNotification } from '../../../src/context/Notification';
import { COMMENT_ADDED } from '../../../src/modules/notification/messages';
import { useAppDispatch } from '../../../src/hooks';
import { get as getTeamComments } from '../../../src/modules/teamcomments/actions';

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
