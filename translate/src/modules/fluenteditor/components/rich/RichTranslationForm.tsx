import React, { useContext } from 'react';
import { Localized } from '@fluent/react';
import {
  Entry,
  Message,
  Pattern,
  serializeVariantKey,
  Term,
  Variant,
} from '@fluent/syntax';

import { Locale } from '~/context/locale';
import * as editor from '~/core/editor';
import type { Translation } from '~/core/editor';
import * as entities from '~/core/entities';
import { CLDR_PLURALS } from '~/core/plural';
import { fluent } from '~/core/utils';
import { useAppDispatch, useAppSelector } from '~/hooks';
import { usePluralExamples } from '~/hooks/usePluralExamples';

import './RichTranslationForm.css';

type MessagePath = Array<string | number>;

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

  // This should be `SyntaxNode | SyntaxNode[]`, but using `path` like this is so
  // un-TypeScript that it doesn't really work.
  let dest: any = source;

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

  const accessKeyElementId = React.useRef('');
  const focusedElementId = React.useRef('');

  const dispatch = useAppDispatch();

  const message = useAppSelector((state) => state.editor.translation);
  const changeSource = useAppSelector((state) => state.editor.changeSource);
  const locale = useContext(Locale);
  const isReadOnlyEditor = useAppSelector((state) =>
    entities.selectors.isReadOnlyEditor(state),
  );
  const searchInputFocused = useAppSelector(
    (state) => state.search.searchInputFocused,
  );
  const entity = useAppSelector((state) =>
    entities.selectors.getSelectedEntity(state),
  );
  const unsavedChangesExist = useAppSelector(
    (state) => state.unsavedchanges.exist,
  );
  const pluralExamples = usePluralExamples(locale);

  const tableBody = React.useRef<HTMLTableSectionElement>(null);

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

  const getFirstInput = React.useCallback(
    () => tableBody.current?.querySelector('textarea:first-of-type'),
    [],
  );

  const getFocusedElement = React.useCallback(() => {
    const id = focusedElementId.current;
    const el = tableBody.current;
    return id && el ? el.querySelector(`textarea#${id}`) : null;
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
    focusedElementId.current = '';
  }, [entity, changeSource]);

  // Reset checks when content of the editor changes and some changes have been made.
  React.useEffect(() => {
    if (unsavedChangesExist) {
      dispatch(editor.actions.resetFailedChecks());
    }
  }, [message, dispatch, unsavedChangesExist]);

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

  if (
    typeof message === 'string' ||
    !(message instanceof Message || message instanceof Term)
  ) {
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
      event.currentTarget.textContent ?? '',
      accessKeyElementId.current.split('-'),
    );
  }

  function setFocusedInput(event: React.FocusEvent<HTMLTextAreaElement>) {
    focusedElementId.current = event.currentTarget.id;
  }

  function renderTextarea(
    value: string,
    path: MessagePath,
    maxlength?: number | undefined,
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
        dir={locale.direction}
        lang={locale.code}
        data-script={locale.script}
      />
    );
  }

  function renderAccessKeys(candidates: Array<string>) {
    // Get selected access key
    const id = accessKeyElementId.current;
    const el = tableBody.current;
    let accessKey: string | null = null;
    if (id && el) {
      const accessKeyElement = el.querySelector<HTMLTextAreaElement>(
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
      accessKeyElementId.current = path.join('-');
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
    className?: string | undefined,
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
                <span className='attribute-label'>{attributeName}</span>
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
    pluralExamples: Record<number, number> | null,
    attributeName: string | null | undefined,
  ) {
    let value: string;
    const element = variant.value.elements[0];
    if (element && element.value && typeof element.value === 'string') {
      value = element.value;
    } else {
      value = '';
    }

    const label = serializeVariantKey(variant.key);
    let example = null;
    const pluralForm = CLDR_PLURALS.indexOf(label);

    if (pluralExamples && pluralForm >= 0) {
      example = pluralExamples[pluralForm];
    }

    const path = ePath.concat([
      eIndex,
      'expression',
      'variants',
      vIndex,
      'value',
      'elements',
      0,
      'value',
    ]);
    return renderItem(
      value,
      path,
      label,
      attributeName,
      indent ? 'indented' : undefined,
      example,
    );
  }

  function renderPattern(
    { elements }: Pattern,
    path: MessagePath,
    attributeName?: string,
  ) {
    let indent = false;

    return elements.map((element, eIndex) => {
      if (
        element.type === 'Placeable' &&
        element.expression.type === 'SelectExpression'
      ) {
        const { expression } = element;
        const rendered_variants = expression.variants.map((variant, vIndex) => {
          return renderVariant(
            variant,
            path,
            indent,
            eIndex,
            vIndex,
            fluent.isPluralExpression(expression) ? pluralExamples : null,
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

        return renderItem(element.value, path.concat(eIndex, 'value'), label);
      }
    });
  }

  return (
    <div className='fluent-rich-translation-form'>
      <table>
        <tbody ref={tableBody}>
          {message.value
            ? renderPattern(message.value, ['value', 'elements'])
            : null}
          {message.attributes?.map(({ id, value }, index) =>
            value
              ? renderPattern(
                  value,
                  ['attributes', index, 'value', 'elements'],
                  id.name,
                )
              : null,
          )}
        </tbody>
      </table>
    </div>
  );
}
