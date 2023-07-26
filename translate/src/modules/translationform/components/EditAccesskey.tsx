import React, {
  forwardRef,
  memo,
  useCallback,
  useContext,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from 'react';

import { EditFieldHandle, EditorActions, EditorData } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { useCopyOriginalIntoEditor } from '~/modules/editor';
import { extractAccessKeyCandidates } from '~/utils/message';

import { useHandleEnter, useHandleEscape } from '../utils/editFieldShortcuts';
import type { EditFieldProps } from './EditField';

function useHandleShortcuts(): (event: React.KeyboardEvent) => void {
  const copyOriginalIntoEditor = useCopyOriginalIntoEditor();
  const { clearEditor } = useContext(EditorActions);

  const onEnter = useHandleEnter();
  const onEscape = useHandleEscape();

  return (ev: React.KeyboardEvent) => {
    switch (ev.key) {
      case 'Enter':
        if (!ev.ctrlKey && !ev.shiftKey && !ev.altKey) {
          ev.preventDefault();
          onEnter();
        }
        break;

      case 'Escape':
        ev.preventDefault();
        onEscape();
        break;

      // On Ctrl + Shift + C, copy the original translation.
      case 'C':
        if (ev.ctrlKey && ev.shiftKey && !ev.altKey) {
          ev.preventDefault();
          copyOriginalIntoEditor();
        }
        break;

      // On Ctrl + Shift + Backspace, clear the content.
      case 'Backspace':
        if (ev.ctrlKey && ev.shiftKey && !ev.altKey) {
          ev.preventDefault();
          clearEditor();
        }
        break;
    }
  };
}

export const EditAccesskey = memo(
  forwardRef<EditFieldHandle, EditFieldProps & { name: string }>(
    ({ defaultValue, index, name, onFocus }, ref) => {
      const locale = useContext(Locale);
      const { setResultFromInput } = useContext(EditorActions);
      const { fields } = useContext(EditorData);
      const domRef = useRef<HTMLInputElement>(null);
      const readOnly = useReadonlyEditor();

      const [value, setValue_] = useState(defaultValue);
      const setValue = useCallback(
        (value: string) => {
          setValue_(value);
          setResultFromInput(index, value);
        },
        [index],
      );

      useEffect(() => setValue(defaultValue), [defaultValue]);

      useImperativeHandle<EditFieldHandle, EditFieldHandle>(
        ref,
        () => ({
          get value() {
            return value;
          },
          focus() {
            const input = domRef.current;
            if (input) {
              input.focus();
              const end = input.value.length;
              input.setSelectionRange(end, end);
            }
          },
          setSelection(text) {
            if (text.length <= 1) {
              setValue(text);
            }
          },
          setValue,
        }),
        [setValue],
      );

      const handleUpdate = (value: string) => {
        onFocus?.();
        setValue(value);
      };
      const handleKeyDown = useHandleShortcuts();

      const candidates = extractAccessKeyCandidates(fields, name);
      return (
        <>
          <input
            ref={domRef}
            className='accesskey-input'
            dir={locale.direction}
            lang={locale.code}
            maxLength={1}
            onChange={(ev) => handleUpdate(ev.currentTarget.value)}
            onKeyDown={readOnly ? undefined : handleKeyDown}
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
