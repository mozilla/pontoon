/* @flow */

import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';

import './FluentEditor.css';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import * as notification from 'core/notification';
import * as plural from 'core/plural';
import { fluent } from 'core/utils';

import SourceEditor from './source/SourceEditor';
import SimpleEditor from './simple/SimpleEditor';
import RichEditor from './rich/RichEditor';

/**
 * Hook to update the editor content whenever the entity changes.
 *
 * This hook is in charge of formatting the translation content for each type of Fluent Editor.
 * It does *not* update that content when the user switches the "force source" mode though,
 * as that is dealt with by using the `useForceSource` hook.
 */
function useLoadTranslation(syntaxType, forceSource) {
    const dispatch = useDispatch();

    const updateTranslation = editor.useUpdateTranslation();

    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );
    const locale = useSelector((state) => state.locale);
    const activeTranslationString = useSelector((state) =>
        plural.selectors.getTranslationStringForSelectedEntity(state),
    );

    // We do not want to perform any formatting when the user switches "force source",
    // as that is handled in the `useForceSource` hook. We thus keep track of that variable's
    // value and only update when it didn't change since the last render.
    const prevForceSource = React.useRef(forceSource);

    // We want to run the following effect only when the entity changes, and in
    // no other cases. We thus track the entity's pk.
    const prevEntityPK = React.useRef(null);

    React.useLayoutEffect(() => {
        if (
            prevForceSource.current !== forceSource ||
            !entity ||
            prevEntityPK.current === entity.pk
        ) {
            prevForceSource.current = forceSource;
            return;
        }

        if (syntaxType === '') {
            return;
        }

        let translationContent = '';
        if (syntaxType === 'complex') {
            // Use the actual content that we get from the server: a Fluent message as a string.
            translationContent = activeTranslationString;
        } else if (syntaxType === 'simple') {
            // Use a simplified preview of the Fluent message.
            translationContent = fluent.getSimplePreview(
                activeTranslationString,
            );
        } else if (syntaxType === 'rich') {
            // Use a Fluent Message object.
            if (activeTranslationString) {
                translationContent = fluent.flattenMessage(
                    fluent.parser.parseEntry(activeTranslationString),
                );
            } else {
                translationContent = fluent.getEmptyMessage(
                    fluent.parser.parseEntry(entity.original),
                    locale,
                );
            }
        }
        dispatch(editor.actions.setInitialTranslation(translationContent));
        updateTranslation(translationContent, 'initial');

        prevEntityPK.current = entity.pk;
    }, [
        syntaxType,
        forceSource,
        entity,
        activeTranslationString,
        locale,
        updateTranslation,
        dispatch,
    ]);
}

/**
 * Function to analyze a translation and determine what its appropriate syntax is.
 *
 * @returns { string } The syntax of the translation, can be "simple", "rich" or "complex".
 *      - "simple" if the translation can be shown as a simple preview
 *      - "rich" if the translation is not simple but can be handled by the Rich editor
 *      - "complex" otherwise
 */
function getSyntaxType(source) {
    if (source && typeof source !== 'string') {
        return fluent.getSyntaxType(source);
    }

    const message = fluent.parser.parseEntry(source);

    // In case a simple message gets analyzed again.
    if (message.type === 'Junk') {
        return 'simple';
    }

    // Figure out and set the syntax type.
    return fluent.getSyntaxType(message);
}

/**
 * Hook that analyzes editor content and determines what its syntax is.
 *
 * @returns { string } See `getSyntaxType`.
 */
function useAnalyzeSyntax() {
    const [syntaxType, setSyntaxType] = React.useState('');

    const translation = useSelector((state) => state.editor.translation);
    const changeSource = useSelector((state) => state.editor.changeSource);
    const activeTranslationString = useSelector((state) =>
        plural.selectors.getTranslationStringForSelectedEntity(state),
    );
    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );

    React.useLayoutEffect(() => {
        if (!entity) {
            return;
        }
        const source = activeTranslationString || entity.original;
        const syntax = getSyntaxType(source);
        setSyntaxType(syntax);
    }, [entity, activeTranslationString]);

    React.useLayoutEffect(() => {
        if (translation && changeSource !== 'internal') {
            const syntax = getSyntaxType(translation);
            setSyntaxType(syntax);
        }
    }, [translation, changeSource]);

    return syntaxType;
}

/**
 * Hook to allow to force showing the source editor.
 *
 * @returns { Array<boolean, Function> } An array containing:
 *      - a boolean indicating if the source mode is enabled;
 *      - a function to toggle the source mode.
 */
function useForceSource(syntaxType) {
    const dispatch = useDispatch();

    const translation = useSelector((state) => state.editor.translation);
    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );
    const activeTranslationString = useSelector((state) =>
        plural.selectors.getTranslationStringForSelectedEntity(state),
    );
    const locale = useSelector((state) => state.locale);

    // Force using the source editor.
    const [forceSource, setForceSource] = React.useState(false);

    // When the entity changes, reset the `forceSource` setting. Never show the source
    // editor by default.
    React.useEffect(() => {
        setForceSource(false);
    }, [entity]);

    // When a user wants to force (or unforce) the source editor, we need to convert
    // the existing translation to a format appropriate for the next editor type.
    function changeForceSource() {
        if (syntaxType === 'complex') {
            return;
        }
        const fromSyntax = forceSource ? 'complex' : syntaxType;
        const toSyntax = forceSource ? syntaxType : 'complex';
        const [translationContent, initialContent] = fluent.convertSyntax(
            fromSyntax,
            toSyntax,
            translation,
            entity.original,
            activeTranslationString,
            locale,
        );
        dispatch(editor.actions.setInitialTranslation(initialContent));
        dispatch(editor.actions.update(translationContent));
        setForceSource(!forceSource);
    }

    return [forceSource, changeForceSource];
}

/**
 * Editor dedicated to modifying Fluent strings.
 *
 * Renders the most appropriate type of editor for the current translation.
 */
export default function FluentEditor() {
    const dispatch = useDispatch();

    const isReadOnlyEditor = useSelector((state) =>
        entities.selectors.isReadOnlyEditor(state),
    );
    const user = useSelector((state) => state.user);

    const syntaxType = useAnalyzeSyntax();
    const [forceSource, changeForceSource] = useForceSource(syntaxType);
    useLoadTranslation(syntaxType, forceSource);

    // Do not render if the syntax has not yet been computed.
    if (syntaxType === '') {
        return null;
    }

    // Choose which editor implementation to render.
    let EditorImplementation = RichEditor;
    if (forceSource || syntaxType === 'complex') {
        EditorImplementation = SourceEditor;
    } else if (syntaxType === 'simple') {
        EditorImplementation = SimpleEditor;
    }

    // When the syntax is complex, the editor is blocked in source mode, and it
    // becomes impossible to switch to a different editor type. Thus we show a
    // notification to the user if they try to use the "FTL" switch button.
    function showUnsupportedMessage() {
        dispatch(
            notification.actions.add(
                notification.messages.FTL_NOT_SUPPORTED_RICH_EDITOR,
            ),
        );
    }

    // Show a button to allow switching to the source editor.
    let ftlSwitch = null;
    // But only if the user is logged in and the string is not read-only.
    if (user.isAuthenticated && !isReadOnlyEditor) {
        if (syntaxType === 'complex') {
            // TODO: To Localize
            ftlSwitch = (
                <button
                    className='ftl active'
                    title='Advanced FTL mode enabled'
                    onClick={showUnsupportedMessage}
                >
                    FTL
                </button>
            );
        } else {
            // TODO: To Localize
            ftlSwitch = (
                <button
                    className={'ftl' + (forceSource ? ' active' : '')}
                    title='Toggle between simple and advanced FTL mode'
                    onClick={changeForceSource}
                >
                    FTL
                </button>
            );
        }
    }

    return <EditorImplementation ftlSwitch={ftlSwitch} />;
}
