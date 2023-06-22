import React, { useContext } from 'react';

import { EditorActions, useEditorValue } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { useHandleShortcuts } from '~/modules/editor';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { extractAccessKeyCandidates } from '~/utils/message';

import type { EditFieldProps } from './EditField';

export function EditAccesskey({
  id,
  inputRef,
  name,
  onFocus,
  userInput,
  value,
}: EditFieldProps & { name: string }) {
  const locale = useContext(Locale);
  const { setEditorFromInput } = useContext(EditorActions);
  const message = useEditorValue();

  const handleUpdate = (value: string | null) => {
    if (onFocus && typeof value === 'string') {
      onFocus({ currentTarget: inputRef.current });
      userInput.current = true;
      setEditorFromInput(value);
    }
  };
  const handleKeyDown = useHandleShortcuts();

  const props = {
    className: 'accesskey-input',
    value,
    dir: locale.direction,
    lang: locale.code,
    'data-script': locale.script,
  };

  if (useReadonlyEditor()) {
    return <input readOnly {...props} />;
  }

  const candidates = extractAccessKeyCandidates(message, name);
  return (
    <>
      <input
        id={id}
        ref={inputRef as React.MutableRefObject<HTMLInputElement>}
        maxLength={1}
        onChange={(ev) => handleUpdate(ev.currentTarget.value)}
        onKeyDown={handleKeyDown}
        {...props}
      />
      <div className='accesskeys'>
        {candidates.map((key) => (
          <button
            className={`key ${key === value ? 'active' : ''}`}
            key={key}
            onClick={(ev) => handleUpdate(ev.currentTarget.textContent)}
          >
            {key}
          </button>
        ))}
      </div>
    </>
  );
}
