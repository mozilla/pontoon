import React from 'react';

import { TranslationForm } from '../../../modules/translationform';

import './Editor.css';
import { EditorMenu } from './EditorMenu';
import { NewContributorTooltip } from './NewContributorTooltip';
import { MachinerySourceIndicator } from './MachinerySourceIndicator';

export const Editor = () => (
  <div className='editor'>
    <NewContributorTooltip />
    <TranslationForm />
    <MachinerySourceIndicator />
    <EditorMenu />
  </div>
);
