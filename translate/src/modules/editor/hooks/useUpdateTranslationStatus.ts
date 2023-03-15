import NProgress from 'nprogress';
import { useContext } from 'react';

import { ChangeOperation, setTranslationStatus } from '~/api/translation';
import { EditorActions } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { FailedChecksData } from '~/context/FailedChecksData';
import { HistoryData } from '~/context/HistoryData';
import { Location } from '~/context/Location';
import { ShowNotification } from '~/context/Notification';
import { updateEntityTranslation } from '~/modules/entities/actions';
import { usePushNextTranslatable } from '~/modules/entities/hooks';
import {
  TRANSLATION_APPROVED,
  TRANSLATION_REJECTED,
  TRANSLATION_UNAPPROVED,
  TRANSLATION_UNREJECTED,
  UNABLE_TO_APPROVE_TRANSLATION,
  UNABLE_TO_REJECT_TRANSLATION,
  UNABLE_TO_UNAPPROVE_TRANSLATION,
  UNABLE_TO_UNREJECT_TRANSLATION,
} from '~/modules/notification/messages';
import { updateResource } from '~/modules/resource/actions';
import { updateStats } from '~/modules/stats/actions';
import { useAppDispatch } from '~/hooks';

/**
 * Return a function to update the status (approved, rejected... ) of a translation.
 */
export function useUpdateTranslationStatus(
  showButtonStatus = true,
): (
  translationId: number,
  change: ChangeOperation,
  ignoreWarnings: boolean,
) => void {
  const dispatch = useAppDispatch();

  const { resource } = useContext(Location);
  const showNotification = useContext(ShowNotification);
  const { entity, hasPluralForms, pluralForm } = useContext(EntityView);
  const pushNextTranslatable = usePushNextTranslatable();
  const { updateHistory } = useContext(HistoryData);
  const { setFailedChecks } = useContext(FailedChecksData);
  const { setEditorBusy, setEditorFromHistory } = useContext(EditorActions);

  return async (
    translationId: number,
    change: ChangeOperation,
    ignoreWarnings: boolean,
  ) => {
    if (entity.pk === 0) {
      return;
    }

    if (showButtonStatus) {
      setEditorBusy(true);
    }
    NProgress.start();

    const results = await setTranslationStatus(
      change,
      translationId,
      resource,
      ignoreWarnings,
    );

    // Update the UI based on the response.
    if (results.failedChecks) {
      setEditorFromHistory(results.string);
      setFailedChecks(results.failedChecks, translationId);
    } else {
      // Show a notification to explain what happened.
      const notif = getNotification(change, !!results.translation);
      showNotification(notif);

      if (results.translation && change === 'approve') {
        // The change did work, we want to move on to the next Entity or pluralForm.
        pushNextTranslatable();
      } else {
        updateHistory();
      }

      if (results.stats) {
        // Update stats in the progress chart and the filter panel.
        dispatch(updateStats(results.stats));

        // Update stats in the resource menu.
        dispatch(
          updateResource(
            entity.path,
            results.stats.approved,
            results.stats.pretranslated,
            results.stats.warnings,
          ),
        );
      }

      // Update entity translation data now that it has changed on the server.
      const pf = hasPluralForms ? pluralForm : -1;
      dispatch(updateEntityTranslation(entity.pk, pf, results.translation));
    }

    NProgress.done();
    setEditorBusy(false);
  };
}

function getNotification(change: ChangeOperation, success: boolean) {
  if (success) {
    switch (change) {
      case 'approve':
        return TRANSLATION_APPROVED;
      case 'unapprove':
        return TRANSLATION_UNAPPROVED;
      case 'reject':
        return TRANSLATION_REJECTED;
      case 'unreject':
        return TRANSLATION_UNREJECTED;
      default:
        throw new Error('Unexpected translation status change: ' + change);
    }
  } else {
    switch (change) {
      case 'approve':
        return UNABLE_TO_APPROVE_TRANSLATION;
      case 'unapprove':
        return UNABLE_TO_UNAPPROVE_TRANSLATION;
      case 'reject':
        return UNABLE_TO_REJECT_TRANSLATION;
      case 'unreject':
        return UNABLE_TO_UNREJECT_TRANSLATION;
      default:
        throw new Error('Unexpected translation status change: ' + change);
    }
  }
}
