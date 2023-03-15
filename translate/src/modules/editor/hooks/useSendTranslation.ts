import NProgress from 'nprogress';
import { useContext } from 'react';

import { createTranslation } from '~/api/translation';
import {
  EditorActions,
  EditorData,
  useEditorMessageEntry,
} from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { FailedChecksData } from '~/context/FailedChecksData';
import { Locale } from '~/context/Locale';
import { Location } from '~/context/Location';
import { ShowNotification } from '~/context/Notification';
import { UnsavedActions } from '~/context/UnsavedChanges';
import { updateEntityTranslation } from '~/modules/entities/actions';
import { usePushNextTranslatable } from '~/modules/entities/hooks';
import {
  SAME_TRANSLATION,
  TRANSLATION_SAVED,
} from '~/modules/notification/messages';
import { updateResource } from '~/modules/resource/actions';
import { updateStats } from '~/modules/stats/actions';
import { useAppDispatch, useAppSelector } from '~/hooks';
import { serializeEntry } from '~/utils/message';

/**
 * Return a function to send a translation to the server.
 */
export function useSendTranslation(): (ignoreWarnings?: boolean) => void {
  const dispatch = useAppDispatch();

  const location = useContext(Location);
  const locale = useContext(Locale);
  const showNotification = useContext(ShowNotification);
  const forceSuggestions = useAppSelector(
    (state) => state.user.settings.forceSuggestions,
  );
  const { entity, hasPluralForms, pluralForm } = useContext(EntityView);
  const pushNextTranslatable = usePushNextTranslatable();
  const { resetUnsavedChanges } = useContext(UnsavedActions);
  const { setFailedChecks } = useContext(FailedChecksData);
  const { setEditorBusy } = useContext(EditorActions);
  const { busy, machinery } = useContext(EditorData);
  const entry = useEditorMessageEntry();

  return async (ignoreWarnings = false) => {
    if (busy || entity.pk === 0) {
      return;
    }

    NProgress.start();
    setEditorBusy(true);

    const translation = serializeEntry(entity.format, entry);
    const sources =
      machinery && machinery.translation === translation
        ? machinery.sources
        : [];
    const content = await createTranslation(
      entity.pk,
      translation,
      locale.code,
      hasPluralForms ? pluralForm : -1,
      entity.original,
      forceSuggestions,
      location.resource,
      ignoreWarnings,
      sources,
    );

    if (content.status) {
      // Notify the user of the change that happened.
      showNotification(TRANSLATION_SAVED);

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
            content.stats.pretranslated,
            content.stats.warnings,
          ),
        );
      }

      // The change did work, we want to move on to the next Entity or pluralForm.
      pushNextTranslatable();
    } else if (content.failedChecks) {
      setFailedChecks(content.failedChecks, 'submitted');
    } else if (content.same) {
      // The translation that was provided is the same as an existing
      // translation for that entity.
      showNotification(SAME_TRANSLATION);
    }

    setEditorBusy(false);
    NProgress.done();
  };
}
