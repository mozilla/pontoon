import React from 'react';

import { MachineryProvider } from '~/context/MachineryTranslations';
import { PluralFormProvider } from '~/context/pluralForm';
import { SearchProvider } from '~/context/SearchData';
import { EntityDetails } from './EntityDetails';

export const Entity = () => (
  <SearchProvider>
    <MachineryProvider>
      <PluralFormProvider>
        <EntityDetails />
      </PluralFormProvider>
    </MachineryProvider>
  </SearchProvider>
);
