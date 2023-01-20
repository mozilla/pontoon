import React, { useContext } from 'react';

import { EditorData } from '~/context/Editor';
import { RichTranslationForm } from '~/modules/fluenteditor/components/RichTranslationForm';
import { GenericTranslationForm } from '~/modules/genericeditor';
import { PluralSelector } from '~/modules/genericeditor/components/PluralSelector';

import './Editor.css';
import { EditorMenu } from './EditorMenu';
import { NewContributorTooltip } from './NewContributorTooltip';
import { MachinerySourceIndicator } from './MachinerySourceIndicator';

export function Editor(): React.ReactElement<'div'> {
  const { value } = useContext(EditorData);

  return (
    <div className='editor'>
      <PluralSelector />
      <NewContributorTooltip />
      {value.length === 1 ? (
        <GenericTranslationForm />
      ) : (
        <RichTranslationForm />
      )}
      <MachinerySourceIndicator />
      <EditorMenu />
    </div>
  );
}
