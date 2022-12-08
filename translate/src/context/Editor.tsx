import type { Entry } from '@fluent/syntax';
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import type { SourceType } from '~/api/machinery';
import { useTranslationStatus } from '~/core/entities/useTranslationStatus';
import {
  getEmptyMessage,
  getReconstructedMessage,
  getSimplePreview,
  getSyntaxType,
  parseEntry,
  serializeEntry,
} from '~/core/utils/fluent';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import { EntityView, useActiveTranslation } from './EntityView';
import { FailedChecksData } from './FailedChecksData';
import { Locale } from './Locale';
import { MachineryTranslations } from './MachineryTranslations';
import { UnsavedActions, UnsavedChanges } from './UnsavedChanges';

export type EditorData = Readonly<{
  activeInput: React.MutableRefObject<HTMLTextAreaElement | null>;

  /** Is a request to send a new translation running? */
  busy: boolean;

  format: 'simple' | 'ftl';

  /** Used for detecting unsaved changes and reconstructing FTL messages */
  initial: string;

  machinery: {
    manual: boolean;
    sources: SourceType[];
    translation: string;
  } | null;

  /**
   * The current value being edited. For `view: 'simple'` and `view: 'source'`,
   * the `string` currently displayed in the editor. For `view: 'rich'`,
   * the Fluent `Entry` value that is displayed in multiple text inputs.
   */
  value: string | Entry;

  view: 'simple' | 'rich' | 'source';
}>;

export type EditorActions = {
  setEditorBusy(busy: boolean): void;

  /** If `format: 'ftl'`, must be called with the source of a full entry */
  setEditorFromHistory(value: string): void;

  /** For `view: 'rich'`, if `value` is a string, sets the value of the active input */
  setEditorFromInput(value: string | Entry): void;

  /** @param manual Set `true` when value set due to direct user action */
  setEditorFromHelpers(
    value: string,
    sources: SourceType[],
    manual: boolean,
  ): void;

  setEditorSelection(content: string): void;

  toggleFtlView(): void;
};

const initEditorData: EditorData = {
  activeInput: { current: null },
  busy: false,
  format: 'simple',
  initial: '',
  machinery: null,
  value: '',
  view: 'simple',
};

const initEditorActions: EditorActions = {
  setEditorBusy: () => {},
  setEditorFromHelpers: () => {},
  setEditorFromHistory: () => {},
  setEditorFromInput: () => {},
  setEditorSelection: () => {},
  toggleFtlView: () => {},
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
      setEditorBusy: (busy) =>
        setState((prev) => (busy === prev.busy ? prev : { ...prev, busy })),

      setEditorFromHelpers: (translation, sources, manual) =>
        setState((prev) => {
          let value: string | Entry;
          switch (prev.view) {
            case 'simple':
              value = translation;
              break;
            case 'rich': {
              value =
                updateRichValue(prev, translation, false, true) ?? translation;
              break;
            }
            case 'source': {
              const entry = getReconstructedMessage(prev.initial, translation);
              value = serializeEntry(entry);
              break;
            }
          }
          const machinery = { manual, translation, sources };
          return { ...prev, machinery, value };
        }),

      setEditorFromHistory: (value) =>
        setState((prev) => {
          if (prev.format === 'ftl' && prev.view !== 'source') {
            const next = getFtlViewAndValue(value);
            return { ...prev, value: next.value, view: next.view };
          } else {
            return { ...prev, value };
          }
        }),

      setEditorFromInput: (value) =>
        setState((prev) => {
          if (prev.view === 'rich' && typeof value === 'string') {
            const next = updateRichValue(prev, value, false, false);
            if (next) {
              return { ...prev, value: next };
            }
          }
          return { ...prev, value };
        }),

      setEditorSelection: (content) =>
        setState((prev) => {
          if (typeof prev.value === 'string') {
            const input = prev.activeInput.current;
            if (input) {
              input.setRangeText(
                content,
                input.selectionStart,
                input.selectionEnd,
                'end',
              );
              return { ...prev, value: input.value };
            }
          } else {
            const next = updateRichValue(prev, content, true, true);
            if (next) {
              return { ...prev, value: next };
            }
          }
          return { ...prev, value: content };
        }),

      toggleFtlView: () =>
        setState((prev) => {
          switch (prev.view) {
            case 'simple': {
              if (prev.format !== 'ftl' || typeof prev.value !== 'string') {
                return prev;
              }
              const entry = getReconstructedMessage(prev.initial, prev.value);
              const value = serializeEntry(entry);
              return { ...prev, value, view: 'source' };
            }

            case 'rich': {
              if (typeof prev.value === 'string') {
                return prev;
              }
              const value = serializeEntry(prev.value);
              return { ...prev, value, view: 'source' };
            }

            case 'source': {
              const { value, view } = getFtlViewAndValue(prev.value as string);
              return view === 'source' ? prev : { ...prev, value, view };
            }
          }
        }),
    };
  }, [readonly]);

  useEffect(() => {
    let initial = activeTranslation?.string || '';

    let format: 'ftl' | 'simple';
    let value: string | Entry;
    let view: 'simple' | 'rich' | 'source';
    if (entity.format === 'ftl') {
      format = 'ftl';
      if (!initial) {
        const entry = parseEntry(entity.original);
        initial = serializeEntry(getEmptyMessage(entry, locale));
      } else if (!initial.endsWith('\n')) {
        // Some Fluent translations may be stored without a terminal newline.
        // If the data is cleaned up, this conditional may be removed.
        // https://github.com/mozilla/pontoon/issues/2216
        initial += '\n';
      }
      const next = getFtlViewAndValue(initial);
      value = next.value;
      view = next.view;
    } else {
      format = 'simple';
      value = initial;
      view = 'simple';
    }

    setState((prev) => ({
      activeInput: prev.activeInput,
      busy: false,
      format,
      initial,
      machinery: null,
      value,
      view,
    }));
  }, [locale, entity, activeTranslation]);

  // For missing entries, fill editor initially with a perfect match from
  // translation memory, if available.
  const status = useTranslationStatus(entity);
  useEffect(() => {
    if (
      status === 'missing' &&
      state.view === 'simple' &&
      state.value === '' &&
      state.machinery === null
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
    // Error recovery, if `view` and `value` type do not match
    if (state.view === 'rich') {
      if (typeof state.value === 'string') {
        if (process.env.NODE_ENV === 'development') {
          console.warn('Editor state mismatch!', state);
        }
        actions.toggleFtlView();
      }
    } else if (typeof state.value !== 'string') {
      if (process.env.NODE_ENV === 'development') {
        console.warn('Editor state mismatch!', state);
      }
      actions.setEditorFromHistory(serializeEntry(state.value));
    }

    // Changes in `value` need to be reflected in `UnsavedChanges`,
    // but the latter needs to be defined at a higher level to make it
    // available in `EntitiesList`. Therefore, that state is managed here.
    setUnsavedChanges(getEditedTranslation(state) !== state.initial);

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

export function useClearEditor() {
  const locale = useContext(Locale);
  const { setEditorFromInput } = useContext(EditorActions);
  const { initial, value, view } = useContext(EditorData);

  return useCallback(() => {
    if (view === 'simple') {
      setEditorFromInput('');
    } else {
      const empty = getEmptyMessage(parseEntry(initial), locale);
      if (typeof value === 'string') {
        const str = serializeEntry(empty);
        setEditorFromInput(str);
      } else {
        setEditorFromInput(empty);
      }
    }
  }, [locale, initial, typeof value, view]);
}

export function getEditedTranslation(data: EditorData): string {
  const { format, value } = data;
  if (format === 'ftl' || typeof value !== 'string') {
    return serializeEntry(getFluentEntry(data));
  } else {
    return value;
  }
}

/** Will return a `Junk` entry for non-Fluent message data */
export function getFluentEntry({ initial, value, view }: EditorData): Entry {
  if (typeof value !== 'string') {
    return value.clone();
  } else if (view === 'simple') {
    return getReconstructedMessage(initial, value);
  } else {
    return parseEntry(value);
  }
}

function getFtlViewAndValue(
  source: string,
): Pick<EditorData, 'value' | 'view'> {
  const entry = parseEntry(source);
  switch (getSyntaxType(entry)) {
    case 'simple':
      return { value: getSimplePreview(entry), view: 'simple' };
    case 'rich':
      return { value: entry, view: 'rich' };
    default:
      return { value: source, view: 'source' };
  }
}

function updateRichValue(
  { activeInput, value }: EditorData,
  content: string,
  selectionOnly: boolean,
  fixFocus: boolean,
): Entry | null {
  if (
    typeof value !== 'string' &&
    (value.type === 'Message' || value.type === 'Term') &&
    activeInput.current?.id
  ) {
    const input = activeInput.current;
    const next = value.clone();

    const path = input.id.split('-');
    const last = path.pop();
    let node: any = next;
    for (const part of path) {
      if (node) {
        node = node[part];
      }
    }
    if (!last || !node || typeof node[last] !== 'string') {
      throw new Error(`Invalid rich editor path: ${path}`);
    }

    let start: number;
    if (selectionOnly) {
      start = input.selectionStart;
      input.setRangeText(content);
      node[last] = input.value;
    } else {
      start = 0;
      node[last] = content;
    }

    // Need to let react-dom "fix" the select position before setting it right
    if (fixFocus) {
      setTimeout(() => {
        const end = start + content.length;
        input.setSelectionRange(end, end);
      });
    }

    return next;
  } else {
    return null;
  }
}
