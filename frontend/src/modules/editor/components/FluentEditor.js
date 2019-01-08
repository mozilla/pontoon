/* @flow */

import * as React from 'react';
import MonacoEditor from 'react-monaco-editor';

import type { EditorProps } from './GenericEditor';


export default class FluentEditor extends React.Component<EditorProps> {
    render() {
        const options = {
            lineNumbers: false,
            wordWrap: 'on',
            wrappingIndent: 'deepIndent',
            minimap: {
                enabled: false,
            },
        };

        return <MonacoEditor
            theme='vs'
            language='html'
            options={ options }
            value={ this.props.translation }
            onChange={ this.props.updateTranslation }
        />;
    }
}
