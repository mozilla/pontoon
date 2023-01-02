import { Localized } from '@fluent/react';
import { Message, Pattern, serializeVariantKey, Term } from '@fluent/syntax';
import React, { useContext, useLayoutEffect, useRef } from 'react';

import { EditorActions, EditorData } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { useHandleShortcuts } from '~/core/editor';
import { CLDR_PLURALS } from '~/utils/constants';
import {
  extractAccessKeyCandidates,
  isPluralExpression,
} from '~/utils/message';
import { usePluralExamples } from '~/hooks/usePluralExamples';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { searchBoxHasFocus } from '~/modules/search/components/SearchBox';

import './RichTranslationForm.css';

type MessagePath = Array<string | number>;

function RichLabel({ label, example }: { label: string; example?: number }) {
  return typeof example === 'number' ? (
    <Localized
      id='fluenteditor-RichTranslationForm--plural-example'
      vars={{ example, plural: label }}
      elems={{ stress: <span className='stress' /> }}
    >
      <span className='example'>
        {'{ $plural } (e.g. <stress>{ $example }</stress>)'}
      </span>
    </Localized>
  ) : (
    <span className='label'>{label}</span>
  );
}

function RichItem({
  activeInput,
  attributeName,
  className,
  example,
  id,
  label,
  message,
  userInput,
  value,
}: {
  activeInput: React.MutableRefObject<HTMLTextAreaElement | null>;
  attributeName?: string;
  className?: string;
  example?: number;
  id: string;
  label: string;
  message: Message | Term;
  userInput: React.MutableRefObject<boolean>;
  value: string;
}) {
  const locale = useContext(Locale);
  const { setEditorFromInput } = useContext(EditorActions);
  const readonly = useReadonlyEditor();
  const accessKeyElement = useRef<HTMLTextAreaElement>(null);
  const handleShortcuts = useHandleShortcuts();
  const handleUpdate = (value: string | null) => {
    if (typeof value === 'string') {
      userInput.current = true;
      setEditorFromInput(value);
    }
  };

  const isAccessKey = label.endsWith('accesskey') && value.length < 2;
  const candidates = isAccessKey
    ? extractAccessKeyCandidates(message, label)
    : [];

  const handleAccessKeyClick = readonly
    ? undefined
    : (ev: React.MouseEvent<HTMLButtonElement>) => {
        activeInput.current = accessKeyElement.current;
        handleUpdate(ev.currentTarget.textContent);
      };

  return (
    <tr className={className}>
      <td>
        <label htmlFor={id}>
          {attributeName ? (
            <span>
              <span className='attribute-label'>{attributeName}</span>
              <span className='divider'>&middot;</span>
              <RichLabel label={label} example={example} />
            </span>
          ) : (
            <RichLabel label={label} example={example} />
          )}
        </label>
      </td>
      <td>
        <textarea
          id={id}
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
        {isAccessKey ? (
          <div className='accesskeys'>
            {candidates.map((key) => (
              <button
                className={`key ${key === value ? 'active' : ''}`}
                key={key}
                onClick={handleAccessKeyClick}
              >
                {key}
              </button>
            ))}
          </div>
        ) : null}
      </td>
    </tr>
  );
}

function RichPattern({
  activeInput,
  attributeName,
  message,
  path,
  pattern,
  userInput,
}: {
  activeInput: React.MutableRefObject<HTMLTextAreaElement | null>;
  attributeName?: string;
  message: Message | Term;
  path: MessagePath;
  pattern: Pattern;
  userInput: React.MutableRefObject<boolean>;
}) {
  const locale = useContext(Locale);
  const pluralExamples = usePluralExamples(locale);
  const getExample = (isPlural: boolean, label: string) => {
    const pluralForm = CLDR_PLURALS.indexOf(label);
    return isPlural && pluralExamples && pluralForm >= 0
      ? pluralExamples[pluralForm]
      : undefined;
  };

  let indent = false;
  const items = pattern.elements.map((element, eIndex) => {
    if (
      element.type === 'Placeable' &&
      element.expression.type === 'SelectExpression'
    ) {
      const { expression } = element;
      const isPlural = isPluralExpression(expression);
      const rendered_variants = expression.variants.map((variant, vIndex) => {
        let value: string;
        const element = variant.value.elements[0];
        if (element && element.value && typeof element.value === 'string') {
          value = element.value;
        } else {
          value = '';
        }

        const label = serializeVariantKey(variant.key);
        const example = getExample(isPlural, label);
        const id = path
          .concat([
            eIndex,
            'expression',
            'variants',
            vIndex,
            'value',
            'elements',
            0,
            'value',
          ])
          .join('-');

        return (
          <RichItem
            activeInput={activeInput}
            attributeName={attributeName}
            className={indent ? 'indented' : undefined}
            example={example}
            id={id}
            key={id}
            label={label}
            message={message}
            userInput={userInput}
            value={value}
          />
        );
      });

      indent = false;
      return rendered_variants;
    } else {
      indent = true;
      if (typeof element.value !== 'string') {
        return null;
      }

      const id = path.concat(eIndex, 'value').join('-');
      return (
        <RichItem
          activeInput={activeInput}
          id={id}
          key={id}
          label={attributeName || 'Value'}
          message={message}
          userInput={userInput}
          value={element.value}
        />
      );
    }
  });
  return <>{items}</>;
}

/**
 * Rich Editor for supported Fluent strings.
 *
 * This shows the Fluent translation based on its AST, presenting a nicer
 * interface to the user. The translation is stored as an AST, and changes
 * are made directly to that AST.
 */
export function RichTranslationForm(): null | React.ReactElement<'div'> {
  const { entity } = useContext(EntityView);
  const { activeInput, machinery, value: message } = useContext(EditorData);

  const root = useRef<HTMLTableSectionElement>(null);
  const userInput = useRef(false);

  // Reset the currently focused element when the entity changes or when
  // the translation changes from an external source.
  useLayoutEffect(() => {
    if (userInput.current) {
      userInput.current = false;
    } else {
      activeInput.current ??=
        root.current?.querySelector('textarea:first-of-type') ?? null;
      if (!searchBoxHasFocus()) {
        activeInput.current?.focus();
      }
    }
  }, [entity, machinery, message]);

  // message should always be a Message or a Term
  return message instanceof Message || message instanceof Term ? (
    <div className='fluent-rich-translation-form'>
      <table>
        <tbody ref={root}>
          {message.value ? (
            <RichPattern
              activeInput={activeInput}
              message={message}
              pattern={message.value}
              path={['value', 'elements']}
              userInput={userInput}
            />
          ) : null}
          {message.attributes?.map(({ id, value }, index) =>
            value ? (
              <RichPattern
                activeInput={activeInput}
                attributeName={id.name}
                key={id.name}
                message={message}
                pattern={value}
                path={['attributes', index, 'value', 'elements']}
                userInput={userInput}
              />
            ) : null,
          )}
        </tbody>
      </table>
    </div>
  ) : null;
}
