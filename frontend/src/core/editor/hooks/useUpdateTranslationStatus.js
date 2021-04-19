/* @flow */

import { useDispatch, useSelector } from 'react-redux';

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
    ignoreWarnings?: ?boolean,
) => void {
    const dispatch = useDispatch();

    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );
    const locale = useSelector((state) => state.locale);
    const parameters = useSelector((state) =>
        navigation.selectors.getNavigationParams(state),
    );
    const pluralForm = useSelector((state) =>
        plural.selectors.getPluralForm(state),
    );
    const nextEntity = useSelector((state) =>
        entities.selectors.getNextEntity(state),
    );
    const router = useSelector((state) => state.router);

    return (
        translationId: number,
        change: ChangeOperation,
        ignoreWarnings: ?boolean,
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
