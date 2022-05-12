import React, { useContext } from 'react';

import { Locale } from '~/context/locale';
import { PluralForm, usePluralForm } from '~/context/pluralForm';
import { useCheckUnsavedChanges } from '~/context/unsavedChanges';
import { useSelectedEntity } from '~/core/entities/hooks';
import { CLDR_PLURALS } from '~/core/utils/constants';
import { usePluralExamples } from '~/hooks/usePluralExamples';

import './PluralSelector.css';

interface Props {
  resetEditor: () => void;
}

interface InternalProps extends Props {
  pluralForm: PluralForm;
}

/**
 * Plural form picker component.
 *
 * Shows a list of available plural forms for the current locale, and allows
 * to change selected plural form.
 */
export function PluralSelectorBase({
  pluralForm: { pluralForm, setPluralForm },
  resetEditor,
}: InternalProps): React.ReactElement<'nav'> | null {
  const locale = useContext(Locale);
  const { cldrPlurals } = locale;
  const examples = usePluralExamples(locale);
  const checkUnsavedChanges = useCheckUnsavedChanges();

  function selectPluralForm(nextPluralForm: number) {
    if (pluralForm !== nextPluralForm) {
      checkUnsavedChanges(() => {
        resetEditor();
        setPluralForm(nextPluralForm);
      });
    }
  }

  if (pluralForm === -1 || cldrPlurals.length <= 1) {
    return null;
  }

  return (
    <nav className='plural-selector'>
      <ul>
        {cldrPlurals.map((item, i) => (
          <li key={item} className={i === pluralForm ? 'active' : ''}>
            <button onClick={() => selectPluralForm(i)}>
              <span>{CLDR_PLURALS[item]}</span>
              <sup>{examples[item]}</sup>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export function PluralSelector(
  props: Props,
): React.ReactElement<typeof PluralSelectorBase> {
  return (
    <PluralSelectorBase
      {...props}
      pluralForm={usePluralForm(useSelectedEntity())}
    />
  );
}
