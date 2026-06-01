import React, { useContext } from 'react';

import { ThemeContext } from '~/context/Theme';
import { TranslationForm } from '~/modules/translationform';

import './Editor.css';
import { EditorMenu } from './EditorMenu';
import { NewContributorTooltip } from './NewContributorTooltip';
import { MachinerySourceIndicator } from './MachinerySourceIndicator';

export const Editor = () => {
  const { editorTheme } = useContext(ThemeContext);
  const overrideClass =
    editorTheme === 'dark' || editorTheme === 'light'
      ? `${editorTheme}-theme`
      : '';
  return (
    <div className={`editor ${overrideClass}`.trim()}>
      <NewContributorTooltip />
      <TranslationForm />
      <MachinerySourceIndicator />
      <EditorMenu />
    </div>
  );
};
