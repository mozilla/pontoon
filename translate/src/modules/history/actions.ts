import NProgress from 'nprogress';

import { Entity, fetchEntityHistory } from '~/api/entity';
import {
  ChangeOperation,
  deleteTranslation,
  HistoryTranslation,
  setTranslationStatus,
} from '~/api/translation';
import type { LocaleType } from '~/context/locale';
import type { LocationType } from '~/context/location';
import type { PluralFormType } from '~/context/pluralForm';
import {
  resetEditor,
  updateFailedChecks,
  updateTranslation,
} from '~/core/editor/actions';
import { updateEntityTranslation } from '~/core/entities/actions';
import { addNotification } from '~/core/notification/actions';
import { notificationMessages } from '~/core/notification/messages';
import { updateResource } from '~/core/resource/actions';
import { updateStats } from '~/core/stats/actions';
import type { AppDispatch } from '~/store';

export const RECEIVE = 'history/RECEIVE';
export const REQUEST = 'history/REQUEST';
export const UPDATE = 'history/UPDATE';

export type Action = ReceiveAction | RequestAction | UpdateAction;

export type ReceiveAction = {
  readonly type: typeof RECEIVE;
  readonly translations: Array<HistoryTranslation>;
};
export function receive(
  translations: Array<HistoryTranslation>,
): ReceiveAction {
  return {
    type: RECEIVE,
    translations,
  };
}

export type UpdateAction = {
  readonly type: typeof UPDATE;
  readonly translation: HistoryTranslation;
};
export function update(translation: HistoryTranslation): UpdateAction {
  return {
    type: UPDATE,
    translation,
  };
}

export type RequestAction = {
  readonly type: typeof REQUEST;
  readonly entity: number;
  readonly pluralForm: number;
};
export function request(entity: number, pluralForm: number): RequestAction {
  return {
    type: REQUEST,
    entity,
    pluralForm,
  };
}

export function get(entity: number, locale: string, pluralForm: number) {
  return async (dispatch: AppDispatch) => {
    // request() must be called separately to prevent
    // re-rendering of the component on addComment()

    const translations = await fetchEntityHistory(entity, locale, pluralForm);
    dispatch({ type: RECEIVE, translations });
  };
}

function _getOperationNotif(change: ChangeOperation, success: boolean) {
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

export function updateStatus(
  change: ChangeOperation,
  entity: Entity,
  locale: LocaleType,
  { pluralForm, setPluralForm }: PluralFormType,
  translation: number,
  nextEntity: Entity | null,
  location: LocationType,
  ignoreWarnings: boolean,
) {
  return async (dispatch: AppDispatch) => {
    NProgress.start();

    const results = await setTranslationStatus(
      change,
      translation,
      location.resource,
      ignoreWarnings,
    );

    // Update the UI based on the response.
    if (results.failedChecks) {
      dispatch(updateTranslation(results.string, 'external'));
      dispatch(updateFailedChecks(results.failedChecks, translation));
    } else {
      // Show a notification to explain what happened.
      const notif = _getOperationNotif(change, !!results.translation);
      dispatch(addNotification(notif));

      if (results.translation && change === 'approve') {
        // The change did work, we want to move on to the next Entity or pluralForm.
        if (pluralForm !== -1 && pluralForm < locale.cldrPlurals.length - 1) {
          setPluralForm(pluralForm + 1);
        } else if (nextEntity && nextEntity.pk !== entity.pk) {
          location.push({ entity: nextEntity.pk });
        }
        dispatch(resetEditor());
      } else {
        dispatch(get(entity.pk, locale.code, pluralForm));
      }

      if (results.stats) {
        // Update stats in the progress chart and the filter panel.
        dispatch(updateStats(results.stats));

        // Update stats in the resource menu.
        dispatch(
          updateResource(
            entity.path,
            results.stats.approved,
            results.stats.warnings,
          ),
        );
      }

      // Update entity translation data now that it has changed on the server.
      dispatch(
        updateEntityTranslation(entity.pk, pluralForm, results.translation),
      );
    }

    NProgress.done();
  };
}

export function deleteTranslation_(
  entity: number,
  locale: string,
  pluralForm: number,
  translation: number,
) {
  return async (dispatch: AppDispatch) => {
    NProgress.start();

    const { status } = await deleteTranslation(translation);

    if (status) {
      dispatch(addNotification(notificationMessages.TRANSLATION_DELETED));
      dispatch(get(entity, locale, pluralForm));
    } else {
      dispatch(
        addNotification(notificationMessages.UNABLE_TO_DELETE_TRANSLATION),
      );
    }

    NProgress.done();
  };
}
