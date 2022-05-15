import React, { useContext } from 'react';

import { Locale } from '~/context/Locale';
import { usePluralForm } from '~/context/PluralForm';
import { UnsavedActions } from '~/context/UnsavedChanges';
import { useSelectedEntity } from '~/core/entities/hooks';
import { CLDR_PLURALS } from '~/core/utils/constants';
import { usePluralExamples } from '~/hooks/usePluralExamples';

import './PluralSelector.css';

/**
 * Plural form picker component.
 *
 * Shows a list of available plural forms for the current locale, and allows
 * to change selected plural form.
 */
export function PluralSelector(): React.ReactElement<'nav'> | null {
  const locale = useContext(Locale);
  const { cldrPlurals } = locale;
  const examples = usePluralExamples(locale);
  const { checkUnsavedChanges } = useContext(UnsavedActions);
  const entity = useSelectedEntity();
  const { pluralForm, setPluralForm } = usePluralForm(entity);

  if (
    pluralForm === -1 ||
    cldrPlurals.length <= 1 ||
    entity?.format === 'ftl'
  ) {
    return null;
  }

  return (
    <nav className='plural-selector'>
      <ul>
        {cldrPlurals.map((item, i) =>
          i === pluralForm ? (
            <li key={item} className='active'>
              <button>
                <span>{CLDR_PLURALS[item]}</span>
                <sup>{examples[item]}</sup>
              </button>
            </li>
          ) : (
            <li key={item}>
              <button
                onClick={() => checkUnsavedChanges(() => setPluralForm(i))}
              >
                <span>{CLDR_PLURALS[item]}</span>
                <sup>{examples[item]}</sup>
              </button>
            </li>
          ),
        )}
      </ul>
    </nav>
  );
}
