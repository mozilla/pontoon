/* @flow */

import { useDispatch, useSelector } from 'react-redux';

import * as entities from 'core/entities';
import * as navigation from 'core/navigation';
import * as plural from 'core/plural';

import { actions } from '..';

/**
 * Return a function to send a translation to the server.
 */
export default function useSendTranslation() {
    const dispatch = useDispatch();

    const translation = useSelector((state) => state.editor.translation);
    const isRunningRequest = useSelector(
        (state) => state.editor.isRunningRequest,
    );
    const machinerySources = useSelector(
        (state) => state.editor.machinerySources,
    );
    const machineryTranslation = useSelector(
        (state) => state.editor.machineryTranslation,
    );
    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );
    const locale = useSelector((state) => state.locale);
    const user = useSelector((state) => state.user);
    const router = useSelector((state) => state.router);
    const pluralForm = useSelector((state) =>
        plural.selectors.getPluralForm(state),
    );
    const nextEntity = useSelector((state) =>
        entities.selectors.getNextEntity(state),
    );
    const parameters = useSelector((state) =>
        navigation.selectors.getNavigationParams(state),
    );

    return (ignoreWarnings?: boolean, content?: string) => {
        if (isRunningRequest || !entity || !locale) {
            return;
        }

        const translationContent = content || translation;

        if (typeof translationContent !== 'string') {
            throw new Error(
                'Trying to save an unsupported non-string translation: ' +
                    typeof translationContent,
            );
        }

        let realMachinerySources = machinerySources;
        if (realMachinerySources && machineryTranslation !== translation) {
            realMachinerySources = [];
        }

        dispatch(
            actions.sendTranslation(
                entity,
                translationContent,
                locale,
                pluralForm,
                user.settings.forceSuggestions,
                nextEntity,
                router,
                parameters.resource,
                ignoreWarnings,
                realMachinerySources,
            ),
        );
    };
}
