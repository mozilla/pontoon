import { Localized } from '@fluent/react';
import { Message, Pattern } from 'messageformat';
import React, { useContext, useLayoutEffect, useRef } from 'react';

import { EditorActions, EditorData } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { useHandleShortcuts } from '~/core/editor';
import {
  extractAccessKeyCandidates,
  findPluralSelectors,
  MessageEntry,
  serializePattern,
} from '~/utils/message';
import { usePluralExamples } from '~/hooks/usePluralExamples';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { searchBoxHasFocus } from '~/modules/search/components/SearchBox';
import { CLDR_PLURALS } from '~/utils/constants';

import './RichTranslationForm.css';

type LabelData = Array<{ label: string; example?: string }>;
type MessagePath = Array<string | number>;

const RichLabel = ({
  htmlFor,
  labels,
}: {
  htmlFor: string;
  labels: LabelData;
}) => (
  <label htmlFor={htmlFor}>
    {labels.map(({ label, example }) =>
      example ? (
        <Localized
          id='fluenteditor-RichTranslationForm--label-with-example'
          key={label}
          vars={{ example, label }}
          elems={{ stress: <span className='stress' /> }}
        >
          <span>
            {label} (e.g. <span className='stress'>{example}</span>)
          </span>
        </Localized>
      ) : (
        <span key={label}>{label}</span>
      ),
    )}
  </label>
);

function RichPattern({
  activeInput,
  attributeName,
  entry,
  labels,
  path,
  pattern,
  userInput,
}: {
  activeInput: React.MutableRefObject<HTMLTextAreaElement | null>;
  attributeName?: string;
  entry: MessageEntry;
  labels: LabelData;
  path: MessagePath;
  pattern: Pattern;
  userInput: React.MutableRefObject<boolean>;
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

  const id = path.join('|');
  const value = serializePattern(pattern);
  const isAccessKey = attributeName?.endsWith('accesskey') && value.length < 2;
  const candidates = isAccessKey
    ? // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      extractAccessKeyCandidates(entry, attributeName!)
    : [];

  const handleAccessKeyClick = readonly
    ? undefined
    : (ev: React.MouseEvent<HTMLButtonElement>) => {
        activeInput.current = accessKeyElement.current;
        handleUpdate(ev.currentTarget.textContent);
      };

  return (
    <tr>
      <td>
        <RichLabel htmlFor={id} labels={labels} />
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

function RichMessage({
  activeInput,
  attributeName,
  entry,
  path,
  message,
  userInput,
}: {
  activeInput: React.MutableRefObject<HTMLTextAreaElement | null>;
  attributeName?: string;
  entry: MessageEntry;
  path: MessagePath;
  message: Message;
  userInput: React.MutableRefObject<boolean>;
}) {
  const locale = useContext(Locale);
  const pluralExamples = usePluralExamples(locale);
  const getExample = (label: string) => {
    const pluralForm = CLDR_PLURALS.indexOf(label);
    return pluralExamples && pluralForm >= 0
      ? pluralExamples[pluralForm]
      : undefined;
  };

  let nameLabel: LabelData;
  if (attributeName) {
    nameLabel = [{ label: attributeName }];
  } else if (entry.attributes?.size) {
    nameLabel = [{ label: 'Value' }];
  } else {
    nameLabel = [];
  }

  switch (message.type) {
    case 'message':
      return (
        <RichPattern
          activeInput={activeInput}
          attributeName={attributeName}
          entry={entry}
          labels={nameLabel}
          path={path}
          pattern={message.pattern}
          userInput={userInput}
        />
      );

    case 'select': {
      const plurals = findPluralSelectors(message);
      const items = message.variants.map(({ keys, value }, index) => {
        const labels = nameLabel.concat(
          keys.map((key, i) => {
            const label = 'value' in key ? key.value : 'other';
            const ex = plurals.includes(i) && getExample(label);
            return typeof ex === 'number'
              ? { label, example: String(ex) }
              : { label };
          }),
        );
        return (
          <RichPattern
            activeInput={activeInput}
            attributeName={attributeName}
            entry={entry}
            key={labels.map((kl) => kl.label).join()}
            labels={labels}
            path={path.concat(index)}
            pattern={value}
            userInput={userInput}
          />
        );
      });
      return <>{items}</>;
    }

    default:
      return null;
  }
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
  const { activeInput, machinery, value: entry } = useContext(EditorData);

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
  }, [entity, machinery, entry]);

  // message should always be a Message or a Term
  return typeof entry !== 'string' && entry ? (
    <div className='fluent-rich-translation-form'>
      <table>
        <tbody ref={root}>
          {entry.value ? (
            <RichMessage
              activeInput={activeInput}
              entry={entry}
              message={entry.value}
              path={['value']}
              userInput={userInput}
            />
          ) : null}
          {entry.attributes
            ? Array.from(entry.attributes).map(([name, value]) =>
                value ? (
                  <RichMessage
                    activeInput={activeInput}
                    attributeName={name}
                    key={name}
                    entry={entry}
                    message={value}
                    path={['attributes', name]}
                    userInput={userInput}
                  />
                ) : null,
              )
            : null}
        </tbody>
      </table>
    </div>
  ) : null;
}
