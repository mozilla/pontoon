import { CatchallKey } from '@mozilla/l10n';
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
  type MessageEntry,
  parseEntry,
  requiresSourceView,
  serializeEntry,
} from '~/utils/message';
import {
  hasOuterWhitespace,
  htmlElementEscapes,
} from '~/utils/message/entryInformation';
import { messageEntryFromEntityTranslation } from '~/utils/message/fromEntity';
import { specialFormats } from '~/utils/message/specialFormats';
import { pojoEquals } from '~/utils/pojo';

import { EntityView, useActiveTranslation, useEntityEntry } from './EntityView';
import { FailedChecksData } from './FailedChecksData';
import { Locale } from './Locale';
import { MachineryTranslations } from './MachineryTranslations';
import { UnsavedActions } from './UnsavedChanges';

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

function parseEntryFromFluentSource(base: MessageEntry, fields: EditorField[]) {
  const source = fields[0].handle.current.value;
  const entry = parseEntry('fluent', source);
  if (entry) {
    entry.id = base.id;
  }
  return entry;
}

const initEditorData: EditorData = {
  pk: 0,
  busy: false,
  base: { format: 'plain', id: '', value: [] },
  focusField: { current: null },
  initial: { format: 'plain', id: '', value: [] },
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
  const sourceEntry = useEntityEntry();
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
    const buildOpts = {
      escapeHTML: htmlElementEscapes(sourceEntry),
      trim: !hasOuterWhitespace(sourceEntry),
    };
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
          const { fields, focusField, sourceView } = prev;
          let field = focusField.current ?? fields[0];
          field.handle.current.setValue(str);
          const next = {
            ...prev,
            machinery: { manual, translation: str, sources },
          } satisfies EditorData;
          if (sourceView) {
            const result = buildMessageEntry(prev.base, prev.fields, buildOpts);
            next.fields = editSource(result ?? str);
            field = focusField.current = next.fields[0];
            setResult(result);
          }
          if (manual) {
            field.handle.current.focus();
          }
          return next;
        }),

      setEditorFromHistory: (str) =>
        setState((prev) => {
          const next = { ...prev };
          if (specialFormats.has(format)) {
            const entry = parseEntry(format, str);
            if (entry) {
              next.base = entry;
            } else if (format !== 'fluent') {
              return prev;
            }
            if (entry && !requiresSourceView(entry)) {
              next.fields = prev.sourceView
                ? editSource(entry)
                : editMessageEntry(sourceEntry, entry);
            } else {
              next.fields = editSource(str);
              next.sourceView = true;
            }
          } else {
            next.fields = editMessageEntry(sourceEntry, prev.initial);
            next.fields[0].handle.current.setValue(str);
          }
          next.focusField.current = next.fields[0];
          const result = buildMessageEntry(next.base, next.fields, buildOpts);
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
          const { base, fields, sourceView } = state;
          const result = sourceView
            ? parseEntryFromFluentSource(base, fields)
            : buildMessageEntry(base, fields, buildOpts);
          setResult(result);
          return state;
        }),

      toggleSourceView: () =>
        setState((state) => {
          const { base, fields, sourceView } = state;
          if (sourceView) {
            const entry = parseEntryFromFluentSource(base, fields);
            if (entry && !requiresSourceView(entry)) {
              const fields = editMessageEntry(sourceEntry, entry);
              state.focusField.current = fields[0];
              setResult(entry);
              return { ...state, base: entry, fields, sourceView: false };
            }
          } else if (format === 'fluent') {
            const entry = buildMessageEntry(base, fields, buildOpts);
            if (entry) {
              const source = serializeEntry(entry);
              const fields = editSource(source);
              state.focusField.current = fields[0];
              setResult(entry);
              return { ...state, fields, sourceView: true };
            }
          }
          return state;
        }),
    };
  }, [format, readonly, sourceEntry]);

  useEffect(() => {
    const base = messageEntryFromEntityTranslation(entity, locale);
    const sourceView = requiresSourceView(base);
    const fields = sourceView
      ? editSource(serializeEntry(base))
      : editMessageEntry(sourceEntry, base);
    setState(() => ({
      pk: entity.pk,
      busy: false,
      base,
      fields,
      focusField: { current: fields[0] },
      initial: base,
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
