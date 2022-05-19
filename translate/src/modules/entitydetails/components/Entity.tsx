import React from 'react';

import { MachineryProvider } from '~/context/MachineryTranslations';
import { EntityViewProvider } from '~/context/EntityView';
import { SearchProvider } from '~/context/SearchData';
import { EntityDetails } from './EntityDetails';

export const Entity = () => (
  <EntityViewProvider>
    <SearchProvider>
      <MachineryProvider>
        <EntityDetails />
      </MachineryProvider>
    </SearchProvider>
  </EntityViewProvider>
);
