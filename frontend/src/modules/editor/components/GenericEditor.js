/* @flow */

import * as React from 'react';

import type { Locale } from 'core/locales';
import type { ChangeOperation } from 'modules/history';
import type { EditorState } from '..';


export type EditorProps = {|
    isReadOnlyEditor: boolean,
    editor: EditorState,
    locale: Locale,
    copyOriginalIntoEditor: () => void,
    resetFailedChecks: () => void,
    resetSelectionContent: () => void,
    sendTranslation: (ignoreWarnings: ?boolean) => void,
    updateTranslation: (string) => void,
    updateTranslationStatus: (
        translationId: number,
        change: ChangeOperation,
        ignoreWarnings: ?boolean,
    ) => void,
|};

type State = {|
    isEnterShortcutDisabled: boolean,
|};


/*
 * Render a simple textarea to edit a translation.
 */
export default class GenericEditor extends React.Component<EditorProps, State> {
    textarea: { current: any };

    constructor(props: EditorProps) {
        super(props);

        this.state = {
            isEnterShortcutDisabled: false,
        };
        this.textarea = React.createRef();
    }

    componentDidMount() {
        if (!this.textarea.current) {
            return;
        }

        this.textarea.current.focus();
        // After mounting, put the cursor at the beginning of the content.
        this.textarea.current.setSelectionRange(0, 0);
    }

    componentDidUpdate(prevProps: EditorProps, prevState: State) {
        // If there is content to add to the editor, do so, then remove
        // the content so it isn't added again.
        // This is an abuse of the redux store, because we want to update
        // the content differently for each Editor type. Thus each Editor
        // implements an `updateTranslationSelectionWith` method and that is
        // used to update the translation.
        if (this.props.editor.selectionReplacementContent) {
            this.updateTranslationSelectionWith(
                this.props.editor.selectionReplacementContent
            );
            this.props.resetSelectionContent();
        }

        if (this.textarea.current) {
            this.textarea.current.focus();
        }

        if (this.props.editor.changeSource === 'external') {
            this.textarea.current.setSelectionRange(0, 0);
        }

        if (prevState.isEnterShortcutDisabled) {
            this.setState({ isEnterShortcutDisabled: false });
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

        // On Enter, send the current translation.
        if (key === 13 && !event.ctrlKey && !event.shiftKey && !event.altKey) {
            if (this.state.isEnterShortcutDisabled) {
                event.preventDefault();
                return;
            }
            this.setState({ isEnterShortcutDisabled: true });

            handledEvent = true;

            const errors = this.props.editor.errors;
            const warnings = this.props.editor.warnings;
            const source = this.props.editor.source;
            const ignoreWarnings = !!(errors.length || warnings.length);

            if (typeof(source) === 'number') {
                this.props.updateTranslationStatus(source, 'approve', ignoreWarnings);
            }
            else {
                this.props.sendTranslation(ignoreWarnings);
            }
        }

        // On Esc, close failed checks popup if open.
        if (key === 27) {
            handledEvent = true;

            const errors = this.props.editor.errors;
            const warnings = this.props.editor.warnings;

            if (errors.length || warnings.length) {
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
            this.props.updateTranslation('');
        }

        // On Tab, walk through current helper tab content and copy it.
        // TODO

        if (handledEvent) {
            event.preventDefault();
        }
    }

    render() {
        return <textarea
            placeholder={ this.props.isReadOnlyEditor ? null : 'Type translation and press Enter to save' }
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
