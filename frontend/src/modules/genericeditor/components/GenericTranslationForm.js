/* @flow */

import * as React from 'react';

import type { EditorProps } from 'core/editor';

import isEqual from 'lodash.isequal';

/*
 * Render a simple textarea to edit a translation.
 */
export default class GenericTranslationForm extends React.Component<EditorProps> {
    textarea: { current: any };

    constructor(props: EditorProps) {
        super(props);

        this.textarea = React.createRef();
    }

    componentDidMount() {
        this.focusInput(true);
    }

    componentDidUpdate(prevProps: EditorProps) {
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
                editor.selectionReplacementContent,
            );
            this.props.resetSelectionContent();
        }

        const prevPropsWithoutUser = this.removeUser(prevProps);
        const propsWithoutUser = this.removeUser(this.props);

        if (!isEqual(prevPropsWithoutUser, propsWithoutUser)) {
            this.focusInput(editor.changeSource !== 'internal');
        }
    }

    removeUser(props: EditorProps) {
        const { user, ...propsWithoutUser } = props;
        return propsWithoutUser;
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

        const newSelectionPos =
            this.textarea.current.selectionStart + content.length;

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

    handleShortcuts = (event: SyntheticKeyboardEvent<HTMLTextAreaElement>) => {
        this.props.handleShortcuts(event, this.props.sendTranslation);
    };

    handleChange = (event: SyntheticInputEvent<HTMLTextAreaElement>) => {
        this.props.updateTranslation(event.currentTarget.value);
    };

    render() {
        return (
            <textarea
                placeholder={
                    this.props.isReadOnlyEditor
                        ? null
                        : 'Type translation and press Enter to save'
                }
                readOnly={this.props.isReadOnlyEditor}
                ref={this.textarea}
                value={this.props.editor.translation}
                onKeyDown={this.handleShortcuts}
                onChange={this.handleChange}
                dir={this.props.locale.direction}
                lang={this.props.locale.code}
                data-script={this.props.locale.script}
            />
        );
    }
}
