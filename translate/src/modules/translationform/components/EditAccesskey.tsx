import React, { useContext, useRef } from 'react';

import { EditorActions, EditorData } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { useHandleShortcuts } from '~/core/editor';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { extractAccessKeyCandidates } from '~/utils/message';

import type { EditFieldProps } from './EditField';

export function EditAccesskey({
  activeInput,
  id,
  name,
  userInput,
  value,
}: EditFieldProps & { name: string }) {
  const locale = useContext(Locale);
  const { setEditorFromInput } = useContext(EditorActions);
  const { value: message } = useContext(EditorData);
  const accessKeyElement = useRef<HTMLInputElement>(null);

  const handleUpdate = (value: string | null) => {
    if (typeof value === 'string') {
      userInput.current = true;
      setEditorFromInput(value);
    }
  };
  const handleKeyDown = useHandleShortcuts();
  const handleClick = (ev: React.MouseEvent) => {
    activeInput.current = accessKeyElement.current;
    handleUpdate(ev.currentTarget.textContent);
  };

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
        ref={accessKeyElement}
        maxLength={1}
        onChange={(ev) => handleUpdate(ev.currentTarget.value)}
        onFocus={(ev) => (activeInput.current = ev.currentTarget)}
        onKeyDown={handleKeyDown}
        {...props}
      />
      <div className='accesskeys'>
        {candidates.map((key) => (
          <button
            className={`key ${key === value ? 'active' : ''}`}
            key={key}
            onClick={handleClick}
          >
            {key}
          </button>
        ))}
      </div>
    </>
  );
}
