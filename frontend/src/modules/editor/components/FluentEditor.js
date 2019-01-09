/* @flow */

import * as React from 'react';
import AceEditor from 'react-ace';

import './editor-mode-fluent';
import './editor-theme-fluent';

import type { EditorProps } from './GenericEditor';


/*
 * Render an Ace editor for Fluent string editting.
 */
export default class FluentEditor extends React.Component<EditorProps> {
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
            scrollPastEnd: false,
            showInvisibles: false,
            showFoldWidgets: false,
            showLineNumbers: false,
            showPrintMargin: false,
        };

        return <AceEditor
            mode='fluent'
            theme='fluent'
            width='100%'
            wrapEnabled={ true }
            setOptions={ options }
            value={ this.props.translation }
            onChange={ this.props.updateTranslation }
        />;
    }
}
