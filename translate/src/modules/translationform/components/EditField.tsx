import { useLocalization } from '@fluent/react';
import React, { useCallback, useContext } from 'react';
import { EditorActions } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { useHandleShortcuts } from '~/modules/editor';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

export type EditFieldProps = {
  id?: string;
  inputRef: React.MutableRefObject<
    HTMLInputElement | HTMLTextAreaElement | null
  >;
  onFocus?: (ev: {
    currentTarget: HTMLInputElement | HTMLTextAreaElement | null;
  }) => void;
  singleField?: boolean;
  userInput: React.MutableRefObject<boolean>;
  value: string;
};

export function EditField({
  id,
  inputRef,
  onFocus,
  singleField,
  userInput,
  value,
}: EditFieldProps) {
  const { l10n } = useLocalization();
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
  const handleKeyDown = useHandleShortcuts();
  const readOnly = useReadonlyEditor();
  const placeholder =
    singleField && !readOnly
      ? l10n.getString('translationform--single-field-placeholder')
      : undefined;

  return (
    <textarea
      id={id}
      onChange={handleChange}
      onFocus={onFocus}
      onKeyDown={handleKeyDown}
      placeholder={placeholder}
      readOnly={readOnly}
      ref={inputRef as React.MutableRefObject<HTMLTextAreaElement>}
      value={value}
      dir={locale.direction}
      lang={locale.code}
      data-script={locale.script}
    />
  );
}
