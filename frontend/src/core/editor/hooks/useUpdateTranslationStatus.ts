import { useDispatch } from 'react-redux';

import { useAppSelector } from 'hooks';
import * as entities from 'core/entities';
import * as navigation from 'core/navigation';
import * as plural from 'core/plural';
import * as history from 'modules/history';

import { actions } from '..';

import type { ChangeOperation } from 'modules/history';

/**
 * Return a function to update the status (approved, rejected... ) of a translation.
 */
export default function useUpdateTranslationStatus(): (
    translationId: number,
    change: ChangeOperation,
    ignoreWarnings?: boolean | null | undefined,
) => void {
    const dispatch = useDispatch();

    const entity = useAppSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );
    const locale = useAppSelector((state) => state.locale);
    const parameters = useAppSelector((state) =>
        navigation.selectors.getNavigationParams(state),
    );
    const pluralForm = useAppSelector((state) =>
        plural.selectors.getPluralForm(state),
    );
    const nextEntity = useAppSelector((state) =>
        entities.selectors.getNextEntity(state),
    );
    const router = useAppSelector((state) => state.router);

    return (
        translationId: number,
        change: ChangeOperation,
        ignoreWarnings: boolean | null | undefined,
    ) => {
        dispatch(async (dispatch) => {
            dispatch(actions.startUpdateTranslation());
            await dispatch(
                history.actions.updateStatus(
                    change,
                    entity,
                    locale,
                    parameters.resource,
                    pluralForm,
                    translationId,
                    nextEntity,
                    router,
                    ignoreWarnings,
                ),
            );
            dispatch(actions.endUpdateTranslation());
        });
    };
}
