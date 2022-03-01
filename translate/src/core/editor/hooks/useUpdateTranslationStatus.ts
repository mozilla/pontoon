import { useContext } from 'react';

import { Locale } from '~/context/locale';
import { useNextEntity, useSelectedEntity } from '~/core/entities/hooks';
import { getPluralForm } from '~/core/plural/selectors';
import { useAppDispatch, useAppSelector } from '~/hooks';
import { useLocation } from '~/hooks/useLocation';
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
  const { resource } = useLocation();
  const pluralForm = useAppSelector(getPluralForm);
  const nextEntity = useNextEntity();
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
          resource,
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
