/* @flow */

import * as React from 'react';

import { withActionsDisabled } from 'core/utils';

import type { EditorProps } from 'core/editor';


type InternalProps = {|
    ...EditorProps,
    isActionDisabled: boolean,
    disableAction: () => void,
|};


/*
 * Render a simple textarea to edit a translation.
 */
export class GenericTranslationFormBase extends React.Component<InternalProps> {
    textarea: { current: any };

    constructor(props: InternalProps) {
        super(props);

        this.textarea = React.createRef();
    }

    componentDidMount() {
        this.focusInput(true);
    }

    componentDidUpdate(prevProps: InternalProps) {
        // Unused by Generic Editor - reset to default value.
        if (this.props.editor.initialTranslation) {
            return this.props.setInitialTranslation('');
        }

        // Close failed checks popup when content of the editor changes,
        // but only if the errors and warnings did not change
        // meaning they were already shown in the previous render
        const prevEditor = prevProps.editor;
        const editor = this.props.editor;
        if (
            prevProps.editor.translation !== this.props.editor.translation &&
            prevEditor.errors === editor.errors &&
            prevEditor.warnings === editor.warnings &&
            (editor.errors.length || editor.warnings.length)
        ) {
            this.props.resetFailedChecks();
        }

        // When content of the translation changes
        //   - close unsaved changes popup if open
        //   - update unsaved changes status
        if (prevEditor.translation !== editor.translation) {
            if (this.props.unsavedchanges.shown) {
                this.props.hideUnsavedChanges();
            }
            this.props.updateUnsavedChanges();
        }

        // If there is content to add to the editor, do so, then remove
        // the content so it isn't added again.
        // This is an abuse of the redux store, because we want to update
        // the content differently for each Editor type. Thus each Editor
        // implements an `updateTranslationSelectionWith` method and that is
        // used to update the translation.
        if (editor.selectionReplacementContent) {
            this.updateTranslationSelectionWith(
                editor.selectionReplacementContent
            );
            this.props.resetSelectionContent();
        }

        this.focusInput(editor.changeSource === 'external');
    }

    focusInput(putCursorToStart: boolean) {
        const input = this.textarea.current;

        if (!input) {
            return;
        }

        if (this.props.searchInputFocused) {
            return;
        }

        input.focus();

        if (putCursorToStart) {
            input.setSelectionRange(0, 0);
        }
    }

    updateTranslationSelectionWith(content: string) {
        if (!this.textarea.current) {
            return;
        }

        const newSelectionPos = this.textarea.current.selectionStart + content.length;

        // Update content in the textarea.
        this.textarea.current.setRangeText(content);

        // Put the cursor right after the newly inserted content.
        this.textarea.current.setSelectionRange(
            newSelectionPos,
            newSelectionPos,
        );

        // Update the state to show the new content in the Editor.
        this.props.updateTranslation(this.textarea.current.value);
    }

    handleChange = (event: SyntheticInputEvent<HTMLTextAreaElement>) => {
        this.props.updateTranslation(event.currentTarget.value);
    }

    handleShortcuts = (event: SyntheticKeyboardEvent<HTMLTextAreaElement>) => {
        const key = event.keyCode;

        let handledEvent = false;

        // On Enter:
        //   - If unsaved changes popup is shown, leave anyway.
        //   - If failed checks popup is shown after approving a translation, approve it anyway.
        //   - In other cases, send current translation.
        if (key === 13 && !event.ctrlKey && !event.shiftKey && !event.altKey) {
            if (this.props.isActionDisabled) {
                event.preventDefault();
                return;
            }
            this.props.disableAction();

            handledEvent = true;

            const errors = this.props.editor.errors;
            const warnings = this.props.editor.warnings;
            const source = this.props.editor.source;
            const ignoreWarnings = !!(errors.length || warnings.length);

            // Leave anyway
            if (this.props.unsavedchanges.shown) {
                this.props.ignoreUnsavedChanges();
            }
            // Approve anyway
            else if (typeof(source) === 'number') {
                this.props.updateTranslationStatus(source, 'approve', ignoreWarnings);
            }
            // Send translation
            else {
                this.props.sendTranslation(ignoreWarnings);
            }
        }

        // On Esc, close unsaved changes and failed checks popups if open.
        if (key === 27) {
            handledEvent = true;

            const errors = this.props.editor.errors;
            const warnings = this.props.editor.warnings;

            // Close unsaved changes popup
            if (this.props.unsavedchanges.shown) {
                this.props.hideUnsavedChanges();
            }
            // Close failed checks popup
            else if (errors.length || warnings.length) {
                this.props.resetFailedChecks();
            }
        }

        // On Ctrl + Shift + C, copy the original translation.
        if (key === 67 && event.ctrlKey && event.shiftKey && !event.altKey) {
            handledEvent = true;
            this.props.copyOriginalIntoEditor();
        }

        // On Ctrl + Shift + Backspace, clear the content.
        if (key === 8 && event.ctrlKey && event.shiftKey && !event.altKey) {
            handledEvent = true;
            this.props.updateTranslation('', true);
        }

        // On Tab, walk through current helper tab content and copy it.
        // TODO

        if (handledEvent) {
            event.preventDefault();
        }
    }

    render() {
        return <textarea
            placeholder={
                this.props.isReadOnlyEditor ? null :
                'Type translation and press Enter to save'
            }
            readOnly={ this.props.isReadOnlyEditor }
            ref={ this.textarea }
            value={ this.props.editor.translation }
            onKeyDown={ this.handleShortcuts }
            onChange={ this.handleChange }
            dir={ this.props.locale.direction }
            lang={ this.props.locale.code }
            data-script={ this.props.locale.script }
        />;
    }
}


export default withActionsDisabled(GenericTranslationFormBase);
