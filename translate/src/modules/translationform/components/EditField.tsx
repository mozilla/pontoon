import { Localized } from '@fluent/react';
import React, { useCallback, useContext } from 'react';
import { EditorActions } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { useHandleShortcuts } from '~/core/editor';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

export type EditFieldProps = {
  activeField: React.MutableRefObject<HTMLTextAreaElement | null>;
  id?: string;
  singleField?: boolean;
  userInput: React.MutableRefObject<boolean>;
  value: string;
};

export function EditField({
  activeField,
  id,
  singleField,
  userInput,
  value,
}: EditFieldProps) {
  const locale = useContext(Locale);
  const { setEditorFromInput } = useContext(EditorActions);

  const handleChange: React.ChangeEventHandler<HTMLTextAreaElement> =
    useCallback(
      (ev) => {
        userInput.current = true;
        setEditorFromInput(ev.currentTarget.value);
      },
      [userInput, setEditorFromInput],
    );
  const handleFocus: React.FocusEventHandler<HTMLTextAreaElement> = useCallback(
    (ev) => (activeField.current = ev.currentTarget),
    [activeField],
  );
  const handleKeyDown = useHandleShortcuts();

  const props = {
    value,
    dir: locale.direction,
    lang: locale.code,
    'data-script': locale.script,
  };

  if (useReadonlyEditor()) {
    return <textarea readOnly {...props} />;
  }

  if (singleField) {
    return (
      <Localized id='translationform--single-field'>
        <textarea
          id={id}
          onChange={handleChange}
          onFocus={handleFocus}
          onKeyDown={handleKeyDown}
          ref={activeField}
          {...props}
        />
      </Localized>
    );
  }

  return (
    <textarea
      id={id}
      onChange={handleChange}
      onFocus={handleFocus}
      onKeyDown={handleKeyDown}
      {...props}
    />
  );
}
