/* @flow */

import * as React from 'react';

import './RichTranslationForm.css';

import type { EditorProps } from 'core/editor';


/**
 * Render an Rich editor for Fluent string editting.
 */
export default class RichTranslationForm extends React.Component<EditorProps> {
    componentDidUpdate(prevProps: EditorProps) {
        const prevEditor = prevProps.editor;
        const editor = this.props.editor;

        // If the translation is a string, that means we're in a translational
        // state and there's going to be another render with a Fluent AST.
        if (typeof(editor.translation) === 'string') {
            return;
        }

        // Close failed checks popup when content of the editor changes,
        // but only if the errors and warnings did not change
        // meaning they were already shown in the previous render
        if (
            !editor.translation.equals(prevEditor.translation) &&
            prevEditor.errors === editor.errors &&
            prevEditor.warnings === editor.warnings &&
            (editor.errors.length || editor.warnings.length)
        ) {
            this.props.resetFailedChecks();
        }

        // When content of the editor changes
        //   - close unsaved changes popup if open
        //   - update unsaved changes status
        if (!editor.translation.equals(prevEditor.translation)) {
            if (this.props.unsavedchanges.shown) {
                this.props.hideUnsavedChanges();
            }
            this.props.updateUnsavedChanges();
        }
    }

    createHandleChange = (path: Array<string | number>) => {
        return (event: SyntheticInputEvent<HTMLTextAreaElement>) => {
            const value = event.currentTarget.value;
            const message = this.props.editor.translation;

            let dest = message;
            // Walk the path until the next to last item.
            for (let i = 0, ln = path.length; i < ln - 1; i++) {
                dest = dest[path[i]];
            }
            // Assign the new value to the last element in the path, so that
            // it is actually assigned to the message object reference and
            // to the extracted value.
            dest[path[path.length - 1]] = value;

            this.props.updateTranslation(message);
        }
    }

    renderElements(
        elements: Array<Object>,
        path: Array<string | number>,
        label: string,
    ): Array<React.Node> {
        return elements.map((element, index) => {
            if (element.type === 'TextElement') {
                return <tr key={ `message-value-${index}` }>
                    <td>
                        <label htmlFor={ `message-value-${index}` }>{ label }</label>
                    </td>
                    <td>
                        <textarea
                            id={ `message-value-${index}` }
                            className=""
                            value={ element.value }
                            onChange={ this.createHandleChange([].concat(path, [ index, 'value' ])) }
                        />
                    </td>
                </tr>;
            }

            return null;
        })
    }

    render() {
        const message = this.props.editor.translation;

        return <div className="fluent-rich-translation-form">
            <table>
                <tbody>
                    { (!message.value) ? null :
                        this.renderElements(message.value.elements, [ 'value', 'elements' ], 'Value')
                    }
                    { (!message.attributes) ? null :
                        message.attributes.map((attribute, index) => {
                            if (attribute.value) {
                                return this.renderElements(attribute.value.elements, [ 'attributes', index, 'value', 'elements' ], attribute.id.name)
                            }
                            return null;
                        })
                    }
                </tbody>
            </table>
        </div>;
    }
}
