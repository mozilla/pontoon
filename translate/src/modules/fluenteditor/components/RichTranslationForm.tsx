import { Localized } from '@fluent/react';
import {
  Message,
  Pattern,
  serializeVariantKey,
  Term,
  Variant,
} from '@fluent/syntax';
import React, { useContext, useLayoutEffect, useRef } from 'react';

import { EditorActions, EditorData } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { useHandleShortcuts } from '~/core/editor';
import { CLDR_PLURALS } from '~/core/utils/constants';
import {
  extractAccessKeyCandidates,
  isPluralExpression,
} from '~/core/utils/fluent';
import { useAppSelector } from '~/hooks';
import { usePluralExamples } from '~/hooks/usePluralExamples';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import './RichTranslationForm.css';

type MessagePath = Array<string | number>;

/**
 * Rich Editor for supported Fluent strings.
 *
 * This shows the Fluent translation based on its AST, presenting a nicer
 * interface to the user. The translation is stored as an AST, and changes
 * are made directly to that AST.
 */
export function RichTranslationForm(): null | React.ReactElement<'div'> {
  const locale = useContext(Locale);
  const readonly = useReadonlyEditor();
  const searchInputFocused = useAppSelector(
    (state) => state.search.searchInputFocused,
  );
  const { entity } = useContext(EntityView);
  const pluralExamples = usePluralExamples(locale);
  const { setEditorFromInput } = useContext(EditorActions);
  const { activeInput, value: message } = useContext(EditorData);

  const root = useRef<HTMLTableSectionElement>(null);
  const accessKeyElement = useRef<HTMLTextAreaElement>(null);
  const userInput = useRef(false);

  const handleShortcuts = useHandleShortcuts();

  const handleUpdate = (value: string | null) => {
    if (typeof value === 'string') {
      userInput.current = true;
      setEditorFromInput(value);
    }
  };

  // Reset the currently focused element when the entity changes or when
  // the translation changes from an external source.
  useLayoutEffect(() => {
    if (userInput.current) {
      userInput.current = false;
    } else {
      activeInput.current ??=
        root.current?.querySelector('textarea:first-of-type') ?? null;
      if (activeInput.current && !searchInputFocused) {
        activeInput.current.focus();
        activeInput.current.setSelectionRange(0, 0);
      }
    }
  }, [entity, message]);

  if (
    typeof message === 'string' ||
    !(message instanceof Message || message instanceof Term)
  ) {
    // This is a transitional state, and this editor is not able to handle a
    // non-Fluent message translation. Thus we abort this render and wait for the
    // next one.
    return null;
  }

  function renderTextarea(
    value: string,
    path: MessagePath,
    isAccessKey: boolean,
  ) {
    return (
      <textarea
        id={`${path.join('-')}`}
        key={`${path.join('-')}`}
        ref={isAccessKey ? accessKeyElement : undefined}
        readOnly={readonly}
        value={value}
        maxLength={isAccessKey ? 1 : undefined}
        onChange={(ev) => handleUpdate(ev.currentTarget.value)}
        onFocus={(ev) => (activeInput.current = ev.currentTarget)}
        onKeyDown={(ev) => handleShortcuts(ev)}
        dir={locale.direction}
        lang={locale.code}
        data-script={locale.script}
      />
    );
  }

  function renderAccessKeys(value: string, candidates: string[]) {
    const handleClick = readonly
      ? undefined
      : (ev: React.MouseEvent<HTMLButtonElement>) => {
          activeInput.current = accessKeyElement.current;
          handleUpdate(ev.currentTarget.textContent);
        };

    return (
      <div className='accesskeys'>
        {candidates.map((key) => (
          <button
            className={`key ${key === value ? 'active' : ''}`}
            key={key}
            onClick={handleClick}
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
    const candidates =
      typeof message !== 'string' && label === 'accesskey'
        ? extractAccessKeyCandidates(message)
        : null;

    // Access Key UI
    if (candidates?.length && value.length < 2) {
      return (
        <td>
          {renderTextarea(value, path, true)}
          {renderAccessKeys(value, candidates)}
        </td>
      );
    } else {
      // Default UI
      return <td>{renderTextarea(value, path, false)}</td>;
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
            isPluralExpression(expression) ? pluralExamples : null,
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
        <tbody ref={root}>
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
