import type { Variant } from 'messageformat';
import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import type { SourceType } from '~/api/machinery';
import { useTranslationStatus } from '~/modules/entities/useTranslationStatus';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import {
  buildMessageEntry,
  editMessageEntry,
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
import { UnsavedActions, UnsavedChanges } from './UnsavedChanges';

export type EditorMessage = Array<{
  /** An identifier for this field */
  id: string;

  /** Attribute name, or empty for the value */
  name: string;

  /** Selector keys, or empty array for single-pattern messages */
  keys: Variant['keys'];

  labels: Array<{ label: string; plural: boolean }>;

  /**
   * A flattened representation of a single message pattern,
   * which may contain syntactic representations of placeholders.
   */
  value: string;
}>;

function editSource(source: string | MessageEntry) {
  const value =
    typeof source === 'string' ? source : serializeEntry('ftl', source);
  return [{ id: '', name: '', keys: [], labels: [], value: value.trim() }];
}

/**
 * Creates a copy of `base` with an entry matching `id` updated to `value`.
 *
 * @param id If empty, matches first entry of `base`.
 *           If set, a path split by `|` characters.
 */
function setEditorMessage(
  base: EditorMessage,
  id: string | null | undefined,
  value: string,
): EditorMessage {
  let set = false;
  return base.map((field) => {
    if (!set && (!id || field.id === id)) {
      set = true;
      return { ...field, value };
    } else {
      return field;
    }
  });
}

function parseEntryFromFluentSource(base: MessageEntry, source: string) {
  const entry = parseEntry(source);
  if (entry) {
    entry.id = base.id;
  }
  return entry;
}

/**
 * Create a new MessageEntry with a simple string pattern `value`,
 * using `id` as its identifier.
 */
const createSimpleMessageEntry = (id: string, value: string): MessageEntry => ({
  id,
  value: {
    type: 'message',
    declarations: [],
    pattern: { body: [{ type: 'text', value }] },
  },
});

export type EditorData = Readonly<{
  /** Is a request to send a new translation running? */
  busy: boolean;

  /** Used to reconstruct edited messages */
  entry: MessageEntry;

  /** Editor input components */
  fields: Array<
    React.MutableRefObject<HTMLInputElement | HTMLTextAreaElement | null>
  >;

  /**
   * Index in `fields` of the current or most recent field with focus;
   * used as the target of machinery replacements.
   */
  focusField: React.MutableRefObject<number>;

  /** Used for detecting unsaved changes */
  initial: EditorMessage;

  machinery: {
    manual: boolean;
    sources: SourceType[];
    translation: string;
  } | null;

  sourceView: boolean;

  /** The current value being edited */
  value: EditorMessage;
}>;

export type EditorActions = {
  clearEditor(): void;

  setEditorBusy(busy: boolean): void;

  /** If `format: 'ftl'`, must be called with the source of a full entry */
  setEditorFromHistory(value: string): void;

  /** For `view: 'rich'`, if `value` is a string, sets the value of the active input */
  setEditorFromInput(value: string | EditorMessage): void;

  /** @param manual Set `true` when value set due to direct user action */
  setEditorFromHelpers(
    value: string,
    sources: SourceType[],
    manual: boolean,
  ): void;

  setEditorSelection(content: string): void;

  toggleSourceView(): void;
};

const initEditorData: EditorData = {
  busy: false,
  entry: { id: '', value: null, attributes: new Map() },
  fields: [],
  focusField: { current: 0 },
  initial: [],
  machinery: null,
  sourceView: false,
  value: [],
};

const initEditorActions: EditorActions = {
  clearEditor: () => {},
  setEditorBusy: () => {},
  setEditorFromHelpers: () => {},
  setEditorFromHistory: () => {},
  setEditorFromInput: () => {},
  setEditorSelection: () => {},
  toggleSourceView: () => {},
};

export const EditorData = createContext(initEditorData);
export const EditorActions = createContext(initEditorActions);

export function EditorProvider({ children }: { children: React.ReactElement }) {
  const locale = useContext(Locale);
  const { entity } = useContext(EntityView);
  const activeTranslation = useActiveTranslation();
  const readonly = useReadonlyEditor();
  const machinery = useContext(MachineryTranslations);
  const { setUnsavedChanges } = useContext(UnsavedActions);
  const { exist } = useContext(UnsavedChanges);
  const { resetFailedChecks } = useContext(FailedChecksData);

  const [state, setState] = useState<EditorData>(initEditorData);

  const actions = useMemo<EditorActions>(() => {
    if (readonly) {
      return initEditorActions;
    }
    return {
      clearEditor: () =>
        setState((prev) => {
          const empty = prev.value.map((field) => ({ ...field, value: '' }));
          return { ...prev, value: empty };
        }),

      setEditorBusy: (busy) =>
        setState((prev) => (busy === prev.busy ? prev : { ...prev, busy })),

      setEditorFromHelpers: (str, sources, manual) =>
        setState((prev) => {
          const { fields, focusField, sourceView, value } = prev;
          const input = fields[focusField.current]?.current;
          let next = setEditorMessage(value, input?.id, str);
          if (sourceView) {
            next = editSource(buildMessageEntry(prev.entry, next));
          }
          return {
            ...prev,
            machinery: { manual, translation: str, sources },
            value: next,
          };
        }),

      setEditorFromHistory: (str) =>
        setState((prev) => {
          const next = { ...prev };
          if (entity.format === 'ftl') {
            const entry = parseEntry(str);
            if (entry) {
              next.entry = entry;
            }
            if (entry && !requiresSourceView(entry)) {
              next.value = prev.sourceView
                ? editSource(entry)
                : editMessageEntry(entry);
            } else {
              next.value = editSource(str);
              next.sourceView = true;
            }
            next.fields = next.value.map(() => ({ current: null }));
          } else {
            next.value = setEditorMessage(prev.initial, null, str);
          }
          return next;
        }),

      setEditorFromInput: (input) =>
        setState((prev) => {
          if (typeof input === 'string') {
            const { fields, focusField, value } = prev;
            const field = fields[focusField.current]?.current;
            const next = setEditorMessage(value, field?.id, input);
            return { ...prev, value: next };
          } else {
            return { ...prev, value: input };
          }
        }),

      setEditorSelection: (content) =>
        setState((prev) => {
          const { fields, focusField, sourceView, value } = prev;
          let next: EditorMessage;
          const input = fields[focusField.current]?.current;
          if (input) {
            input.setRangeText(
              content,
              input.selectionStart ?? 0, // never actually null for <input type="text"> or <textarea>
              input.selectionEnd ?? 0,
              'end',
            );
            next = setEditorMessage(value, input.id, input.value);
          } else if (value.length === 1) {
            next = setEditorMessage(value, null, value[0].value + content);
            if (sourceView) {
              next = editSource(buildMessageEntry(prev.entry, next));
            }
          } else {
            next = setEditorMessage(value, null, content);
          }
          return { ...prev, value: next };
        }),

      toggleSourceView: () =>
        setState((prev) => {
          if (prev.sourceView) {
            const source = prev.value[0].value;
            const entry = parseEntryFromFluentSource(prev.entry, source);
            if (entry && !requiresSourceView(entry)) {
              const value = editMessageEntry(entry);
              return {
                ...prev,
                entry,
                fields: value.map(() => ({ current: null })),
                sourceView: false,
                value,
              };
            }
          } else if (entity.format === 'ftl') {
            const entry = buildMessageEntry(prev.entry, prev.value);
            const source = serializeEntry('ftl', entry);
            return {
              ...prev,
              fields: [{ current: null }],
              sourceView: true,
              value: editSource(source),
            };
          }
          return prev;
        }),
    };
  }, [entity.format, readonly]);

  useEffect(() => {
    let entry: MessageEntry;
    let source = activeTranslation?.string || '';
    let sourceView = false;
    if (entity.format === 'ftl') {
      if (!source) {
        const orig = parseEntry(entity.original);
        entry = orig
          ? getEmptyMessageEntry(orig, locale)
          : createSimpleMessageEntry(entity.key, '');
        if (requiresSourceView(entry)) {
          source = serializeEntry('ftl', entry);
          sourceView = true;
        }
      } else {
        if (!source.endsWith('\n')) {
          // Some Fluent translations may be stored without a terminal newline.
          // If the data is cleaned up, this conditional may be removed.
          // https://github.com/mozilla/pontoon/issues/2216
          source += '\n';
        }
        const entry_ = parseEntry(source);
        if (entry_) {
          entry = entry_;
          sourceView = requiresSourceView(entry);
        } else {
          entry = createSimpleMessageEntry(entity.key, source);
          sourceView = true;
        }
      }
    } else {
      entry = createSimpleMessageEntry(entity.key, source);
    }

    const value: EditorMessage = sourceView
      ? editSource(source)
      : editMessageEntry(entry);

    setState(() => ({
      busy: false,
      entry,
      fields: value.map(() => ({ current: null })),
      focusField: { current: 0 },
      initial: value,
      machinery: null,
      sourceView,
      value,
    }));
  }, [locale, entity, activeTranslation]);

  // For missing entries, fill editor initially with a perfect match from
  // translation memory, if available.
  const status = useTranslationStatus(entity);
  useEffect(() => {
    if (
      status === 'missing' &&
      state.machinery === null &&
      !state.sourceView &&
      state.value.length === 1 &&
      state.value[0].value === ''
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
    // Changes in `value` need to be reflected in `UnsavedChanges`,
    // but the latter needs to be defined at a higher level to make it
    // available in `EntitiesList`. Therefore, that state is managed here.
    setUnsavedChanges(!pojoEquals(state.initial, state.value));

    if (exist) {
      resetFailedChecks();
    }
  }, [state.value, state.initial]);

  return (
    <EditorData.Provider value={state}>
      <EditorActions.Provider value={actions}>
        {children}
      </EditorActions.Provider>
    </EditorData.Provider>
  );
}

export function useEditorValue(): EditorMessage {
  const { value } = useContext(EditorData);
  return value;
}

export function useEditorMessageEntry() {
  const { entry, sourceView } = useContext(EditorData);
  const value = useEditorValue();
  return sourceView
    ? parseEntryFromFluentSource(entry, value[0].value)
    : buildMessageEntry(entry, value);
}
