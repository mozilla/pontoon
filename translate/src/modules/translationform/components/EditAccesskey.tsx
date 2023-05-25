import React, {
  forwardRef,
  memo,
  useContext,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from 'react';

import { EditFieldHandle, EditorActions, EditorData } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { useHandleShortcuts } from '~/modules/editor';
import { extractAccessKeyCandidates } from '~/utils/message';

import type { EditFieldProps } from './EditField';

export const EditAccesskey = memo(
  forwardRef<EditFieldHandle, EditFieldProps & { name: string }>(
    ({ defaultValue, id, index, name, onFocus }, ref) => {
      const locale = useContext(Locale);
      const { setEditorFromInput } = useContext(EditorActions);
      const { fields } = useContext(EditorData);
      const domRef = useRef<HTMLInputElement>(null);
      const readOnly = useReadonlyEditor();

      const [value, setValue] = useState(defaultValue);
      useEffect(() => setValue(defaultValue), [defaultValue]);

      useImperativeHandle<EditFieldHandle, EditFieldHandle>(
        ref,
        () => ({
          get value() {
            return value;
          },
          set value(next) {
            setValue(next);
          },
          focus() {
            const input = domRef.current;
            if (input) {
              input.focus();
              const end = input.value.length;
              input.setSelectionRange(end, end);
            }
          },
          setSelection(content) {
            if (content.length <= 1) {
              setValue(content);
            }
          },
        }),
        [],
      );

      const handleUpdate = (value: string) => {
        onFocus?.();
        setValue(value);
        setEditorFromInput(index, value);
      };

      const candidates = extractAccessKeyCandidates(fields, name);
      return (
        <>
          <input
            ref={domRef}
            className='accesskey-input'
            dir={locale.direction}
            id={id}
            lang={locale.code}
            maxLength={1}
            onChange={(ev) => handleUpdate(ev.currentTarget.value)}
            onKeyDown={useHandleShortcuts()}
            readOnly={readOnly}
            value={value}
            data-script={locale.script}
          />
          <div className='accesskeys'>
            {candidates.map((key) => (
              <button
                className={`key ${key === value ? 'active' : ''}`}
                disabled={readOnly}
                key={key}
                onClick={(ev) => {
                  const value = ev.currentTarget.textContent ?? '';
                  handleUpdate(value);
                }}
              >
                {key}
              </button>
            ))}
          </div>
        </>
      );
    },
  ),
);
