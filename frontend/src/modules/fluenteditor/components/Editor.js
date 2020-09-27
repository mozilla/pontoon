/* @flow */

import * as React from 'react';

import './Editor.css';

import * as editor from 'core/editor';
import { fluent } from 'core/utils';

import SourceEditor from './SourceEditor';
import SimpleEditor from './SimpleEditor';
import RichEditor from './RichEditor';

import type { EditorProps, Translation } from 'core/editor';
import type { SyntaxType } from 'core/utils/fluent/types';

type State = {|
    // Force using the source editor.
    forceSource: boolean,
    // The type of form to use to show the translation.
    syntaxType: SyntaxType,
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
        if (this.props.entity && this.props.entity !== prevProps.entity) {
            this.setState({ forceSource: false });
            this.analyzeFluentMessage();
        }
        // If the user switched the editor mode, update the editor
        // content to match the form type.
        else if (
            this.props.entity &&
            this.state.forceSource !== prevState.forceSource &&
            this.props.editor.translation === prevProps.editor.translation
        ) {
            // Syntax type might have changed in the source editor, make sure it's set correctly
            let syntaxType = this.state.syntaxType;
            if (prevState.forceSource) {
                const message = fluent.parser.parseEntry(
                    this.props.editor.translation,
                );
                if (message.type !== 'Junk') {
                    syntaxType = fluent.getSyntaxType(message);
                    this.setState({ syntaxType });
                }
            }

            // Complex strings can only be displayed in the source editor, so no need to update
            if (syntaxType === 'complex') {
                return;
            }

            const fromSyntax = this.state.forceSource ? syntaxType : 'complex';
            const toSyntax = this.state.forceSource ? 'complex' : syntaxType;
            this.updateEditorContent(
                this.props.editor.translation,
                fromSyntax,
                toSyntax,
            );
        }
        // If translation changes from external source (e.g. copied from helpers),
        // re-analyze the translation.
        else if (
            this.props.entity &&
            !this.state.forceSource &&
            this.props.editor.translation !== prevProps.editor.translation &&
            this.props.editor.changeSource !== 'internal' &&
            this.props.editor.changeSource !== 'machinery' &&
            typeof this.props.editor.translation === 'string'
        ) {
            this.analyzeFluentMessage(this.props.editor.translation);
        }
        // If translation changes from machinery tab,
        // check if it's valid and convert syntax to comlex if no.
        else if (
            this.props.entity &&
            this.state.forceSource &&
            this.props.editor.translation !== prevProps.editor.translation &&
            this.props.editor.changeSource === 'machinery' &&
            typeof this.props.editor.translation === 'string'
        ) {
            const message = fluent.parser.parseEntry(
                this.props.editor.translation,
            );
            if (message.type === 'Junk') {
                this.updateEditorContent(
                    this.props.editor.translation,
                    'simple',
                    'complex',
                );
            }
        }
    }

    /**
     * Analyze the translation to determine the best form to use. Update the
     * content to match that type if needed.
     */
    analyzeFluentMessage(translation: ?string) {
        const props = this.props;

        const source =
            translation ||
            props.activeTranslationString ||
            props.entity.original;
        const message = fluent.parser.parseEntry(source);

        // In case simple message gets analyzed again
        if (message.type === 'Junk') {
            return;
        }

        // Figure out and set the syntax type.
        const syntaxType = fluent.getSyntaxType(message);
        this.setState({ syntaxType });

        // Figure out and set the initial translation content.
        let translationContent = translation || props.activeTranslationString;

        if (syntaxType === 'simple') {
            translationContent = fluent.getSimplePreview(translationContent);
        } else if (syntaxType === 'rich') {
            if (!translationContent) {
                translationContent = fluent.getEmptyMessage(
                    message,
                    props.locale,
                );
            } else {
                translationContent = message;
            }
        }

        // Update the initial translation content only when the entity changed, not
        // when new content is loaded from an external source.
        if (typeof translation === 'undefined') {
            props.setInitialTranslation(translationContent);
        }
        props.updateTranslation(translationContent, true);
    }

    /**
     * Update the content for the new type of form from the previous one. This
     * allows to keep changes made by the user when switching editing modes.
     */
    updateEditorContent(
        translation: Translation,
        fromSyntax: SyntaxType,
        toSyntax: SyntaxType,
    ) {
        const props = this.props;

        const [translationContent, initialContent] = fluent.convertSyntax(
            fromSyntax,
            toSyntax,
            translation,
            props.entity.original,
            props.activeTranslationString,
            props.locale,
        );

        props.updateTranslation(translationContent, true);
        props.setInitialTranslation(initialContent);
    }

    toggleForceSource = () => {
        this.setState((state) => {
            return {
                ...state,
                forceSource: !state.forceSource,
            };
        });
    };

    render() {
        let EditorImplementation = RichEditor;
        if (this.state.forceSource || this.state.syntaxType === 'complex') {
            EditorImplementation = SourceEditor;
        } else if (this.state.syntaxType === 'simple') {
            EditorImplementation = SimpleEditor;
        }

        // Show a button to allow switching to the source editor.
        let ftlSwitch = null;
        // But only if the user is logged in and the string is not read-only.
        if (this.props.user.isAuthenticated && !this.props.isReadOnlyEditor) {
            ftlSwitch =
                this.state.syntaxType === 'complex' ? (
                    <button
                        className='ftl active'
                        title='Advanced FTL mode enabled'
                        onClick={this.props.showNotSupportedMessage}
                    >
                        FTL
                    </button>
                ) : (
                    <button
                        className={
                            'ftl' + (this.state.forceSource ? ' active' : '')
                        }
                        title='Toggle between simple and advanced FTL mode'
                        onClick={this.toggleForceSource}
                    >
                        FTL
                    </button>
                );
        }

        return <EditorImplementation {...this.props} ftlSwitch={ftlSwitch} />;
    }
}

export default editor.connectedEditor(EditorBase);
