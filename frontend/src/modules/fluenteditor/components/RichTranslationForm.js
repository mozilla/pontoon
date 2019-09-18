/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';
import { serializeVariantKey } from 'fluent-syntax';

import './RichTranslationForm.css';

import * as locale from 'core/locale';
import { CLDR_PLURALS } from 'core/plural';
import { fluent } from 'core/utils';

import type { EditorProps } from 'core/editor';
import type {
    FluentAttribute,
    FluentAttributes,
    FluentMessage,
    Pattern,
    PatternElement,
    Variant,
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
 * Render a Rich editor for Fluent string editing.
 */
export default class RichTranslationForm extends React.Component<EditorProps> {
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

    componentDidUpdate(prevProps: EditorProps) {
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

    update(prevProps: EditorProps, translation: FluentMessage) {
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
        this.props.handleShortcuts(
            event,
            this.props.sendTranslation,
            this.props.clearEditor,
            this.props.copyOriginalIntoEditor,
        );
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

    renderInput(value: string, path: MessagePath, maxlength: ?number) {
        return <textarea
            id={ `${path.join('-')}` }
            key={ `${path.join('-')}` }
            readOnly={ this.props.isReadOnlyEditor }
            value={ value }
            maxLength={ maxlength }
            onChange={ this.createHandleChange(path) }
            onFocus={ this.setFocusedInput }
            onKeyDown={ this.handleShortcuts }
            dir={ this.props.locale.direction }
            lang={ this.props.locale.code }
            data-script={ this.props.locale.script }
        />;
    }

    renderLabel(label: string, example: number) {
        return <Localized
            id="fluenteditor-RichTranslationForm--plural-example"
            $example={ example }
            $plural={ label }
            stress={ <span className="stress" /> }
        >
            <span className="example">
                { '{ $plural } (e.g. <stress>{ $example }</stress>)' }
            </span>
        </Localized>
    }

    renderItem(
        value: string,
        path: MessagePath,
        label: string,
        className: ?string,
        example: ?number,
    ) {
        const maxlength = (label === 'accesskey') ? 1 : null;
        return <tr key={ `${path.join('-')}` } className={ className }>
            <td>
                <label htmlFor={ `${path.join('-')}` }>
                    { typeof(example) === 'number' ?
                        this.renderLabel(label, example)
                        :
                        <span>{ label }</span>
                    }
                </label>
            </td>
            <td>
                { this.renderInput(value, path, maxlength) }
            </td>
        </tr>;
    }

    renderVariant(
        variant: Variant,
        ePath: MessagePath,
        indent: boolean,
        eIndex: number,
        vIndex: number,
        pluralExamples: any,
    ): React.Node {
        const element = variant.value.elements[0];
        if (element.value === null) {
            return null;
        }

        const value = element.value;
        if (typeof(value) !== 'string') {
            return null;
        }

        const label = serializeVariantKey(variant.key);
        let example = null;
        const pluralForm = CLDR_PLURALS.indexOf(label);

        if (pluralExamples && pluralForm >= 0) {
            example = pluralExamples[pluralForm];
        }

        const vPath = [eIndex, 'expression', 'variants', vIndex, 'value', 'elements', 0, 'value'];

        return this.renderItem(
            value,
            [].concat(ePath, vPath),
            label,
            indent ? 'indented' : null,
            example,
        );
    }

    renderElements(elements: Array<PatternElement>, path: MessagePath, label: string): React.Node {
        let indent = false;

        return elements.map((element, eIndex) => {
            if (
                element.type === 'Placeable' &&
                element.expression && element.expression.type === 'SelectExpression'
            ) {
                let pluralExamples = null;
                if (fluent.isPluralExpression(element.expression)) {
                    pluralExamples = locale.getPluralExamples(this.props.locale);
                }
                const variants = element.expression.variants.map((variant, vIndex) => {
                    return this.renderVariant(
                        variant,
                        path,
                        indent,
                        eIndex,
                        vIndex,
                        pluralExamples,
                    );
                });

                indent = false;
                return variants;
            }
            else {
                indent = true;
                if (typeof(element.value) !== 'string') {
                    return null;
                }

                return this.renderItem(
                    element.value,
                    [].concat(path, [ eIndex, 'value' ]),
                    label,
                );
            }
        });
    }

    renderValue(value: Pattern, path: MessagePath, label?: string): React.Node {
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
