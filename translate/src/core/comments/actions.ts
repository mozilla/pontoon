import NProgress from 'nprogress';

import { addComment } from '~/api/comment';
import { addNotification } from '~/core/notification/actions';
import notificationMessages from '~/core/notification/messages';
import { get as getHistory } from '~/modules/history/actions';
import { get as getTeamComments } from '~/modules/teamcomments/actions';
import type { AppDispatch } from '~/store';

export function addComment_(
  entity: number,
  locale: string,
  pluralForm: number,
  translation: number | null | undefined,
  comment: string,
) {
  return async (dispatch: AppDispatch) => {
    NProgress.start();

    await addComment(entity, locale, comment, translation);

    dispatch(addNotification(notificationMessages.COMMENT_ADDED));
    if (translation) {
      dispatch(getHistory(entity, locale, pluralForm));
    } else {
      dispatch(getTeamComments(entity, locale));
    }

    NProgress.done();
  };
}

export default {
  addComment: addComment_,
};
