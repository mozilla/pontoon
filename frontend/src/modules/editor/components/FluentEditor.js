/* @flow */

import * as React from 'react';
import AceEditor from 'react-ace';
import { FluentParser, lineOffset, columnOffset } from 'fluent-syntax';

import './editor-mode-fluent';
import './editor-theme-fluent';

import type { EditorProps } from './GenericEditor';


const fluent_parser = new FluentParser();

function annotate(source) {
    let resource = fluent_parser.parse(source);
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
export default class FluentEditor extends React.Component<EditorProps> {
    aceEditor: { current: any };

    constructor(props: EditorProps) {
        super(props);
        this.aceEditor = React.createRef();
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
        if (this.aceEditor.current) {
            this.aceEditor.current.editor.insert(content);
            this.props.updateTranslation(this.aceEditor.current.editor.getValue());
        }
    }

    render() {
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
            wrapEnabled={ true }
            setOptions={ options }
            value={ this.props.editor.translation }
            annotations={ annotate(this.props.editor.translation) }
            onChange={ this.props.updateTranslation }
            debounceChangePeriod={200}
        />;
    }
}
