import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';

import * as editor from 'core/editor';
import * as entities from 'core/entities';

type Props = {
    sendTranslation: (ignoreWarnings?: boolean) => void;
    updateTranslation: (arg0: string) => void;
};

/**
 * Shows a generic translation form, a simple textarea.
 */
export default function GenericTranslationForm(
    props: Props,
): React.ReactElement<'textarea'> {
    const dispatch = useDispatch();

    const translation = useSelector((state) => state.editor.translation);
    const changeSource = useSelector((state) => state.editor.changeSource);
    const searchInputFocused = useSelector(
        (state) => state.search.searchInputFocused,
    );
    const locale = useSelector((state) => state.locale);
    const isReadOnlyEditor = useSelector((state) =>
        entities.selectors.isReadOnlyEditor(state),
    );

    const handleShortcutsFn = editor.useHandleShortcuts();

    const textareaRef = React.useRef(null);

    // Focus the textarea when something changes.
    React.useLayoutEffect(() => {
        const input = textareaRef.current;

        if (!input || searchInputFocused) {
            return;
        }

        input.focus();

        if (changeSource !== 'internal') {
            input.setSelectionRange(0, 0);
        }
    }, [translation, changeSource, searchInputFocused]);

    // Reset checks when content of the editor changes.
    React.useEffect(() => {
        dispatch(editor.actions.resetFailedChecks());
    }, [translation, dispatch]);

    // When the translation or the initial translation changes, check for unsaved changes.
    editor.useUpdateUnsavedChanges(false);

    // Replace selected content on external actions (for example, when a user clicks
    // on a placeable).
    editor.useReplaceSelectionContent((content: string) => {
        const input = textareaRef.current;

        if (!input) {
            return;
        }

        const newSelectionPos = input.selectionStart + content.length;

        // Update content in the textarea.
        input.setRangeText(content);

        // Put the cursor right after the newly inserted content.
        input.setSelectionRange(newSelectionPos, newSelectionPos);

        // Update the state to show the new content in the Editor.
        props.updateTranslation(input.value);
    });

    function handleChange(event: React.SyntheticEvent<HTMLTextAreaElement>) {
        props.updateTranslation(event.currentTarget.value);
    }

    function handleShortcuts(event: React.KeyboardEvent<HTMLTextAreaElement>) {
        handleShortcutsFn(event, props.sendTranslation);
    }

    return (
        <textarea
            placeholder={
                isReadOnlyEditor
                    ? null
                    : 'Type translation and press Enter to save'
            }
            readOnly={isReadOnlyEditor}
            ref={textareaRef}
            value={translation}
            onKeyDown={handleShortcuts}
            onChange={handleChange}
            dir={locale.direction}
            lang={locale.code}
            data-script={locale.script}
        />
    );
}
