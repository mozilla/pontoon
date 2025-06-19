import React from 'react';

import { PluralSelector, TranslationForm } from '~/modules/translationform';

import './Editor.css';
import { EditorMenu } from './EditorMenu';
import { NewContributorTooltip } from './NewContributorTooltip';
import { MachinerySourceIndicator } from './MachinerySourceIndicator';
import { TranslationWarningsErrors } from './TranslationWarningsErrors';
import { FailedChecksProvider } from '~/context/FailedChecksData';

export const Editor = () => (
  <div className='editor'>
    <PluralSelector />
    <NewContributorTooltip />
    <TranslationForm />
    <MachinerySourceIndicator />
    <EditorMenu />
    <FailedChecksProvider>
      <TranslationWarningsErrors />
    </FailedChecksProvider>
  </div>
);
