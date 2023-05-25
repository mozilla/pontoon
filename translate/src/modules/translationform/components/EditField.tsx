import { useLocalization } from '@fluent/react';
import React, {
  forwardRef,
  memo,
  useContext,
  useEffect,
  useImperativeHandle,
  useRef,
} from 'react';
import { EditFieldHandle, EditorActions } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { useHandleShortcuts } from '~/modules/editor';

export type EditFieldProps = {
  /** Used by `<label htmlFor>` */
  id?: string;
  index: number;
  onFocus?: () => void;
  singleField?: boolean;
  defaultValue: string;
};

export const EditField = memo(
  forwardRef<EditFieldHandle, EditFieldProps>(
    ({ defaultValue, id, index, onFocus, singleField }, ref) => {
      const { l10n } = useLocalization();
      const locale = useContext(Locale);
      const { setEditorFromInput } = useContext(EditorActions);
      const domRef = useRef<HTMLTextAreaElement>(null);

      useEffect(() => {
        const textarea = domRef.current;
        if (textarea) {
          textarea.value = defaultValue;
        }
      }, [defaultValue]);

      useImperativeHandle<EditFieldHandle, EditFieldHandle>(
        ref,
        () => ({
          get value() {
            return domRef.current?.value ?? '';
          },
          set value(next) {
            const textarea = domRef.current;
            if (textarea) {
              textarea.value = next;
            }
          },
          focus() {
            const textarea = domRef.current;
            if (textarea) {
              textarea.focus();
              const end = textarea.value.length;
              textarea.setSelectionRange(end, end);
            }
          },
          setSelection(content) {
            const textarea = domRef.current;
            textarea?.setRangeText(
              content,
              textarea.selectionStart,
              textarea.selectionEnd,
              'end',
            );
          },
        }),
        [],
      );

      const readOnly = useReadonlyEditor();
      const placeholder =
        singleField && !readOnly
          ? l10n.getString('translationform--single-field-placeholder')
          : undefined;

      return (
        <textarea
          ref={domRef}
          defaultValue={defaultValue}
          id={id}
          onChange={(ev) => {
            setEditorFromInput(index, ev.currentTarget.value);
          }}
          onFocus={onFocus}
          onKeyDown={useHandleShortcuts()}
          placeholder={placeholder}
          readOnly={readOnly}
          dir={locale.direction}
          lang={locale.code}
          data-script={locale.script}
        />
      );
    },
  ),
);
