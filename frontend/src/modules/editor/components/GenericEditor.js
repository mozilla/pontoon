/* @flow */

import * as React from 'react';

import type { Locale } from 'core/locales';
import type { EditorState } from '..';


export type EditorProps = {|
    isReadOnlyEditor: boolean,
    editor: EditorState,
    translation: string,
    locale: Locale,
    copyOriginalIntoEditor: () => void,
    resetSelectionContent: () => void,
    sendTranslation: () => void,
    updateTranslation: (string) => void,
|};


/*
 * Render a simple textarea to edit a translation.
 */
export default class GenericEditor extends React.Component<EditorProps> {
    textarea: { current: any };

    constructor(props: EditorProps) {
        super(props);
        this.textarea = React.createRef();
    }

    componentDidMount() {
        if (!this.textarea.current) {
            return;
        }

        // After mounting, put the cursor at the end of the content.
        this.textarea.current.setSelectionRange(
            this.props.translation.length,
            this.props.translation.length,
        );
    }

    componentDidUpdate() {
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
            handledEvent = true;
            this.props.sendTranslation();
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
            readOnly={ this.props.isReadOnlyEditor }
            ref={ this.textarea }
            value={ this.props.translation }
            onKeyDown={ this.handleShortcuts }
            onChange={ this.handleChange }
            dir={ this.props.locale.direction }
            lang={ this.props.locale.code }
            data-script={ this.props.locale.script }
        />;
    }
}
