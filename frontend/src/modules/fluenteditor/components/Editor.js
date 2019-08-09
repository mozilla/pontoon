/* @flow */

import * as React from 'react';

import './Editor.css';

import * as editor from 'core/editor';
import { fluent } from 'core/utils';

import SourceEditor from './SourceEditor';
import SimpleEditor from './SimpleEditor';
import RichEditor from './RichEditor';

import type { EditorProps } from 'core/editor';


type State = {|
    // Force using the source editor.
    forceSource: boolean,
    // The type of form to use to show the translation.
    syntaxType: 'simple' | 'rich' | 'complex',
|};


/**
 * Editor dedicated to modifying Fluent strings.
 *
 * Renders the best type of form for the passed string.
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
        // If the entity changed, re-analyze the translation.
        if (
            this.props.entity &&
            this.props.entity !== prevProps.entity
        ) {
            this.setState({ forceSource: false });
            this.analyzeFluentMessage();
        }
        // Otherwise if the user switched the editor mode, update the editor
        // content to match the form type.
        else if (
            this.props.entity &&
            this.state.forceSource !== prevState.forceSource &&
            this.props.editor.translation === prevProps.editor.translation
        ) {
            const fromSyntax = this.state.forceSource ? 'simple' : 'complex';
            const toSyntax = this.state.forceSource ? 'complex' : 'simple';
            this.updateEditorContent(
                this.props.editor.translation,
                fromSyntax,
                toSyntax,
            );
        }
    }

    /**
     * Analyze the translation to determine the best form to use. Update the
     * content to match that type if needed.
     */
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
        if (!fluent.isSupportedMessage(message)) {
            return 'complex';
        }

        if (
            fluent.isSimpleMessage(message) ||
            fluent.isSimpleSingleAttributeMessage(message)
        ) {
            return 'simple';
        }

        return 'rich';
    }

    /**
     * Update the content for the new type of form from the previous one. This
     * allows to keep changes made by the user when switching editing modes.
     */
    updateEditorContent(translation: string, fromSyntax: string, toSyntax: string) {
        const props = this.props;

        let translationContent = translation;
        let originalContent = props.activeTranslation;

        if (fromSyntax === 'complex' && toSyntax === 'simple') {
            translationContent = fluent.getSimplePreview(translationContent);
            originalContent = fluent.getSimplePreview(originalContent);

            // If any of the contents are junk, discard them.
            if (translationContent === translation) {
                translationContent = '';
            }
            if (originalContent === props.activeTranslation) {
                originalContent = '';
            }
        }
        else if (fromSyntax === 'simple' && toSyntax === 'complex') {
            translationContent = fluent.getReconstructedSimpleMessage(
                props.entity.original,
                translation,
            );

            // If there is no active translation (it's an untranslated string)
            // we make the initial translation an empty fluent message to avoid
            // showing unchanged content warnings.
            if (!originalContent) {
                originalContent = fluent.getReconstructedSimpleMessage(
                    props.entity.original,
                    '',
                );
            }
        }

        props.setInitialTranslation(originalContent);
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
        let EditorImplementation = RichEditor;
        if (this.state.forceSource || this.state.syntaxType === 'complex') {
            EditorImplementation = SourceEditor
        }
        else if (this.state.syntaxType === 'simple') {
            EditorImplementation = SimpleEditor;
        }

        // If the type of the string is not 'complex', meaning we show an
        // optimized editor by default, show a button to allow switching to
        // the source editor.
        const ftlSwitch = this.state.syntaxType === 'complex' ? <button
            className='ftl active'
            title='Advanced FTL mode enabled'
            onClick={ this.props.showNotSupportedMessage }
        >
            FTL
        </button> : <button
            className={ 'ftl' + (this.state.forceSource ? ' active' : '') }
            title='Toggle between simple and advanced FTL mode'
            onClick={ this.toggleForceSource }
        >
            FTL
        </button>;

        return <EditorImplementation
            { ...this.props }
            ftlSwitch={ ftlSwitch }
        />;
    }
}


export default editor.connectedEditor(EditorBase);
