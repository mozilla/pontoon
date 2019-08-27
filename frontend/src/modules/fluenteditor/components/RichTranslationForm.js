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


type MessagePath = Array<string | number>;


/**
 * Return a clone of a translation with one of its elements replaced with a new
 * value.
 */
function getUpdatedTranslation(
    translation: FluentMessage,
    value: string,
    path: MessagePath,
) {
    // Never mutate state.
    const source = translation.clone();
    let dest = source;
    // Walk the path until the next to last item.
    for (let i = 0, ln = path.length; i < ln - 1; i++) {
        dest = dest[path[i]];
    }
    // Assign the new value to the last element in the path, so that
    // it is actually assigned to the message object reference and
    // to the extracted value.
    dest[path[path.length - 1]] = value;

    return source;
}


/**
 * Render a Rich editor for Fluent string editting.
 */
export default class RichTranslationForm extends React.Component<EditorProps> {
    // A React ref to the currently focused input, if any.
    focusedElement = null;

    tableBodyRef: { current: any } = React.createRef();

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

        // Because of a bug in Flow, we create a new `update` function to
        // which we explicitely pass the translation as a FluentMessage. This
        // avoids having Flow complain about `translation` possibly being a
        // string even if we checked that on the previous lines.
        this.update(prevProps, editor.translation);
    }

    update(prevProps: EditorProps, translation: FluentMessage) {
        const prevEditor = prevProps.editor;
        const editor = this.props.editor;

        // Reset the currently focused element when the entity changes.
        if (this.props.entity !== prevProps.entity) {
            this.focusedElement = null;
        }

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

        // If there is content to add to the editor, do so, then remove
        // the content so it isn't added again.
        // This is an abuse of the redux store, because we want to update
        // the content differently for each Editor type. Thus each Editor
        // implements an `updateTranslationSelectionWith` method and that is
        // used to update the translation.
        if (this.props.editor.selectionReplacementContent) {
            this.updateTranslationSelectionWith(
                this.props.editor.selectionReplacementContent,
                translation,
            );
            this.props.resetSelectionContent();
        }
    }

    getFirstInput() {
        if (this.tableBodyRef.current) {
            return this.tableBodyRef.current.querySelector('textarea:first-of-type');
        }
        return null;
    }

    updateTranslationSelectionWith(content: string, translation: FluentMessage) {
        let target = this.focusedElement;

        // If there is no explicitely focused element, find the first input.
        if (!target) {
            target = this.getFirstInput();
        }

        if (!target) {
            return null;
        }

        const newSelectionPos = target.selectionStart + content.length;

        // Update content in the textarea.
        // $FLOW_IGNORE: Flow doesn't know about this method, but it does exist.
        target.setRangeText(content);

        // Put the cursor right after the newly inserted content.
        target.setSelectionRange(
            newSelectionPos,
            newSelectionPos,
        );

        // Update the state to show the new content in the Editor.
        const value = target.value;
        const path = target.id.split('-');

        const source = getUpdatedTranslation(
            translation,
            value,
            // $FLOW_IGNORE: Bug in Flow, again.
            path
        );
        this.props.updateTranslation(source);
    }

    createHandleChange = (path: MessagePath) => {
        return (event: SyntheticInputEvent<HTMLTextAreaElement>) => {
            const value = event.currentTarget.value;
            const translation = this.props.editor.translation;

            if (typeof(translation) === 'string') {
                return null;
            }

            const source = getUpdatedTranslation(translation, value, path);
            this.props.updateTranslation(source);
        }
    }

    setFocusedInput = (event: SyntheticFocusEvent<HTMLTextAreaElement>) => {
        this.focusedElement = event.currentTarget;
    }

    renderInput(value: string, index: number, path: MessagePath) {
        return <textarea
            id={ `${path.join('-')}` }
            value={ value }
            onChange={ this.createHandleChange(path) }
            onFocus={ this.setFocusedInput }
        />;
    }

    renderElements(
        elements: Array<FluentElement>,
        path: MessagePath,
        label: string,
    ): React.Node {
        return elements.map((element, index) => {
            if (element.type !== 'TextElement') {
                return null;
            }

            const eltPath = [].concat(path, [ index, 'value' ]);

            return <tr key={ `${eltPath.join('-')}` }>
                <td>
                    <label htmlFor={ `${eltPath.join('-')}` }>{ label }</label>
                </td>
                <td>
                    { this.renderInput(element.value, index, eltPath) }
                </td>
            </tr>;
        });
    }

    renderValue(value: FluentValue, path: MessagePath, label?: string): React.Node {
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

    renderAttributes(attributes: ?FluentAttributes, path: MessagePath): React.Node {
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
                <tbody ref={ this.tableBodyRef }>
                    { this.renderValue(message.value, [ 'value' ]) }
                    { this.renderAttributes(message.attributes, [ 'attributes' ]) }
                </tbody>
            </table>
        </div>;
    }
}
