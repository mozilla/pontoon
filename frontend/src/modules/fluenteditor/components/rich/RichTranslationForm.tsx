import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Localized } from '@fluent/react';
import { serializeVariantKey } from '@fluent/syntax';

import './RichTranslationForm.css';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import * as locale from 'core/locale';
import { CLDR_PLURALS } from 'core/plural';
import { fluent } from 'core/utils';

import type { Translation } from 'core/editor';
import type { Attribute, Entry } from '@fluent/syntax';
import type {
    Pattern,
    PatternElement,
    Variant,
    SyntaxNode,
} from '@fluent/syntax';

type MessagePath = Array<string | number>;
type Child = SyntaxNode | Array<SyntaxNode>;

/**
 * Return a clone of a translation with one of its elements replaced with a new
 * value.
 */
function getUpdatedTranslation(
    translation: Entry,
    value: string,
    path: MessagePath,
) {
    // Never mutate state.
    const source = translation.clone();
    // Safeguard against all the entry types, keep cloning, though.
    if (source.type !== 'Message' && source.type !== 'Term') {
        return source;
    }
    let dest: Child = source;
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

type Props = {
    clearEditor: () => void;
    copyOriginalIntoEditor: () => void;
    sendTranslation: (ignoreWarnings?: boolean) => void;
    updateTranslation: (translation: Translation) => void;
};

/**
 * Render a Rich editor for Fluent string editing.
 */
export default function RichTranslationForm(
    props: Props,
): null | React.ReactElement<'div'> {
    const {
        clearEditor,
        copyOriginalIntoEditor,
        sendTranslation,
        updateTranslation,
    } = props;

    const accessKeyElementIdRef = React.useRef(null);
    const focusedElementIdRef = React.useRef(null);

    const dispatch = useDispatch();

    const message = useSelector((state) => state.editor.translation);
    const changeSource = useSelector((state) => state.editor.changeSource);
    const localeState = useSelector((state) => state.locale);
    const isReadOnlyEditor = useSelector((state) =>
        entities.selectors.isReadOnlyEditor(state),
    );
    const searchInputFocused = useSelector(
        (state) => state.search.searchInputFocused,
    );
    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );

    const tableBodyRef: { current: any } = React.useRef();

    const handleShortcutsFn = editor.useHandleShortcuts();

    const updateRichTranslation = React.useCallback(
        (value: string, path: MessagePath) => {
            if (typeof message === 'string') {
                return;
            }

            const source = getUpdatedTranslation(message, value, path);
            updateTranslation(source);
        },
        [message, updateTranslation],
    );

    const getFirstInput = React.useCallback(() => {
        if (tableBodyRef.current) {
            return tableBodyRef.current.querySelector('textarea:first-of-type');
        }
        return null;
    }, []);

    const getFocusedElement = React.useCallback(() => {
        if (focusedElementIdRef.current && tableBodyRef.current) {
            return tableBodyRef.current.querySelector(
                'textarea#' + focusedElementIdRef.current,
            );
        }
        return null;
    }, []);

    // Replace selected content on external actions (for example, when a user clicks
    // on a placeable).
    editor.useReplaceSelectionContent((content: string, source: string) => {
        // If there is no explicitely focused element, find the first input.
        const target = getFocusedElement() || getFirstInput();

        if (!target) {
            return;
        }

        if (source === 'machinery') {
            // Replace the whole content instead of just what was selected.
            target.select();
        }

        const newSelectionPos = target.selectionStart + content.length;

        // Update content in the textarea.
        target.setRangeText(content);

        // Put the cursor right after the newly inserted content.
        target.setSelectionRange(newSelectionPos, newSelectionPos);

        // Update the state to show the new content in the Editor.
        updateRichTranslation(target.value, target.id.split('-'));
    });

    // Reset the currently focused element when the entity changes or when
    // the translation changes from an external source.
    React.useEffect(() => {
        if (changeSource === 'internal') {
            return;
        }
        focusedElementIdRef.current = null;
    }, [entity, changeSource]);

    // Walks the tree and unify all simple elements into just one.
    React.useEffect(() => {
        if (typeof message === 'string') {
            return;
        }
        const flatMessage = fluent.flattenMessage(message);
        if (!flatMessage.equals(message)) {
            updateTranslation(flatMessage);
        }
    }, [entity, message, updateTranslation]);

    // Reset checks when content of the editor changes.
    React.useEffect(() => {
        dispatch(editor.actions.resetFailedChecks());
    }, [message, dispatch]);

    // When content of the translation changes, update unsaved changes.
    editor.useUpdateUnsavedChanges(false);

    // Put focus on input.
    React.useEffect(() => {
        const input = getFocusedElement() || getFirstInput();

        if (!input || searchInputFocused) {
            return;
        }

        input.focus();

        const putCursorToStart = changeSource !== 'internal';
        if (putCursorToStart) {
            input.setSelectionRange(0, 0);
        }
    }, [
        message,
        changeSource,
        searchInputFocused,
        getFocusedElement,
        getFirstInput,
    ]);

    if (typeof message === 'string') {
        // This is a transitional state, and this editor is not able to handle a
        // non-Fluent message translation. Thus we abort this render and wait for the
        // next one.
        return null;
    }

    function handleShortcuts(event: React.KeyboardEvent<HTMLTextAreaElement>) {
        handleShortcutsFn(
            event,
            sendTranslation,
            clearEditor,
            copyOriginalIntoEditor,
        );
    }

    function createHandleChange(path: MessagePath) {
        return (event: React.SyntheticEvent<HTMLTextAreaElement>) => {
            updateRichTranslation(event.currentTarget.value, path);
        };
    }

    function handleAccessKeyClick(event: React.MouseEvent<HTMLButtonElement>) {
        if (isReadOnlyEditor) {
            return null;
        }

        updateRichTranslation(
            event.currentTarget.textContent,
            accessKeyElementIdRef.current.split('-'),
        );
    }

    function setFocusedInput(event: React.FocusEvent<HTMLTextAreaElement>) {
        focusedElementIdRef.current = event.currentTarget.id;
    }

    function renderTextarea(
        value: string,
        path: MessagePath,
        maxlength?: number | null | undefined,
    ) {
        return (
            <textarea
                id={`${path.join('-')}`}
                key={`${path.join('-')}`}
                readOnly={isReadOnlyEditor}
                value={value}
                maxLength={maxlength}
                onChange={createHandleChange(path)}
                onFocus={setFocusedInput}
                onKeyDown={handleShortcuts}
                dir={localeState.direction}
                lang={localeState.code}
                data-script={localeState.script}
            />
        );
    }

    function renderAccessKeys(candidates: Array<string>) {
        // Get selected access key
        const id = accessKeyElementIdRef.current;
        let accessKey = null;
        if (id && tableBodyRef.current) {
            const accessKeyElement = tableBodyRef.current.querySelector(
                'textarea#' + id,
            );
            if (accessKeyElement) {
                accessKey = accessKeyElement.value;
            }
        }

        return (
            <div className='accesskeys'>
                {candidates.map((key, i) => (
                    <button
                        className={`key ${key === accessKey ? 'active' : ''}`}
                        key={i}
                        onClick={handleAccessKeyClick}
                    >
                        {key}
                    </button>
                ))}
            </div>
        );
    }

    function renderLabel(label: string, example: number) {
        return (
            <Localized
                id='fluenteditor-RichTranslationForm--plural-example'
                vars={{
                    example,
                    plural: label,
                }}
                elems={{ stress: <span className='stress' /> }}
            >
                <span className='example'>
                    {'{ $plural } (e.g. <stress>{ $example }</stress>)'}
                </span>
            </Localized>
        );
    }

    function renderInput(value: string, path: MessagePath, label: string) {
        let candidates = null;
        if (typeof message !== 'string' && label === 'accesskey') {
            candidates = fluent.extractAccessKeyCandidates(message);
        }

        // Access Key UI
        if (candidates && candidates.length && value.length < 2) {
            accessKeyElementIdRef.current = path.join('-');
            return (
                <td>
                    {renderTextarea(value, path, 1)}
                    {renderAccessKeys(candidates)}
                </td>
            );
        }

        // Default UI
        else {
            return <td>{renderTextarea(value, path)}</td>;
        }
    }

    function renderItem(
        value: string,
        path: MessagePath,
        label: string,
        attributeName?: string | null | undefined,
        className?: string | null | undefined,
        example?: number | null | undefined,
    ) {
        return (
            <tr key={`${path.join('-')}`} className={className}>
                <td>
                    <label htmlFor={`${path.join('-')}`}>
                        {typeof example === 'number' ? (
                            renderLabel(label, example)
                        ) : attributeName ? (
                            <span>
                                <span className='attribute-label'>
                                    {attributeName}
                                </span>
                                <span className='divider'>&middot;</span>
                                <span className='label'>{label}</span>
                            </span>
                        ) : (
                            <span>{label}</span>
                        )}
                    </label>
                </td>
                {renderInput(value, path, label)}
            </tr>
        );
    }

    function renderVariant(
        variant: Variant,
        ePath: MessagePath,
        indent: boolean,
        eIndex: number,
        vIndex: number,
        pluralExamples: any,
        attributeName: string | null | undefined,
    ) {
        const element = variant.value.elements[0];
        if (element.value === null) {
            return null;
        }

        const value = element.value;
        if (typeof value !== 'string') {
            return null;
        }

        const label = serializeVariantKey(variant.key);
        let example = null;
        const pluralForm = CLDR_PLURALS.indexOf(label);

        if (pluralExamples && pluralForm >= 0) {
            example = pluralExamples[pluralForm];
        }

        const vPath = [
            eIndex,
            'expression',
            'variants',
            vIndex,
            'value',
            'elements',
            0,
            'value',
        ];

        return renderItem(
            value,
            [].concat(ePath, vPath),
            label,
            attributeName,
            indent ? 'indented' : null,
            example,
        );
    }

    function renderElements(
        elements: Array<PatternElement>,
        path: MessagePath,
        attributeName: string | null | undefined,
    ) {
        let indent = false;

        return elements.map((element, eIndex) => {
            let expression;
            if (
                element.type === 'Placeable' &&
                (expression = element.expression) &&
                expression.type === 'SelectExpression'
            ) {
                const variants = expression.variants;
                let pluralExamples = null;
                if (fluent.isPluralExpression(expression)) {
                    pluralExamples = locale.getPluralExamples(localeState);
                }
                const rendered_variants = variants.map((variant, vIndex) => {
                    return renderVariant(
                        variant,
                        path,
                        indent,
                        eIndex,
                        vIndex,
                        pluralExamples,
                        attributeName,
                    );
                });

                indent = false;
                return rendered_variants;
            } else {
                // When rendering Message attribute, set label to attribute name.
                // When rendering Message value, set label to "Value".
                const label = attributeName || 'Value';

                indent = true;
                if (typeof element.value !== 'string') {
                    return null;
                }

                return renderItem(
                    element.value,
                    [].concat(path, [eIndex, 'value']),
                    label,
                );
            }
        });
    }

    function renderValue(
        value: Pattern,
        path: MessagePath,
        attributeName?: string,
    ) {
        if (!value) {
            return null;
        }

        return renderElements(
            value.elements,
            [].concat(path, ['elements']),
            attributeName,
        );
    }

    function renderAttributes(
        attributes: Array<Attribute> | null | undefined,
        path: MessagePath,
    ) {
        if (!attributes) {
            return null;
        }

        return attributes.map((attribute, index) => {
            return renderValue(
                attribute.value,
                [].concat(path, [index, 'value']),
                attribute.id.name,
            );
        });
    }

    return (
        <div className='fluent-rich-translation-form'>
            <table>
                <tbody ref={tableBodyRef}>
                    {renderValue(message.value, ['value'])}
                    {renderAttributes(message.attributes, ['attributes'])}
                </tbody>
            </table>
        </div>
    );
}
