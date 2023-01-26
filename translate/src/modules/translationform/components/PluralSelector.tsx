import React, { useContext } from 'react';

import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { UnsavedActions } from '~/context/UnsavedChanges';
import { CLDR_PLURALS } from '~/utils/constants';
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
  const { hasPluralForms, pluralForm, setPluralForm } = useContext(EntityView);

  return hasPluralForms ? (
    <nav className='plural-selector'>
      <ul>
        {cldrPlurals.map((item, i) => {
          const active = i === pluralForm;
          const handleClick = active
            ? undefined
            : () => checkUnsavedChanges(() => setPluralForm(i));
          return (
            <li key={item} className={active ? 'active' : undefined}>
              <button onClick={handleClick}>
                <span>{CLDR_PLURALS[item]}</span>
                <sup>{examples[item]}</sup>
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  ) : null;
}
