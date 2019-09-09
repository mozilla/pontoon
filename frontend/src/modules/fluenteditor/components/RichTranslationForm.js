/* @flow */

import * as React from 'react';
import { serializeVariantKey } from 'fluent-syntax';

import './RichTranslationForm.css';

import { fluent, withActionsDisabled } from 'core/utils';

import type { EditorProps } from 'core/editor';
import type {
    FluentAttribute,
    FluentAttributes,
    FluentElement,
    FluentMessage,
    FluentValue,
} from 'core/utils/fluent/types';


type MessagePath = Array<string | number>;


type InternalProps = {|
    ...EditorProps,
    isActionDisabled: boolean,
    disableAction: () => void,
|};


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
export class RichTranslationFormBase extends React.Component<InternalProps> {
    // A React ref to the currently focused input, if any.
    focusedElementId: ?string = null;

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
        this.props.updateTranslation(message, true);

        this.focusInput(true);
    }

    componentDidUpdate(prevProps: InternalProps) {
        const editor = this.props.editor;

        // Reset the currently focused element when the entity changes or when
        // the translation changes from an external source (when that happens,
        // it happens to be passed as a string and not a Fluent AST).
        if (
            this.props.entity !== prevProps.entity ||
            typeof(editor.translation) === 'string'
        ) {
            this.focusedElementId = null;
        }

        // If the translation is a string, that means we're in a transitional
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

    update(prevProps: InternalProps, translation: FluentMessage) {
        const prevEditor = prevProps.editor;
        const editor = this.props.editor;

        if (!translation.equals(prevEditor.translation)) {
            // Walks the tree and unify all simple elements into just one.
            const message = fluent.flattenMessage(translation);
            this.props.updateTranslation(message, editor.changeSource !== 'internal');
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

        this.focusInput(editor.changeSource === 'external');
    }

    focusInput(putCursorToStart: boolean) {
        const input = this.getFocusedElement() || this.getFirstInput();

        if (!input) {
            return;
        }

        if (this.props.searchInputFocused) {
            return;
        }

        input.focus();

        if (putCursorToStart) {
            input.setSelectionRange(0, 0);
        }
    }

    getFirstInput() {
        if (this.tableBodyRef.current) {
            return this.tableBodyRef.current.querySelector('textarea:first-of-type');
        }
        return null;
    }

    getFocusedElement() {
        if (this.focusedElementId && this.tableBodyRef.current) {
            return this.tableBodyRef.current.querySelector('textarea#' + this.focusedElementId);
        }
        return null;
    }

    updateTranslationSelectionWith(content: string, translation: FluentMessage) {
        let target = this.getFocusedElement();

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

    handleShortcuts = (event: SyntheticKeyboardEvent<HTMLTextAreaElement>) => {
        const key = event.keyCode;

        let handledEvent = false;

        // On Enter:
        //   - If unsaved changes popup is shown, leave anyway.
        //   - If failed checks popup is shown after approving a translation, approve it anyway.
        //   - In other cases, send current translation.
        if (key === 13 && !event.ctrlKey && !event.shiftKey && !event.altKey) {
            if (this.props.isActionDisabled) {
                event.preventDefault();
                return;
            }
            this.props.disableAction();

            handledEvent = true;

            const errors = this.props.editor.errors;
            const warnings = this.props.editor.warnings;
            const source = this.props.editor.source;
            const ignoreWarnings = !!(errors.length || warnings.length);

            // Leave anyway
            if (this.props.unsavedchanges.shown) {
                this.props.ignoreUnsavedChanges();
            }
            // Approve anyway
            else if (typeof(source) === 'number') {
                this.props.updateTranslationStatus(source, 'approve', ignoreWarnings);
            }
            // Send translation
            else {
                this.props.sendTranslation(ignoreWarnings);
            }
        }

        // On Esc, close unsaved changes and failed checks popups if open.
        if (key === 27) {
            handledEvent = true;

            const errors = this.props.editor.errors;
            const warnings = this.props.editor.warnings;

            // Close unsaved changes popup
            if (this.props.unsavedchanges.shown) {
                this.props.hideUnsavedChanges();
            }
            // Close failed checks popup
            else if (errors.length || warnings.length) {
                this.props.resetFailedChecks();
            }
        }

        // On Ctrl + Shift + C, copy the original translation.
        if (key === 67 && event.ctrlKey && event.shiftKey && !event.altKey) {
            handledEvent = true;
            this.props.copyOriginalIntoEditor();
        }

        // On Ctrl + Shift + Backspace, clear the content.
        if (key === 8 && event.ctrlKey && event.shiftKey && !event.altKey) {
            handledEvent = true;
            this.props.clearEditor();
        }

        // On Tab, walk through current helper tab content and copy it.
        // TODO

        if (handledEvent) {
            event.preventDefault();
        }
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
        this.focusedElementId = event.currentTarget.id;
    }

    renderInput(value: string, path: MessagePath) {
        return <textarea
            id={ `${path.join('-')}` }
            key={ `${path.join('-')}` }
            readOnly={ this.props.isReadOnlyEditor }
            value={ value }
            onChange={ this.createHandleChange(path) }
            onFocus={ this.setFocusedInput }
            onKeyDown={ this.handleShortcuts }
            dir={ this.props.locale.direction }
            lang={ this.props.locale.code }
            data-script={ this.props.locale.script }
        />;
    }

    renderItem(value: string, path: MessagePath, label: string) {
        return <tr key={ `${path.join('-')}` }>
            <td>
                <label htmlFor={ `${path.join('-')}` }>{ label }</label>
            </td>
            <td>
                { this.renderInput(value, path) }
            </td>
        </tr>;
    }

    renderElements(elements: Array<FluentElement>, path: MessagePath, label: string): React.Node {
        return elements.map((element, index) => {
            if (element.type === 'Placeable' && element.expression.type === 'SelectExpression') {
                return element.expression.variants.map((variant, i) => {
                    return this.renderItem(
                        variant.value.elements[0].value,
                        [].concat(
                            path,
                            [ index, 'expression', 'variants', i, 'value', 'elements', 0, 'value' ]
                        ),
                        serializeVariantKey(variant.key),
                    );
                });
            }
            else {
                return this.renderItem(
                    element.value,
                    [].concat(path, [ index, 'value' ]),
                    label,
                );
            }
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


export default withActionsDisabled(RichTranslationFormBase);
