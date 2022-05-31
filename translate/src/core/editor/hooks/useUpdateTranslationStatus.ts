import NProgress from 'nprogress';
import { useContext } from 'react';

import { ChangeOperation, setTranslationStatus } from '~/api/translation';
import { EditorActions } from '~/context/Editor';
import { FailedChecksData } from '~/context/FailedChecksData';
import { Locale } from '~/context/Locale';
import { Location } from '~/context/Location';
import { usePluralForm } from '~/context/PluralForm';
import { updateEntityTranslation } from '~/core/entities/actions';
import { useNextEntity, useSelectedEntity } from '~/core/entities/hooks';
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

  const entity = useSelectedEntity();
  const locale = useContext(Locale);
  const { push, resource } = useContext(Location);
  const { pluralForm, setPluralForm } = usePluralForm(entity);
  const nextEntity = useNextEntity();
  const { setFailedChecks } = useContext(FailedChecksData);
  const { setEditorBusy, setEditorFromHistory } = useContext(EditorActions);

  return async (
    translationId: number,
    change: ChangeOperation,
    ignoreWarnings: boolean,
  ) => {
    if (!entity) {
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
        if (pluralForm !== -1 && pluralForm < locale.cldrPlurals.length - 1) {
          setPluralForm(pluralForm + 1);
        } else if (nextEntity && nextEntity.pk !== entity.pk) {
          push({ entity: nextEntity.pk });
        }
      } else {
        dispatch(getHistory(entity.pk, locale.code, pluralForm));
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
    setEditorBusy(false);
  };
}
