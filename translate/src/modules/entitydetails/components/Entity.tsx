import React from 'react';

import { EditorProvider } from '~/context/Editor';
import { FailedChecksProvider } from '~/context/FailedChecksData';
import { HelperSelectionProvider } from '~/context/HelperSelection';
import { HistoryProvider } from '~/context/HistoryData';
import { MachineryProvider } from '~/context/MachineryTranslations';
import { SearchProvider } from '~/context/SearchData';
import { EntityDetails } from './EntityDetails';

export const Entity = () => (
  <SearchProvider>
    <MachineryProvider>
      <HistoryProvider>
        <FailedChecksProvider>
          <EditorProvider>
            <HelperSelectionProvider>
              <EntityDetails />
            </HelperSelectionProvider>
          </EditorProvider>
        </FailedChecksProvider>
      </HistoryProvider>
    </MachineryProvider>
  </SearchProvider>
);
