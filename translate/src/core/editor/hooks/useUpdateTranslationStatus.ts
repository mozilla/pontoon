import { useContext } from 'react';

import { Locale } from '~/context/locale';
import { getNextEntity, getSelectedEntity } from '~/core/entities/selectors';
import { getNavigationParams } from '~/core/navigation/selectors';
import { getPluralForm } from '~/core/plural/selectors';
import { useAppDispatch, useAppSelector } from '~/hooks';
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

  const entity = useAppSelector(getSelectedEntity);
  const locale = useContext(Locale);
  const parameters = useAppSelector(getNavigationParams);
  const pluralForm = useAppSelector(getPluralForm);
  const nextEntity = useAppSelector(getNextEntity);
  const router = useAppSelector((state) => state.router);

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
          parameters.resource,
          pluralForm,
          translationId,
          nextEntity,
          router,
          ignoreWarnings,
        ),
      );
      dispatch(endUpdateTranslation());
    });
  };
}
