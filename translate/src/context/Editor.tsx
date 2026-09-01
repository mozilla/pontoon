import type { CatchallKey, Message } from '@mozilla/l10n';
import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
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
  type MessageEntry,
  parseEntry,
  requiresSourceView,
  serializeEntry,
} from '~/utils/message';
import { createMessageEntry } from '~/utils/message/createMessageEntry';
import {
  hasOuterWhitespace,
  htmlElementEscapes,
} from '~/utils/message/entryInformation';
import { messageEntryFromEntityTranslation } from '~/utils/message/fromEntity';
import { getMessageEntryFormat } from '~/utils/message/getMessageEntryFormat';
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

  /**
   * Content filled in automatically rather than by the user.
   */
  autofilled: MessageEntry | null;

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
   */
  setEditorFromHelpers(
    value: string,
    sources: SourceType[],
    manual: boolean,
  ): void;

  /**
   * Rebuild the editor fields from a composed Machinery suggestion, i.e. a full
   * `(value, properties)` data model rather than a single string.
   *
   * @param manual Set `true` when set due to direct user action
   */
  setEditorFromComposed(
    value: Message,
    properties: Record<string, Message> | undefined,
    sources: SourceType[],
    manual: boolean,
  ): void;

  setEditorSelection(content: string): void;

  setResultFromInput(): void;

  toggleSourceView(): void;
};

function parseEntryFromFluentSource(
  sourceEntry: MessageEntry,
  fields: EditorField[],
) {
  const source = fields[0].handle.current.value;
  const entry = parseEntry('fluent', source);
  if (!entry) {
    return null;
  }

  // Terms can have locale-specific attributes
  const isTerm = sourceEntry.id.startsWith('-');

  entry.id = sourceEntry.id;
  if (sourceEntry.value) {
    entry.value ??= [];
  } else if (entry.value) {
    entry.value = null;
  }
  if (sourceEntry.attributes?.size) {
    const sourceKeys = Array.from(sourceEntry.attributes.keys());
    if (!entry.attributes?.size) {
      entry.attributes = new Map(sourceKeys.map((key) => [key, []]));
    } else {
      const attributes = entry.attributes;
      const keys = Array.from(attributes.keys());
      if (
        keys.length !== sourceKeys.length ||
        sourceKeys.some((key, i) => keys[i] !== key)
      ) {
        entry.attributes = new Map(
          sourceKeys.map((key) => {
            const msg = attributes.get(key);
            if (msg) {
              attributes.delete(key);
              return [key, msg];
            }
            return [key, []];
          }),
        );
        if (isTerm) {
          for (const [key, value] of attributes.entries()) {
            entry.attributes.set(key, value);
          }
        }
      }
    }
  } else if (!isTerm) {
    delete entry.attributes;
  }
  return entry;
}

/**
 * Modifies `base` in-place, ensuring that it contains
 * the attributes and declarations present on `sourceEntry`.
 */
function includeSourceAttributesAndDeclarations(
  base: MessageEntry,
  sourceEntry: MessageEntry,
) {
  const apply = (source: Message, target: Message): Message => {
    if (Array.isArray(source)) {
      return target;
    }
    if (Array.isArray(target)) {
      return { decl: structuredClone(source.decl), msg: target };
    }
    for (const [name, expression] of Object.entries(source.decl)) {
      target.decl[name] ??= structuredClone(expression);
    }
    return target;
  };

  if (sourceEntry.value) {
    base.value = apply(sourceEntry.value, base.value ?? []);
  }

  if (sourceEntry.attributes) {
    base.attributes ??= new Map();
    for (const [name, message] of sourceEntry.attributes) {
      const prev = base.attributes.get(name) ?? [];
      base.attributes.set(name, apply(message, prev));
    }
  }
}

const initEditorData: EditorData = {
  pk: 0,
  busy: false,
  base: { format: 'plain', id: '', value: [] },
  focusField: { current: null },
  initial: { format: 'plain', id: '', value: [] },
  autofilled: null,
  machinery: null,
  fields: [],
  sourceView: false,
};

const initEditorActions: EditorActions = {
  clearEditor: () => {},
  setEditorBusy: () => {},
  setEditorFromHelpers: () => {},
  setEditorFromComposed: () => {},
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
  const pendingFieldValues = useRef<Array<[string, string]> | null>(null);
  const [result, setResult] = useState<MessageEntry | null>(null);

  const actions = useMemo<EditorActions>(() => {
    if (readonly) {
      return initEditorActions;
    }
    const buildOpts = {
      escapeHTML: htmlElementEscapes(sourceEntry),
      trim: !hasOuterWhitespace(sourceEntry),
    };

    const resetFields = (next: EditorData): EditorData => {
      pendingFieldValues.current = next.fields.map(({ id, handle }) => [
        id,
        handle.current.value,
      ]);
      next.focusField.current = next.fields[0];
      setResult(buildMessageEntry(next.base, next.fields, buildOpts));
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
          next.autofilled = manual
            ? null
            : buildMessageEntry(next.base, next.fields, buildOpts);
          if (manual) {
            field.handle.current.focus();
          }
          return next;
        }),

      setEditorFromComposed: (value, properties, sources, manual) =>
        setState((prev) => {
          const entry = createMessageEntry(
            getMessageEntryFormat(format),
            prev.base.id,
            value,
            properties,
          );
          const next = { ...prev, base: entry };
          if (requiresSourceView(entry)) {
            next.fields = editSource(entry);
            next.sourceView = true;
          } else {
            next.fields = prev.sourceView
              ? editSource(entry)
              : editMessageEntry(sourceEntry, entry);
          }
          const state = resetFields(next);
          return {
            ...state,
            autofilled: manual
              ? null
              : buildMessageEntry(state.base, state.fields, buildOpts),
            machinery: {
              manual,
              translation: getPlainMessage(entry),
              sources,
            },
          };
        }),

      setEditorFromHistory: (str) =>
        setState((prev) => {
          const next = { ...prev, autofilled: null };
          if (specialFormats.has(format)) {
            const entry = parseEntry(format, str);
            if (entry) {
              includeSourceAttributesAndDeclarations(entry, sourceEntry);
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
          return resetFields(next);
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
            ? parseEntryFromFluentSource(sourceEntry, fields)
            : buildMessageEntry(base, fields, buildOpts);
          setResult(result);
          return state;
        }),

      toggleSourceView: () =>
        setState((state) => {
          const { base, fields, sourceView } = state;
          if (sourceView) {
            const entry = parseEntryFromFluentSource(sourceEntry, fields);
            if (entry && !requiresSourceView(entry)) {
              includeSourceAttributesAndDeclarations(entry, sourceEntry);
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
    includeSourceAttributesAndDeclarations(base, sourceEntry);
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
      autofilled: null,
      machinery: null,
      sourceView,
    }));
    setResult(base);
  }, [locale, entity, activeTranslation]);

  // Write the values recorded by `resetFields` into the fields that are now
  // on screen. After the commit, so that the editor changes this dispatches
  // don't land in React's render phase.
  useEffect(() => {
    const pending = pendingFieldValues.current;
    if (pending) {
      pendingFieldValues.current = null;
      for (const [id, value] of pending) {
        const field = state.fields.find((f) => f.id === id);
        field?.handle.current.setValue(value);
      }
    }
  }, [state.fields]);

  // For missing entries, fill editor initially with a perfect match from
  // translation memory, if available.
  const status = useTranslationStatus(entity);
  useEffect(() => {
    if (
      status !== 'missing' ||
      state.machinery !== null ||
      state.sourceView ||
      state.fields.some((field) => field.handle.current.value !== '')
    ) {
      return;
    }
    if (state.fields.length === 1) {
      const perfect = machinery.translations.find((tx) => tx.quality === 100);
      if (perfect) {
        actions.setEditorFromHelpers(
          perfect.translation,
          perfect.sources,
          false,
        );
      }
    } else if (state.fields.length > 1) {
      const perfect = machinery.composed.find((tx) => tx.quality === 100);
      if (perfect) {
        actions.setEditorFromComposed(
          perfect.value,
          perfect.properties,
          perfect.sources,
          false,
        );
      }
    }
  }, [state, actions, status, machinery.translations, machinery.composed]);

  useEffect(() => {
    // Changes in `result` need to be reflected in `UnsavedChanges`,
    // but the latter needs to be defined at a higher level to make it
    // available in `EntitiesList`. Therefore, that state is managed here.
    // Let's also avoid the calculation, unless it's actually required.
    // Content set by autofill (100% TM match) should not trigger a warning,
    // as it would be autofilled again on the next visit.
    const { autofilled, initial } = state;
    const hasChanges = !pojoEquals(initial, result);
    if (hasChanges) {
      resetFailedChecks();
    }
    const isAutofilled = !!autofilled && pojoEquals(autofilled, result);
    setUnsavedChanges(() => hasChanges && !isAutofilled);
  }, [result, state.autofilled]);

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
