import NProgress from 'nprogress';
import { useContext } from 'react';

import { createTranslation } from '~/api/translation';
import {
  EditorActions,
  EditorData,
  getEditedTranslation,
} from '~/context/Editor';
import { FailedChecksData } from '~/context/FailedChecksData';
import { Locale } from '~/context/Locale';
import { Location } from '~/context/Location';
import { usePluralForm } from '~/context/PluralForm';
import { UnsavedActions } from '~/context/UnsavedChanges';
import { updateEntityTranslation } from '~/core/entities/actions';
import { useNextEntity, useSelectedEntity } from '~/core/entities/hooks';
import { addNotification } from '~/core/notification/actions';
import { notificationMessages } from '~/core/notification/messages';
import { updateResource } from '~/core/resource/actions';
import { updateStats } from '~/core/stats/actions';
import { useAppDispatch, useAppSelector } from '~/hooks';

/**
 * Return a function to send a translation to the server.
 */
export function useSendTranslation(): (ignoreWarnings?: boolean) => void {
  const dispatch = useAppDispatch();

  const location = useContext(Location);
  const locale = useContext(Locale);
  const entity = useSelectedEntity();
  const forceSuggestions = useAppSelector(
    (state) => state.user.settings.forceSuggestions,
  );
  const { pluralForm, setPluralForm } = usePluralForm(entity);
  const nextEntity = useNextEntity();
  const { resetUnsavedChanges } = useContext(UnsavedActions);
  const { setFailedChecks } = useContext(FailedChecksData);
  const { setEditorBusy } = useContext(EditorActions);
  const editor = useContext(EditorData);
  const translation = getEditedTranslation(editor);
  const { busy, machinery } = editor;

  return async (ignoreWarnings = false) => {
    if (busy || !entity) {
      return;
    }

    NProgress.start();
    setEditorBusy(true);

    const sources =
      machinery && machinery.translation === translation
        ? machinery.sources
        : [];
    const content = await createTranslation(
      entity.pk,
      translation,
      locale.code,
      pluralForm,
      entity.original,
      forceSuggestions,
      location.resource,
      ignoreWarnings,
      sources,
    );

    if (content.status) {
      // Notify the user of the change that happened.
      dispatch(addNotification(notificationMessages.TRANSLATION_SAVED));

      // Ignore existing unsavedchanges because they are saved now.
      resetUnsavedChanges(true);

      dispatch(
        updateEntityTranslation(entity.pk, pluralForm, content.translation),
      );

      // Update stats in the filter panel and resource menu if possible.
      if (content.stats) {
        dispatch(updateStats(content.stats));
        dispatch(
          updateResource(
            entity.path,
            content.stats.approved,
            content.stats.warnings,
          ),
        );
      }

      // The change did work, we want to move on to the next Entity or pluralForm.
      if (pluralForm !== -1 && pluralForm < locale.cldrPlurals.length - 1) {
        setPluralForm(pluralForm + 1);
      } else if (nextEntity && nextEntity.pk !== entity.pk) {
        location.push({ entity: nextEntity.pk });
      }
    } else if (content.failedChecks) {
      setFailedChecks(content.failedChecks, 'submitted');
    } else if (content.same) {
      // The translation that was provided is the same as an existing
      // translation for that entity.
      dispatch(addNotification(notificationMessages.SAME_TRANSLATION));
    }

    setEditorBusy(false);
    NProgress.done();
  };
}
