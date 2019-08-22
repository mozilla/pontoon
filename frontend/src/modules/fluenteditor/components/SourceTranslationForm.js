/* @flow */

import * as React from 'react';
import AceEditor from 'react-ace';
import { lineOffset, columnOffset } from 'fluent-syntax';

import './editor-mode-fluent';
import './editor-theme-fluent';

import { fluent } from 'core/utils';

import type { EditorProps } from 'core/editor';


function annotate(source) {
    let resource = fluent.parser.parse(source);
    let junks = resource.body.filter(entry => entry.type === 'Junk');
    let annotations = [];

    for (let junk of junks) {
        for (let annot of junk.annotations) {
            annotations.push({
                type: 'error',
                text: `${annot.code}: ${annot.message}`,
                row: lineOffset(source, annot.span.start),
                column: columnOffset(source, annot.span.start),
            });
        }
    }

    return annotations;
}


/*
 * Render an Ace editor for Fluent string editting.
 */
export default class SourceTranslationForm extends React.Component<EditorProps> {
    aceEditor: { current: any };

    constructor(props: EditorProps) {
        super(props);
        this.aceEditor = React.createRef();
    }

    componentDidMount() {
        if (!this.aceEditor.current) {
            return;
        }
        this.aceEditor.current.editor.focus();
        this.aceEditor.current.editor.moveCursorTo(0, 0);
        this.aceEditor.current.editor.clearSelection();
    }

    componentDidUpdate(prevProps: EditorProps) {
        // Close failed checks popup when content of the editor changes,
        // but only if the errors and warnings did not change
        // meaning they were already shown in the previous render
        const prevEditor = prevProps.editor;
        const editor = this.props.editor;
        if (
            prevEditor.translation !== editor.translation &&
            prevEditor.errors === editor.errors &&
            prevEditor.warnings === editor.warnings &&
            (editor.errors.length || editor.warnings.length)
        ) {
            this.props.resetFailedChecks();
        }

        // When content of the editor changes
        //   - close unsaved changes popup if open
        //   - update unsaved changes status
        if (prevEditor.translation !== editor.translation) {
            if (this.props.unsavedchanges.shown) {
                this.props.hideUnsavedChanges();
            }
            this.props.updateUnsavedChanges();
        }

        if (!this.aceEditor.current) {
            return;
        }

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

        this.aceEditor.current.editor.focus();
    }

    updateTranslationSelectionWith(content: string) {
        if (this.aceEditor.current) {
            this.aceEditor.current.editor.insert(content);
            this.props.updateTranslation(this.aceEditor.current.editor.getValue());
        }
    }

    render() {
        if (typeof(this.props.editor.translation) !== 'string') {
            // This is a transational state.
            return null;
        }

        const options = {
            animatedScroll: false,
            autoScrollEditorIntoView: false,
            behavioursEnabled: false,
            cursorStyle: 'ace',
            displayIndentGuides: false,
            fadeFoldWidgets: false,
            fontSize: 14,
            highlightActiveLine: false,
            highlightSelectedWord: false,
            indentedSoftWrap: false,
            printMargin: false,
            printMarginColumn: false,
            readOnly: this.props.isReadOnlyEditor,
            scrollPastEnd: false,
            showInvisibles: false,
            showFoldWidgets: false,
            showLineNumbers: false,
            showPrintMargin: false,
        };

        return <AceEditor
            ref={ this.aceEditor }
            mode='fluent'
            theme='fluent'
            width='100%'
            focus={ true }
            wrapEnabled={ true }
            setOptions={ options }
            value={ this.props.editor.translation }
            annotations={ annotate(this.props.editor.translation) }
            onChange={ this.props.updateTranslation }
            debounceChangePeriod={200}
        />;
    }
}
