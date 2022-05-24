import React from 'react';

import { EntityViewProvider } from '~/context/EntityView';
import { HistoryProvider } from '~/context/HistoryData';
import { MachineryProvider } from '~/context/MachineryTranslations';
import { SearchProvider } from '~/context/SearchData';
import { EntityDetails } from './EntityDetails';

export const Entity = () => (
  <EntityViewProvider>
    <SearchProvider>
      <MachineryProvider>
        <HistoryProvider>
          <EntityDetails />
        </HistoryProvider>
      </MachineryProvider>
    </SearchProvider>
  </EntityViewProvider>
);
