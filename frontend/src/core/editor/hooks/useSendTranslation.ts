import { useDispatch } from 'react-redux';

import { useAppSelector } from 'hooks';
import * as entities from 'core/entities';
import * as navigation from 'core/navigation';
import * as plural from 'core/plural';

import { actions } from '..';

/**
 * Return a function to send a translation to the server.
 */
export default function useSendTranslation(): (
    ignoreWarnings?: boolean,
    content?: string,
) => void {
    const dispatch = useDispatch();

    const translation = useAppSelector((state) => state.editor.translation);
    const isRunningRequest = useAppSelector(
        (state) => state.editor.isRunningRequest,
    );
    const machinerySources = useAppSelector(
        (state) => state.editor.machinerySources,
    );
    const machineryTranslation = useAppSelector(
        (state) => state.editor.machineryTranslation,
    );
    const entity = useAppSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );
    const locale = useAppSelector((state) => state.locale);
    const user = useAppSelector((state) => state.user);
    const router = useAppSelector((state) => state.router);
    const pluralForm = useAppSelector((state) =>
        plural.selectors.getPluralForm(state),
    );
    const nextEntity = useAppSelector((state) =>
        entities.selectors.getNextEntity(state),
    );
    const parameters = useAppSelector((state) =>
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
