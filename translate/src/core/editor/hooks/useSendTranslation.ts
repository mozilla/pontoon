import NProgress from 'nprogress';
import { useContext } from 'react';

import { createTranslation } from '~/api/translation';
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

import {
  startUpdateTranslation,
  resetEditor,
  updateFailedChecks,
  endUpdateTranslation,
} from '../actions';

/**
 * Return a function to send a translation to the server.
 */
export function useSendTranslation(): (
  ignoreWarnings?: boolean,
  content?: string,
) => void {
  const dispatch = useAppDispatch();

  const {
    isRunningRequest,
    machinerySources,
    machineryTranslation,
    translation,
  } = useAppSelector((state) => state.editor);
  const entity = useSelectedEntity();
  const locale = useContext(Locale);
  const forceSuggestions = useAppSelector(
    (state) => state.user.settings.forceSuggestions,
  );
  const { pluralForm, setPluralForm } = usePluralForm(entity);
  const nextEntity = useNextEntity();
  const location = useContext(Location);
  const { resetUnsavedChanges } = useContext(UnsavedActions);

  return async (ignoreWarnings = false, contentArg?: string) => {
    if (isRunningRequest || !entity) {
      return;
    }

    const translationContent = contentArg || translation;

    if (typeof translationContent !== 'string') {
      throw new Error(
        'Trying to save an unsupported non-string translation: ' +
          typeof translationContent,
      );
    }

    NProgress.start();
    dispatch(startUpdateTranslation());

    const content = await createTranslation(
      entity.pk,
      translationContent,
      locale.code,
      pluralForm,
      entity.original,
      forceSuggestions,
      location.resource,
      ignoreWarnings,
      machineryTranslation === translation ? machinerySources : [],
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
      dispatch(resetEditor());
    } else if (content.failedChecks) {
      dispatch(updateFailedChecks(content.failedChecks, 'submitted'));
    } else if (content.same) {
      // The translation that was provided is the same as an existing
      // translation for that entity.
      dispatch(addNotification(notificationMessages.SAME_TRANSLATION));
    }

    dispatch(endUpdateTranslation());
    NProgress.done();
  };
}
