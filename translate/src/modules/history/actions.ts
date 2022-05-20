import NProgress from 'nprogress';

import { fetchEntityHistory } from '~/api/entity';
import {
  ChangeOperation,
  deleteTranslation,
  HistoryTranslation,
} from '~/api/translation';
import { addNotification } from '~/core/notification/actions';
import { notificationMessages } from '~/core/notification/messages';
import type { AppDispatch } from '~/store';

export const RECEIVE = 'history/RECEIVE';
export const REQUEST = 'history/REQUEST';

export type Action = ReceiveAction | RequestAction;

type ReceiveAction = {
  readonly type: typeof RECEIVE;
  readonly translations: Array<HistoryTranslation>;
};

type RequestAction = { readonly type: typeof REQUEST };
export function requestHistory(): RequestAction {
  return { type: REQUEST };
}

export function getHistory(entity: number, locale: string, pluralForm: number) {
  return async (dispatch: AppDispatch) => {
    // request() must be called separately to prevent
    // re-rendering of the component on addComment()

    const translations = await fetchEntityHistory(entity, locale, pluralForm);
    dispatch({ type: RECEIVE, translations });
  };
}

export function _getOperationNotif(change: ChangeOperation, success: boolean) {
  if (success) {
    switch (change) {
      case 'approve':
        return notificationMessages.TRANSLATION_APPROVED;
      case 'unapprove':
        return notificationMessages.TRANSLATION_UNAPPROVED;
      case 'reject':
        return notificationMessages.TRANSLATION_REJECTED;
      case 'unreject':
        return notificationMessages.TRANSLATION_UNREJECTED;
      default:
        throw new Error('Unexpected translation status change: ' + change);
    }
  } else {
    switch (change) {
      case 'approve':
        return notificationMessages.UNABLE_TO_APPROVE_TRANSLATION;
      case 'unapprove':
        return notificationMessages.UNABLE_TO_UNAPPROVE_TRANSLATION;
      case 'reject':
        return notificationMessages.UNABLE_TO_REJECT_TRANSLATION;
      case 'unreject':
        return notificationMessages.UNABLE_TO_UNREJECT_TRANSLATION;
      default:
        throw new Error('Unexpected translation status change: ' + change);
    }
  }
}

export function deleteTranslation_(
  entity: number | undefined,
  locale: string,
  pluralForm: number,
  translation: number,
) {
  return async (dispatch: AppDispatch) => {
    NProgress.start();

    const { status } = await deleteTranslation(translation);

    if (entity && status) {
      dispatch(addNotification(notificationMessages.TRANSLATION_DELETED));
      dispatch(getHistory(entity, locale, pluralForm));
    } else {
      dispatch(
        addNotification(notificationMessages.UNABLE_TO_DELETE_TRANSLATION),
      );
    }

    NProgress.done();
  };
}
