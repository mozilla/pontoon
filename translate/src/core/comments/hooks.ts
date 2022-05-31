import NProgress from 'nprogress';
import { useCallback, useContext } from 'react';

import { addComment } from '~/api/comment';
import type { HistoryTranslation } from '~/api/translation';
import { Location } from '~/context/Location';
import { usePluralForm } from '~/context/PluralForm';
import { addNotification } from '~/core/notification/actions';
import { notificationMessages } from '~/core/notification/messages';
import { useAppDispatch } from '~/hooks';
import { get as getHistory } from '~/modules/history/actions';
import { get as getTeamComments } from '~/modules/teamcomments/actions';
import { useSelectedEntity } from '../entities/hooks';

export function useAddCommentAndRefresh(
  translation: HistoryTranslation | null,
) {
  const dispatch = useAppDispatch();
  const { entity, locale } = useContext(Location);
  const { pluralForm } = usePluralForm(useSelectedEntity());

  return useCallback(
    async (comment: string) => {
      NProgress.start();

      await addComment(entity, locale, comment, translation);

      dispatch(addNotification(notificationMessages.COMMENT_ADDED));
      if (translation) {
        dispatch(getHistory(entity, locale, pluralForm));
      } else {
        dispatch(getTeamComments(entity, locale));
      }

      NProgress.done();
    },
    [entity, locale, pluralForm, translation],
  );
}
