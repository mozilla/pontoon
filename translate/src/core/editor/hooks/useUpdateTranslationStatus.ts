import NProgress from 'nprogress';
import { useContext } from 'react';

import { ChangeOperation, setTranslationStatus } from '~/api/translation';
import { EditorActions } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { FailedChecksData } from '~/context/FailedChecksData';
import { Locale } from '~/context/Locale';
import { Location } from '~/context/Location';
import { updateEntityTranslation } from '~/core/entities/actions';
import { usePushNextTranslatable } from '~/core/entities/hooks';
import { addNotification } from '~/core/notification/actions';
import { updateResource } from '~/core/resource/actions';
import { updateStats } from '~/core/stats/actions';
import { useAppDispatch } from '~/hooks';
import {
  get as getHistory,
  _getOperationNotif,
} from '~/modules/history/actions';

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
  const locale = useContext(Locale);
  const { entity, hasPluralForms, pluralForm } = useContext(EntityView);
  const pushNextTranslatable = usePushNextTranslatable();
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
      const notif = _getOperationNotif(change, !!results.translation);
      dispatch(addNotification(notif));

      if (results.translation && change === 'approve') {
        // The change did work, we want to move on to the next Entity or pluralForm.
        pushNextTranslatable();
      } else {
        const pf = hasPluralForms ? pluralForm : -1;
        dispatch(getHistory(entity.pk, locale.code, pf));
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
      const pf = hasPluralForms ? pluralForm : -1;
      dispatch(updateEntityTranslation(entity.pk, pf, results.translation));
    }

    NProgress.done();
    setEditorBusy(false);
  };
}
