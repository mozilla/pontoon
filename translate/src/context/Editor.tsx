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
  getPlainMessage,
  MessageEntry,
  parseEntry,
  requiresSourceView,
  serializeEntry,
} from '~/utils/message';
import { messageEntryFromEntityTranslation } from '~/utils/message/fromEntity';
import { specialFormats } from '~/utils/message/specialFormats';
import { pojoEquals } from '~/utils/pojo';

import { EntityView, useActiveTranslation } from './EntityView';
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

  /**
   * @param manual Set `true` when value set due to direct user action
   * @param entry Set `true` when `value` is the source of a full entry (e.g. a
   *   composed Machinery suggestion) that should be parsed and distributed
   *   across all fields rather than inserted into the focused field.
   */
  setEditorFromHelpers(
    value: string,
    sources: SourceType[],
    manual: boolean,
    entry?: boolean,
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

    // Parse a full entry source and distribute its leaves across all editor
    // fields, falling back to a raw source-view field when it can't be parsed.
    // Shared by history restores and composed Machinery copies.
    const distributeEntrySource = (
      prev: EditorData,
      str: string,
    ): EditorData => {
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
            : editMessageEntry(entry);
        } else {
          next.fields = editSource(str);
          next.sourceView = true;
        }
      } else {
        next.fields = editMessageEntry(prev.initial);
        next.fields[0].handle.current.setValue(str);
      }
      next.focusField.current = next.fields[0];
      setResult(buildMessageEntry(next.base, next.fields));
      return next;
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

      setEditorFromHelpers: (str, sources, manual, entry) =>
        setState((prev) => {
          // Composed suggestions carry a full entry source. Outside source view
          // we must parse it and distribute the leaves across all fields rather
          // than dumping the raw syntax into the focused field. Record the plain
          // message as `machinery.translation` so source attribution still
          // matches the saved translation (see `useSendTranslation`).
          if (entry && !prev.sourceView) {
            const next = distributeEntrySource(prev, str);
            return {
              ...next,
              machinery: {
                manual,
                translation: getPlainMessage(str, format),
                sources,
              },
            };
          }
          const { fields, focusField, sourceView } = prev;
          const field = focusField.current ?? fields[0];
          field.handle.current.setValue(str);
          let next = fields.slice();
          if (sourceView) {
            const result = buildMessageEntry(prev.base, fields);
            next = editSource(result ?? str);
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
        setState((prev) => distributeEntrySource(prev, str)),

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
            : buildMessageEntry(base, fields);
          setResult(result);
          return state;
        }),

      toggleSourceView: () =>
        setState((state) => {
          const { base, fields, sourceView } = state;
          if (sourceView) {
            const entry = parseEntryFromFluentSource(base, fields);
            if (entry && !requiresSourceView(entry)) {
              const fields = editMessageEntry(entry);
              state.focusField.current = fields[0];
              setResult(entry);
              return { ...state, base: entry, fields, sourceView: false };
            }
          } else if (format === 'fluent') {
            const entry = buildMessageEntry(base, fields);
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
  }, [format, readonly]);

  useEffect(() => {
    const base = messageEntryFromEntityTranslation(entity, locale);
    const sourceView = requiresSourceView(base);
    const fields = sourceView
      ? editSource(serializeEntry(base))
      : editMessageEntry(base);
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
