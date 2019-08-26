/* @flow */

import * as React from 'react';

import './RichTranslationForm.css';

import { fluent } from 'core/utils';

import type { EditorProps } from 'core/editor';
import type {
    FluentAttribute,
    FluentAttributes,
    FluentElement,
    FluentMessage,
    FluentValue,
} from 'core/utils/fluent/types';


/**
 * Render a Rich editor for Fluent string editting.
 */
export default class RichTranslationForm extends React.Component<EditorProps> {
    componentDidMount() {
        const editor = this.props.editor;

        // If the translation is a string, that means we're in a transitional
        // state and there's going to be another render with a Fluent AST.
        if (typeof(editor.translation) === 'string') {
            return;
        }

        // Walks the tree and unify all simple elements into just one.
        const message = fluent.flattenMessage(editor.translation);
        this.props.updateTranslation(message);
    }

    componentDidUpdate(prevProps: EditorProps) {
        const editor = this.props.editor;

        // If the translation is a string, that means we're in a translational
        // state and there's going to be another render with a Fluent AST.
        if (typeof(editor.translation) === 'string') {
            return;
        }

        this.update(prevProps, editor.translation);
    }

    update(prevProps: EditorProps, translation: FluentMessage) {
        const prevEditor = prevProps.editor;
        const editor = this.props.editor;

        if (!translation.equals(prevEditor.translation)) {
            // Walks the tree and unify all simple elements into just one.
            const message = fluent.flattenMessage(translation);
            this.props.updateTranslation(message);
        }

        // Close failed checks popup when content of the editor changes,
        // but only if the errors and warnings did not change
        // meaning they were already shown in the previous render
        if (
            !translation.equals(prevEditor.translation) &&
            prevEditor.errors === editor.errors &&
            prevEditor.warnings === editor.warnings &&
            (editor.errors.length || editor.warnings.length)
        ) {
            this.props.resetFailedChecks();
        }

        // When content of the editor changes
        //   - close unsaved changes popup if open
        //   - update unsaved changes status
        if (!translation.equals(prevEditor.translation)) {
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

            if (typeof(message) === 'string') {
                return null;
            }

            // Never mutate state.
            const source = message.clone();
            let dest = source;
            // Walk the path until the next to last item.
            for (let i = 0, ln = path.length; i < ln - 1; i++) {
                dest = dest[path[i]];
            }
            // Assign the new value to the last element in the path, so that
            // it is actually assigned to the message object reference and
            // to the extracted value.
            dest[path[path.length - 1]] = value;

            this.props.updateTranslation(source);
        }
    }

    renderElements(
        elements: Array<FluentElement>,
        path: Array<string | number>,
        label: string,
    ): React.Node {
        return elements.map((element, index) => {
            if (element.type !== 'TextElement') {
                return null;
            }

            return <tr key={ `message-value-${index}` }>
                <td>
                    <label htmlFor={ `message-value-${index}` }>{ label }</label>
                </td>
                <td>
                    <textarea
                        id={ `message-value-${index}` }
                        className=""
                        value={ element.value }
                        onChange={
                            this.createHandleChange(
                                [].concat(path, [ index, 'value' ])
                            )
                        }
                    />
                </td>
            </tr>;
        })
    }

    renderValue(value: FluentValue, path: Array<string | number>, label?: string): React.Node {
        if (!value) {
            return null;
        }

        if (!label) {
            label = 'Value';
        }

        return this.renderElements(
            value.elements,
            [].concat(path, [ 'elements' ]),
            label,
        );
    }

    renderAttributes(attributes: ?FluentAttributes, path: Array<string | number>): React.Node {
        if (!attributes) {
            return null;
        }

        return attributes.map((attribute: FluentAttribute, index: number) => {
            return this.renderValue(
                attribute.value,
                [].concat(path, [ index, 'value' ]),
                attribute.id.name,
            );
        });
    }

    render() {
        const message = this.props.editor.translation;

        if (typeof(message) === 'string') {
            return null;
        }

        return <div className="fluent-rich-translation-form">
            <table>
                <tbody>
                    { this.renderValue(message.value, [ 'value' ]) }
                    { this.renderAttributes(message.attributes, [ 'attributes' ]) }
                </tbody>
            </table>
        </div>;
    }
}
