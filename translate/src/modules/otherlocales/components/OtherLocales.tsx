import { Localized } from '@fluent/react';
import React from 'react';

import type { Entity } from '~/api/entity';
import type { Location } from '~/context/Location';

import type { LocalesState } from '../index';
import './OtherLocales.css';
import { OtherLocaleTranslationComponent } from './OtherLocaleTranslation';

type Props = {
  entity: Entity;
  otherlocales: LocalesState;
  parameters: Location;
};

/**
 * Shows all translations of an entity in locales other than the current one.
 */
export function OtherLocales({
  entity,
  otherlocales: { fetching, translations },
  parameters,
}: Props): React.ReactElement<'section'> | null {
  if (fetching) {
    return null;
  }

  if (!translations.length) {
    return (
      <section className='other-locales'>
        <Localized id='history-history-no-translations'>
          <p>No translations available.</p>
        </Localized>
      </section>
    );
  }

  return (
    <section className='other-locales'>
      <ul className='preferred-list'>
        {translations.map((translation, index) =>
          translation.is_preferred ? (
            <OtherLocaleTranslationComponent
              entity={entity}
              index={index}
              key={index}
              parameters={parameters}
              translation={translation}
            />
          ) : null,
        )}
      </ul>

      <ul>
        {translations.map((translation, index) =>
          translation.is_preferred ? null : (
            <OtherLocaleTranslationComponent
              entity={entity}
              index={index}
              key={index}
              parameters={parameters}
              translation={translation}
            />
          ),
        )}
      </ul>
    </section>
  );
}
