import { EditorState } from '@codemirror/state';
import { EditorView, placeholder } from '@codemirror/view';

import { useLocalization } from '@fluent/react';
import React, {
  forwardRef,
  memo,
  useCallback,
  useContext,
  useEffect,
  useImperativeHandle,
  useState,
} from 'react';

import { EditFieldHandle, EditorActions } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import { getExtensions, useKeyHandlers } from '../utils/editFieldExtensions';
import { EntityView } from '~/context/EntityView';

export type EditFieldProps = {
  index: number;
  onFocus?: () => void;
  singleField?: boolean;
  defaultValue: string;
};

/**
 * The CodeMirror initialization is only run once,
 * so changes in props or context are not reflected in the editor unless handled separately,
 * as is done e.g. for `defaultValue`.
 *
 * Make sure apply an appropriate `key` prop to keep old instances from being reused.
 */
export const EditField = memo(
  forwardRef<EditFieldHandle, EditFieldProps>(
    ({ defaultValue, index, onFocus, singleField }, ref) => {
      const { l10n } = useLocalization();
      const locale = useContext(Locale);
      const readOnly = useReadonlyEditor();
      const { entity } = useContext(EntityView);
      const { setResultFromInput } = useContext(EditorActions);
      const keyHandlers = useKeyHandlers();
      const [view, setView] = useState<EditorView | null>(null);

      const initView = useCallback(
        (parent: HTMLDivElement | null) => {
          if (parent) {
            const extensions = getExtensions(entity.format, keyHandlers);
            if (readOnly) {
              extensions.push(
                EditorState.readOnly.of(true),
                EditorView.editable.of(false),
              );
            } else {
              if (singleField) {
                const l10nId = 'translationform--single-field-placeholder';
                extensions.push(placeholder(l10n.getString(l10nId)));
              }
              extensions.push(
                EditorView.updateListener.of((update) => {
                  if (onFocus && update.focusChanged && update.view.hasFocus) {
                    onFocus();
                  }
                  if (update.docChanged) {
                    setResultFromInput(index, update.state.doc.toString());
                  }
                }),
              );
            }

            const state = EditorState.create({ doc: defaultValue, extensions });
            view?.destroy();
            setView(new EditorView({ state, parent }));
          } else if (view) {
            view.destroy();
            setView(null);
          }
        },
        [readOnly],
      );

      const setValue = useCallback(
        (text: string) => {
          const prev = view?.state.doc.toString();
          if (text !== prev) {
            view?.dispatch({
              changes: { from: 0, to: view.state.doc.length, insert: text },
              selection: { anchor: text.length },
            });
          }
        },
        [view],
      );
      useEffect(() => setValue(defaultValue), [defaultValue]);

      useImperativeHandle<EditFieldHandle, EditFieldHandle>(
        ref,
        () => ({
          get value() {
            return view ? view.state.doc.toString() : defaultValue;
          },
          focus() {
            if (view) {
              const range = view.state.selection.main;
              const end = view.state.doc.length;
              if (range.anchor === 0 && range.empty && end) {
                view.dispatch({ selection: { anchor: end } });
              }
              view.focus();
            }
          },
          setSelection(text) {
            if (view) {
              view.dispatch(view.state.replaceSelection(text));
              view.focus();
            }
          },
          setValue,
        }),
        [view],
      );

      return (
        <div
          className={readOnly ? 'readonly' : undefined}
          ref={initView}
          data-script={locale.script}
          dir={locale.direction}
          lang={locale.code}
        />
      );
    },
  ),
);
