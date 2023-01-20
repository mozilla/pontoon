import { Localized } from '@fluent/react';
import React, { useCallback, useContext, useLayoutEffect, useRef } from 'react';

import { EditorActions, EditorData } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { useHandleShortcuts } from '~/core/editor';
import { extractAccessKeyCandidates } from '~/utils/message';
import { usePluralExamples } from '~/hooks/usePluralExamples';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { searchBoxHasFocus } from '~/modules/search/components/SearchBox';
import { CLDR_PLURALS } from '~/utils/constants';

import './RichTranslationForm.css';

const RichLabel = ({
  getExample,
  htmlFor,
  labels,
}: {
  getExample: (label: string) => number | undefined;
  htmlFor: string;
  labels: Array<{ label: string; plural: boolean }>;
}) => (
  <label htmlFor={htmlFor}>
    {labels.map(({ label, plural }) => {
      const example = plural && getExample(label);
      if (typeof example === 'number') {
        return (
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
        );
      } else {
        return <span key={label}>{label}</span>;
      }
    })}
  </label>
);

function RichAccessKeyCandidates({
  active,
  name,
  onClick,
}: {
  active: string;
  name: string;
  onClick: (ev: React.MouseEvent) => void;
}) {
  const { value } = useContext(EditorData);
  const candidates = extractAccessKeyCandidates(value, name);
  return (
    <div className='accesskeys'>
      {candidates.map((key) => (
        <button
          className={`key ${key === active ? 'active' : ''}`}
          key={key}
          onClick={onClick}
        >
          {key}
        </button>
      ))}
    </div>
  );
}

function RichPattern({
  activeInput,
  id,
  name,
  userInput,
  value,
}: {
  activeInput: React.MutableRefObject<HTMLTextAreaElement | null>;
  id: string;
  name: string;
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

  const isAccessKey = name.endsWith('accesskey') && value.length < 2;

  const handleAccessKeyClick = (ev: React.MouseEvent) => {
    if (!readonly) {
      activeInput.current = accessKeyElement.current;
      handleUpdate(ev.currentTarget.textContent);
    }
  };

  return (
    <>
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
        <RichAccessKeyCandidates
          active={value}
          name={name}
          onClick={handleAccessKeyClick}
        />
      ) : null}
    </>
  );
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
  const { activeInput, machinery, value } = useContext(EditorData);

  const root = useRef<HTMLTableSectionElement>(null);
  const userInput = useRef(false);

  const locale = useContext(Locale);
  const pluralExamples = usePluralExamples(locale);
  const getExample = useCallback(
    (label: string) => {
      const pluralForm = CLDR_PLURALS.indexOf(label);
      return pluralExamples && pluralForm >= 0
        ? pluralExamples[pluralForm]
        : undefined;
    },
    [pluralExamples],
  );

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
  }, [entity, machinery, value]);

  return (
    <div className='fluent-rich-translation-form'>
      <table>
        <tbody ref={root}>
          {value.map(({ id, labels, name, value }) => (
            <tr key={id}>
              <td>
                <RichLabel
                  getExample={getExample}
                  htmlFor={id}
                  labels={labels}
                />
              </td>
              <td>
                <RichPattern
                  activeInput={activeInput}
                  id={id}
                  name={name}
                  userInput={userInput}
                  value={value}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
