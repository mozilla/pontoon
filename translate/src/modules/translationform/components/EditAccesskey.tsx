import React, { useContext, useRef } from 'react';

import { EditorActions, useEditorValue } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { useHandleShortcuts } from '~/core/editor';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { extractAccessKeyCandidates } from '~/utils/message';

import type { EditFieldProps } from './EditField';

export function EditAccesskey({
  id,
  name,
  userInput,
  value,
}: EditFieldProps & { name: string }) {
  const locale = useContext(Locale);
  const { setEditorFromInput } = useContext(EditorActions);
  const message = useEditorValue();
  const accessKeyElement = useRef<HTMLInputElement>(null);

  const handleUpdate = (value: string | null) => {
    if (typeof value === 'string') {
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
        ref={accessKeyElement}
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
