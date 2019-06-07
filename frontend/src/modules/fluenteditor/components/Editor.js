/* @flow */

import * as React from 'react';

import './Editor.css';

import * as editor from 'core/editor';
import { fluent } from 'core/utils';

import SourceEditor from './SourceEditor';
import SimpleEditor from './SimpleEditor';

import type { EditorProps } from 'core/editor';


type State = {|
    forceSource: boolean,
    syntaxType: 'simple' | 'complex',
|};


/**
 * Editor
 */
export class EditorBase extends React.Component<EditorProps, State> {
    constructor(props: EditorProps) {
        super(props);
        this.state = {
            forceSource: false,
            syntaxType: 'complex',
        };
    }

    componentDidMount() {
        this.analyzeFluentMessage();
    }

    componentDidUpdate(prevProps: EditorProps, prevState: State) {
        if (
            this.props.entity &&
            this.props.entity !== prevProps.entity
        ) {
            this.analyzeFluentMessage();
        }
        else if (
            this.props.entity &&
            this.state.forceSource !== prevState.forceSource
        ) {
            const fromSyntax = this.state.forceSource ? 'simple' : 'complex';
            const toSyntax = this.state.forceSource ? 'complex' : 'simple';
            this.updateEditorContent(
                this.props.translation,
                fromSyntax,
                toSyntax,
            );
        }
    }

    analyzeFluentMessage() {
        const props = this.props;

        const source = props.activeTranslation || props.entity.original;
        const message = fluent.parser.parseEntry(source);

        const syntaxType = this.getSyntaxType(message);
        let translationContent = props.activeTranslation;

        if (syntaxType === 'simple' && !this.state.forceSource) {
            translationContent = fluent.getSimplePreview(props.activeTranslation);
        }

        this.setState({ syntaxType });
        props.setInitialTranslation(translationContent);
        props.updateTranslation(translationContent);
    }

    getSyntaxType(message: Object) {
        let syntaxType = 'complex';

        if (fluent.isSimpleMessage(message)) {
            syntaxType = 'simple';
        }

        return syntaxType;
    }

    updateEditorContent(translation: string, fromSyntax: string, toSyntax: string) {
        const props = this.props;

        let translationContent = translation;

        if (fromSyntax === 'complex' && toSyntax === 'simple') {
            translationContent = fluent.getSimplePreview(translation);
        }
        else if (fromSyntax === 'simple' && toSyntax === 'complex') {
            translationContent = fluent.getReconstructedSimpleMessage(
                props.entity.original,
                translation,
            );
        }

        props.setInitialTranslation(translationContent);
        props.updateTranslation(translationContent);
    }

    toggleForceSource = () => {
        this.setState(state => {
            return {
                ...state,
                forceSource: !state.forceSource,
            };
        });
    }

    render() {
        let EditorImpl = SourceEditor;
        if (!this.state.forceSource && this.state.syntaxType === 'simple') {
            EditorImpl = SimpleEditor;
        }

        const ftlSwitch = this.state.syntaxType === 'complex' ? null : <button
            className={ 'ftl' + (this.state.forceSource ? ' active' : '') }
            title='Toggle between simple and advanced FTL mode'
            onClick={ this.toggleForceSource }
        >
            FTL
        </button>;

        return <EditorImpl { ...this.props } ftlSwitch={ ftlSwitch } />;
    }
}


export default editor.connectedEditor(EditorBase);
