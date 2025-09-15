import type { Model } from 'messageformat';
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
  keys: Model.Variant['keys'];

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
  entry: MessageEntry;

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

export type EditorResult = Array<{
  /** Attribute name, or empty for the value */
  name: string;

  /** Selector keys, or empty array for single-pattern messages */
  keys: Model.Variant['keys'];

  /**
   * A flattened representation of a single message pattern,
   * which may contain syntactic representations of placeholders.
   */
  value: string;
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

  /** Set the result value of the active input */
  setResultFromInput(idx: number, value: string): void;

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
  key: string[],
  value: string,
): MessageEntry => ({
  id: key[0] ?? '',
  value: { type: 'message', declarations: [], pattern: [value] },
});

const initEditorData: EditorData = {
  pk: 0,
  busy: false,
  entry: { id: '', value: null, attributes: new Map() },
  focusField: { current: null },
  initial: { id: '', value: null, attributes: new Map() },
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
export const EditorResult = createContext<EditorResult>([]);
export const EditorActions = createContext(initEditorActions);

const buildResult = (message: EditorField[]): EditorResult =>
  message.map(({ handle, keys, name }) => ({
    name,
    keys,
    value: handle.current.value,
  }));

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
  const [result, setResult] = useState<EditorResult>([]);

  const actions = useMemo<EditorActions>(() => {
    if (readonly) {
      return initEditorActions;
    }
    return {
      clearEditor() {
        setState((state) => {
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
          const field = focusField.current ?? fields[0];
          field.handle.current.setValue(str);
          let next = fields.slice();
          if (sourceView) {
            const result = buildResult(next);
            next = editSource(buildMessageEntry(prev.entry, result));
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
          if (format === 'fluent' || format === 'gettext') {
            const entry = parseEntry(format, str);
            if (entry) {
              next.entry = entry;
            }
            if (entry && !requiresSourceView(format, entry)) {
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
          setResult(buildResult(next.fields));
          return next;
        }),

      setEditorSelection: (content) =>
        setState((state) => {
          const { fields, focusField } = state;
          const field = focusField.current ?? fields[0];
          field.handle.current.setSelection(content);
          return state;
        }),

      setResultFromInput: (idx, value) =>
        setResult((prev) => {
          if (prev.length > idx) {
            const res = prev.slice();
            res[idx] = { ...res[idx], value };
            return res;
          } else {
            return prev;
          }
        }),

      toggleSourceView: () =>
        setState((prev) => {
          if (prev.sourceView) {
            const source = prev.fields[0].handle.current.value;
            const entry = parseEntryFromFluentSource(prev.entry, source);
            if (entry && !requiresSourceView(format, entry)) {
              const fields = editMessageEntry(entry);
              prev.focusField.current = fields[0];
              setResult(buildResult(fields));
              return { ...prev, entry, fields, sourceView: false };
            }
          } else if (format === 'fluent') {
            const entry = buildMessageEntry(
              prev.entry,
              buildResult(prev.fields),
            );
            const source = serializeEntry('fluent', entry);
            const fields = editSource(source);
            prev.focusField.current = fields[0];
            setResult(buildResult(fields));
            return { ...prev, fields, sourceView: true };
          }
          return prev;
        }),
    };
  }, [format, readonly]);

  useEffect(() => {
    let entry: MessageEntry;
    let source = activeTranslation?.string || '';
    let sourceView = false;
    if (!source) {
      const orig = parseEntry(format, entity.original);
      entry = orig
        ? getEmptyMessageEntry(orig, locale)
        : createSimpleMessageEntry(entity.key, '');
      if (requiresSourceView(format, entry)) {
        source = serializeEntry(format, entry);
        sourceView = true;
      }
    } else {
      const entry_ = parseEntry(format, source);
      if (entry_) {
        entry = entry_;
        sourceView = requiresSourceView(format, entry);
      } else {
        entry = createSimpleMessageEntry(entity.key, source);
        sourceView = format === 'fluent';
      }
    }

    const fields = sourceView ? editSource(source) : editMessageEntry(entry);

    setState(() => ({
      pk: entity.pk,
      busy: false,
      entry,
      fields,
      focusField: { current: fields[0] },
      initial: entry,
      machinery: null,
      sourceView,
    }));
    setResult(buildResult(fields));
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
    // Dismiss failed checks when the results change.
    // Note that if the editor is updated simultaneously,
    // setting failed checks needs to be delayed past this.
    resetFailedChecks();

    // Changes in `result` need to be reflected in `UnsavedChanges`,
    // but the latter needs to be defined at a higher level to make it
    // available in `EntitiesList`. Therefore, that state is managed here.
    // Let's also avoid the calculation, unless it's actually required.
    setUnsavedChanges(() => {
      const { entry, initial, sourceView } = state;
      const next = sourceView
        ? parseEntryFromFluentSource(entry, result[0].value)
        : buildMessageEntry(entry, result);
      return !pojoEquals(initial, next);
    });
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

export function useEditorMessageEntry() {
  const { entry, sourceView } = useContext(EditorData);
  const message = useContext(EditorResult);
  return sourceView
    ? parseEntryFromFluentSource(entry, message[0].value)
    : buildMessageEntry(entry, message);
}
