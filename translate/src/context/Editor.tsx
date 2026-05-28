import { CatchallKey, Expression, Markup } from '@mozilla/l10n';
import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import type { SourceType } from '~/api/machinery';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { useTranslationStatus } from '~/modules/entities/useTranslationStatus';
import {
  buildMessageEntry,
  editMessageEntry,
  editSource,
  requiresSourceView,
  getEmptyMessageEntry,
  MessageEntry,
  parseEntry,
  serializeEntry,
} from '~/utils/message';
import { pojoEquals } from '~/utils/pojo';

import { EntityView, useActiveTranslation } from './EntityView';
import { FailedChecksData } from './FailedChecksData';
import { Locale } from './Locale';
import { MachineryTranslations } from './MachineryTranslations';
import { UnsavedActions } from './UnsavedChanges';
import { getMessageEntryFormat } from '../utils/message/getMessageEntryFormat';
import {
  getPlaceholderMap,
  placeholderFormats,
} from '../utils/message/placeholders';

export type EditFieldHandle = {
  get value(): string;
  focus(): void;
  setSelection(text: string): void;
  setValue(text: string): void;
};

export type EditorField = {
  /** An identifier for this field */
  id: string;

  /** Attribute name, or empty for the value */
  name: string;

  /** Selector keys, or empty array for single-pattern messages */
  keys: (string | CatchallKey)[];

  labels: Array<{ label: string; plural: boolean }>;

  handle: React.MutableRefObject<EditFieldHandle>;
};

export type EditorData = Readonly<{
  /**
   * Should match `useContext(EntityView).pk`.
   * If it doesn't, the entity has changed but data isn't updated yet.
   */
  pk: number;

  /** Is a request to send a new translation running? */
  busy: boolean;

  /** Used to reconstruct edited messages */
  base: MessageEntry;

  /** Input fields for the value being edited */
  fields: EditorField[];

  /**
   * The current or most recent field with focus;
   * used as the target of machinery replacements.
   */
  focusField: React.MutableRefObject<EditorField | null>;

  /** Used for detecting unsaved changes */
  initial: MessageEntry;

  placeholders: Map<string, Expression | Markup> | null;

  machinery: {
    manual: boolean;
    sources: SourceType[];
    translation: string;
  } | null;

  sourceView: boolean;
}>;

export type EditorActions = {
  clearEditor(): void;

  setEditorBusy(busy: boolean): void;

  /** If `format: 'fluent'`, must be called with the source of a full entry */
  setEditorFromHistory(value: string): void;

  /** @param manual Set `true` when value set due to direct user action */
  setEditorFromHelpers(
    value: string,
    sources: SourceType[],
    manual: boolean,
  ): void;

  setEditorSelection(content: string): void;

  setResultFromInput(): void;

  toggleSourceView(): void;
};

function parseEntryFromFluentSource(base: MessageEntry, source: string) {
  const entry = parseEntry('fluent', source);
  if (entry) {
    entry.id = base.id;
  }
  return entry;
}

/**
 * Create a new MessageEntry with a simple string pattern `value`,
 * using `id` as its identifier.
 */
const createSimpleMessageEntry = (
  format: string,
  key: string[],
  value: string,
): MessageEntry => ({
  format: getMessageEntryFormat(format),
  id: key[0] ?? '',
  value: value ? [value] : [],
});

const initEditorData: EditorData = {
  pk: 0,
  busy: false,
  base: { format: 'plain', id: '', value: [] },
  focusField: { current: null },
  initial: { format: 'plain', id: '', value: [] },
  placeholders: null,
  machinery: null,
  fields: [],
  sourceView: false,
};

const initEditorActions: EditorActions = {
  clearEditor: () => {},
  setEditorBusy: () => {},
  setEditorFromHelpers: () => {},
  setEditorFromHistory: () => {},
  setEditorSelection: () => {},
  setResultFromInput: () => {},
  toggleSourceView: () => {},
};

export const EditorData = createContext(initEditorData);
export const EditorResult = createContext<MessageEntry | null>(null);
export const EditorActions = createContext(initEditorActions);

export function EditorProvider({ children }: { children: React.ReactElement }) {
  const locale = useContext(Locale);
  const { entity } = useContext(EntityView);
  const { format } = entity;
  const activeTranslation = useActiveTranslation();
  const readonly = useReadonlyEditor();
  const machinery = useContext(MachineryTranslations);
  const { setUnsavedChanges } = useContext(UnsavedActions);
  const { resetFailedChecks } = useContext(FailedChecksData);

  const [state, setState] = useState(initEditorData);
  const [result, setResult] = useState<MessageEntry | null>(null);

  const actions = useMemo<EditorActions>(() => {
    if (readonly) {
      return initEditorActions;
    }
    return {
      clearEditor() {
        setState((state) => {
          // Inside setState() only to access the current `state` value
          for (const field of state.fields) {
            field.handle.current.setValue('');
          }
          return state;
        });
      },

      setEditorBusy: (busy) =>
        setState((prev) => (busy === prev.busy ? prev : { ...prev, busy })),

      setEditorFromHelpers: (str, sources, manual) =>
        setState((prev) => {
          const { fields, focusField, placeholders, sourceView } = prev;
          const field = focusField.current ?? fields[0];
          field.handle.current.setValue(str);
          let next = fields.slice();
          if (sourceView) {
            const result = buildMessageEntry(prev.base, placeholders, fields);
            next = editSource(result);
            focusField.current = next[0];
            setResult(result);
          }
          return {
            ...prev,
            machinery: { manual, translation: str, sources },
            fields: next,
          };
        }),

      setEditorFromHistory: (str) =>
        setState((prev) => {
          const next = { ...prev };
          switch (format) {
            case 'fluent': {
              const entry = parseEntry(format, str);
              if (entry) {
                next.base = entry;
                if (!requiresSourceView(entry)) {
                  next.fields = prev.sourceView
                    ? editSource(entry)
                    : editMessageEntry(entry);
                }
              } else {
                next.fields = editSource(str);
                next.sourceView = true;
              }
              break;
            }
            case 'android':
            case 'gettext':
            case 'webext':
            case 'xcode':
            case 'xliff': {
              const entry = parseEntry(format, str);
              if (entry) {
                next.base = entry;
                next.fields = editMessageEntry(entry);
              } else {
                next.fields = editSource(str);
                next.sourceView = true;
              }
              break;
            }
            default:
              next.fields = editMessageEntry(prev.initial);
              next.fields[0].handle.current.setValue(str);
          }
          next.focusField.current = next.fields[0];
          const result = buildMessageEntry(
            next.base,
            next.placeholders,
            next.fields,
          );
          setResult(result);
          return next;
        }),

      setEditorSelection: (content) =>
        setState((state) => {
          // Inside setState() only to access the current `state` value
          const { fields, focusField } = state;
          const field = focusField.current ?? fields[0];
          field.handle.current.setSelection(content);
          return state;
        }),

      setResultFromInput: () =>
        setState((state) => {
          // Inside setState() only to access the current `state` value
          const { base, fields, placeholders, sourceView } = state;
          const result = sourceView
            ? parseEntryFromFluentSource(base, fields[0].handle.current.value)
            : buildMessageEntry(base, placeholders, fields);
          setResult(result);
          return state;
        }),

      toggleSourceView: () =>
        setState((prev) => {
          if (prev.sourceView) {
            const source = prev.fields[0].handle.current.value;
            const entry = parseEntryFromFluentSource(prev.base, source);
            if (entry && !requiresSourceView(entry)) {
              const fields = editMessageEntry(entry);
              prev.focusField.current = fields[0];
              setResult(entry);
              return { ...prev, base: entry, fields, sourceView: false };
            }
          } else if (format === 'fluent') {
            const entry = buildMessageEntry(
              prev.base,
              prev.placeholders,
              prev.fields,
            );
            const source = serializeEntry(entry);
            const fields = editSource(source);
            prev.focusField.current = fields[0];
            setResult(entry);
            return { ...prev, fields, sourceView: true };
          }
          return prev;
        }),
    };
  }, [format, readonly]);

  useEffect(() => {
    let base: MessageEntry;
    let source = activeTranslation?.string || '';
    let sourceView = false;
    let placeholders: Map<string, Expression | Markup> | null = null;
    let orig: MessageEntry | null = null;
    if (placeholderFormats.has(format)) {
      orig = parseEntry(format, entity.original);
      if (orig?.value) placeholders = getPlaceholderMap(orig.value);
    }
    if (!source) {
      orig ??= parseEntry(format, entity.original);
      base = orig
        ? getEmptyMessageEntry(orig, locale)
        : createSimpleMessageEntry(format, entity.key, '');
      if (requiresSourceView(base)) {
        source = serializeEntry(base);
        sourceView = true;
      }
    } else {
      const base_ = parseEntry(format, source);
      if (base_) {
        base = base_;
        sourceView = requiresSourceView(base);
      } else {
        base = createSimpleMessageEntry(format, entity.key, source);
        sourceView = format === 'fluent';
      }
    }

    const fields = sourceView ? editSource(source) : editMessageEntry(base);

    setState(() => ({
      pk: entity.pk,
      busy: false,
      base,
      fields,
      focusField: { current: fields[0] },
      initial: base,
      placeholders,
      machinery: null,
      sourceView,
    }));
    setResult(base);
  }, [locale, entity, activeTranslation]);

  // For missing entries, fill editor initially with a perfect match from
  // translation memory, if available.
  const status = useTranslationStatus(entity);
  useEffect(() => {
    if (
      status === 'missing' &&
      state.machinery === null &&
      !state.sourceView &&
      state.fields.length === 1 &&
      state.fields[0].handle.current.value === ''
    ) {
      const perfect = machinery.translations.find((tx) => tx.quality === 100);
      if (perfect) {
        actions.setEditorFromHelpers(
          perfect.translation,
          perfect.sources,
          false,
        );
      }
    }
  }, [state, actions, status, machinery.translations]);

  useEffect(() => {
    // Changes in `result` need to be reflected in `UnsavedChanges`,
    // but the latter needs to be defined at a higher level to make it
    // available in `EntitiesList`. Therefore, that state is managed here.
    // Let's also avoid the calculation, unless it's actually required.
    const hasChanges = !pojoEquals(state.initial, result);
    if (hasChanges) {
      resetFailedChecks();
    }
    setUnsavedChanges(() => hasChanges);
  }, [result]);

  return (
    <EditorData.Provider value={state}>
      <EditorResult.Provider value={result}>
        <EditorActions.Provider value={actions}>
          {children}
        </EditorActions.Provider>
      </EditorResult.Provider>
    </EditorData.Provider>
  );
}
