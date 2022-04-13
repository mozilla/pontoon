import { useContext } from 'react';

import { Locale } from '~/context/locale';
import { Location } from '~/context/location';
import { useNextEntity, useSelectedEntity } from '~/core/entities/hooks';
import { usePluralForm } from '~/context/pluralForm';
import { useAppDispatch } from '~/hooks';
import type { ChangeOperation } from '~/modules/history';
import { updateStatus } from '~/modules/history/actions';

import { startUpdateTranslation, endUpdateTranslation } from '../actions';

/**
 * Return a function to update the status (approved, rejected... ) of a translation.
 */
export default function useUpdateTranslationStatus(): (
  translationId: number,
  change: ChangeOperation,
  ignoreWarnings?: boolean | null | undefined,
) => void {
  const dispatch = useAppDispatch();

  const entity = useSelectedEntity();
  const locale = useContext(Locale);
  const location = useContext(Location);
  const pluralForm = usePluralForm(entity);
  const nextEntity = useNextEntity();

  return (
    translationId: number,
    change: ChangeOperation,
    ignoreWarnings: boolean | null | undefined,
  ) => {
    dispatch(async (dispatch) => {
      dispatch(startUpdateTranslation());
      await dispatch(
        updateStatus(
          change,
          // The EditorMainAction tests fail if this dispatch() is skipped on an empty entity
          // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
          entity!,
          locale,
          pluralForm,
          translationId,
          nextEntity,
          location,
          ignoreWarnings,
        ),
      );
      dispatch(endUpdateTranslation());
    });
  };
}
