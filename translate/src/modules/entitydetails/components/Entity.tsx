import React from 'react';

import { PluralFormProvider } from '~/context/pluralForm';
import { EntityDetails } from './EntityDetails';

export const Entity = () => (
  <PluralFormProvider>
    <EntityDetails />
  </PluralFormProvider>
);
