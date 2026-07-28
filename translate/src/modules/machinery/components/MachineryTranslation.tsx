import { Localized } from '@fluent/react';
import classNames from 'classnames';
import React, { useCallback, useContext, useRef } from 'react';

import type {
  ComposedMachineryTranslation,
  MachineryTranslation,
  SourceType,
} from '~/api/machinery';
import { logUXAction } from '~/api/uxaction';
import { EditorActions, EditorField } from '~/context/Editor';
import { useMachineryEntry } from '~/context/EntityView';
import { HelperSelection } from '~/context/HelperSelection';
import { Locale } from '~/context/Locale';
import { GenericTranslation } from '~/modules/translation';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { useScrollOnSelect } from '~/hooks/useScrollOnSelect';
import {
  editMessageEntry,
  requiresSourceView,
  serializeEntry,
  type MessageEntry,
} from '~/utils/message';
import { createMessageEntry } from '~/utils/message/createMessageEntry';

import { ConcordanceSearch } from './ConcordanceSearch';
import { MachineryTranslationSource } from './MachineryTranslationSource';
import { useLLMTranslation } from '~/context/TranslationContext';

import './ConcordanceSearch.css';
import './MachineryTranslation.css';

type Props = {
  sourceString: string;
  translation: MachineryTranslation;
  index: number;
};

/**
 * Render a Translation in the Machinery tab.
 *
 * Shows the original string and the translation, as well as a list of sources.
 * Similar translations (same original and translation) are shown only once
 * and their sources are merged.
 */
export function MachineryTranslationComponent({
  index,
  sourceString,
  translation,
}: Props): React.ReactElement<React.ElementType> {
  const { setEditorFromHelpers } = useContext(EditorActions);
  const { element, setElement } = useContext(HelperSelection);
  const isSelected = element === index;

  const getLLMTranslationState = useLLMTranslation();
  const { llmTranslation } = getLLMTranslationState(translation);

  const locale = useContext(Locale);

  const copyTranslationIntoEditor = useCallback(() => {
    if (window.getSelection()?.isCollapsed !== false) {
      setElement(index);
      let content = llmTranslation || translation.translation;
      // FIXME: https://bugzilla.mozilla.org/show_bug.cgi?id=2055465
      // Should just strip these out;
      // CodeMirror will throw an error if we leave any CR in the value.
      content = content.replaceAll('\r', '\\r');
      const sources: SourceType[] = llmTranslation
        ? ['gpt-transform']
        : translation.sources;
      setEditorFromHelpers(content, sources, true);
      if (llmTranslation) {
        logUXAction('LLM Translation Copied', 'LLM Feature Adoption', {
          action: 'Copy LLM Translation',
          localeCode: locale.code,
        });
      }
    }
  }, [index, setEditorFromHelpers, translation, llmTranslation]);

  const className = classNames(
    'translation',
    useReadonlyEditor() && 'cannot-copy',
    isSelected && 'selected',
  );

  const translationRef = useRef<HTMLLIElement>(null);
  useScrollOnSelect(translationRef, isSelected);

  return (
    <Localized id='machinery-Translation--copy' attrs={{ title: true }}>
      <li
        className={className}
        title='Copy Into Translation (Ctrl + Shift + Down)'
        onClick={copyTranslationIntoEditor}
        ref={translationRef}
      >
        {translation.sources.includes('concordance-search') ? (
          <ConcordanceSearch
            sourceString={sourceString}
            translation={translation}
          />
        ) : (
          <MachineryTranslationSuggestion
            sourceString={sourceString}
            translation={translation}
          />
        )}
      </li>
    </Localized>
  );
}

function MachineryTranslationSuggestion({
  sourceString,
  translation,
}: {
  sourceString: string;
  translation: MachineryTranslation;
}) {
  const { code, direction, script } = useContext(Locale);

  const getLLMTranslationState = useLLMTranslation();
  const { llmTranslation, loading } = getLLMTranslationState(translation);

  return (
    <>
      <header>
        {translation.quality && (
          <span className='quality'>{translation.quality + '%'}</span>
        )}

        <MachineryTranslationSource translation={translation} />
      </header>
      <p className='original'>
        <GenericTranslation
          content={translation.original}
          diffTarget={
            // Caighdean takes `gd` translations as input, so we shouldn't
            // diff it against the `en-US` source string.
            translation.sources.includes('caighdean') ? undefined : sourceString
          }
        />
      </p>
      <p
        className='suggestion'
        dir={direction}
        data-script={script}
        lang={code}
      >
        {loading ? (
          <i className='fas fa-circle-notch fa-spin' />
        ) : (
          <GenericTranslation
            content={llmTranslation || translation.translation}
          />
        )}
      </p>
    </>
  );
}

/**
 * Render a composed multi-value suggestion in the Machinery tab.
 *
 * A composed suggestion carries the whole `(value, properties)` data model, so
 * it's shown as labeled fields (source above, suggestion below) and copied
 * across all editor fields at once.
 */
export function ComposedTranslationComponent({
  index,
  translation,
}: {
  index: number;
  translation: ComposedMachineryTranslation;
}): React.ReactElement<React.ElementType> {
  const { setEditorFromComposed } = useContext(EditorActions);
  const { element, setElement } = useContext(HelperSelection);
  const isSelected = element === index;

  const copyIntoEditor = useCallback(() => {
    if (window.getSelection()?.isCollapsed !== false) {
      setElement(index);
      setEditorFromComposed(
        translation.value,
        translation.properties,
        translation.sources,
        true,
      );
    }
  }, [index, setEditorFromComposed, setElement, translation]);

  const className = classNames(
    'translation',
    useReadonlyEditor() && 'cannot-copy',
    isSelected && 'selected',
  );

  const translationRef = useRef<HTMLLIElement>(null);
  useScrollOnSelect(translationRef, isSelected);

  return (
    <Localized id='machinery-Translation--copy' attrs={{ title: true }}>
      <li
        className={className}
        title='Copy Into Translation (Ctrl + Shift + Down)'
        onClick={copyIntoEditor}
        ref={translationRef}
      >
        <ComposedSuggestion translation={translation} />
      </li>
    </Localized>
  );
}

function ComposedSuggestion({
  translation,
}: {
  translation: ComposedMachineryTranslation;
}) {
  const { code, direction, script } = useContext(Locale);
  const machineryEntry = useMachineryEntry();
  const suggestionEntry = createMessageEntry(
    machineryEntry.format,
    machineryEntry.id,
    translation.value,
    translation.properties,
  );

  const originalFields = richFields(machineryEntry);
  const suggestionFields = richFields(suggestionEntry);

  return (
    <>
      <header>
        {translation.quality && (
          <span className='quality'>{translation.quality + '%'}</span>
        )}

        <MachineryTranslationSource translation={translation} composed />
      </header>
      {originalFields ? (
        <RichMessage className='original' fields={originalFields} />
      ) : (
        <p className='original'>
          <GenericTranslation content={serializeEntry(machineryEntry)} />
        </p>
      )}
      {suggestionFields ? (
        <RichMessage
          className='suggestion'
          fields={suggestionFields}
          dir={direction}
          script={script}
          lang={code}
        />
      ) : (
        <p
          className='suggestion'
          dir={direction}
          data-script={script}
          lang={code}
        >
          <GenericTranslation content={serializeEntry(suggestionEntry)} />
        </p>
      )}
    </>
  );
}

/**
 * Fields of a message entry, or `null` when it can't be shown as a rich
 * multi-field view (source-view-only entry, or a single field — in which case
 * the plain rendering is used).
 *
 * Reuses `editMessageEntry()` so this read-only view splits an entry into
 * labeled rows exactly as the editor splits it into inputs; the two must agree,
 * because clicking the row copies it into those inputs. The editor handles it
 * builds are unused here.
 */
function richFields(entry: MessageEntry): EditorField[] | null {
  if (requiresSourceView(entry)) {
    return null;
  }
  const fields = editMessageEntry(entry);
  return fields.length > 1 ? fields : null;
}

/** Render a parsed message as a labeled table, mirroring the original string panel. */
function RichMessage({
  className,
  fields,
  dir,
  lang,
  script,
}: {
  className: string;
  fields: EditorField[];
  dir?: string;
  lang?: string;
  script?: string;
}): React.ReactElement<'table'> {
  return (
    <table
      className={`fluent-rich-string ${className}`}
      dir={dir}
      data-script={script}
      lang={lang}
    >
      <tbody>
        {fields.map(({ handle, id, labels }) => (
          <tr key={id}>
            <td>
              <label>
                {labels.map(({ label }) => (
                  <span key={label}>{label}</span>
                ))}
              </label>
            </td>
            <td>
              <span>
                <GenericTranslation content={handle.current.value} />
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
