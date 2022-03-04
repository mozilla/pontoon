import React, { useContext } from 'react';

import { Locale } from '~/context/locale';
import { PluralFormType, usePluralForm } from '~/context/pluralForm';
import { useSelectedEntity } from '~/core/entities/hooks';
import { AppStore, useAppDispatch, useAppStore } from '~/hooks';
import { usePluralExamples } from '~/hooks/usePluralExamples';
import { NAME as UNSAVEDCHANGES } from '~/modules/unsavedchanges';
import { check as checkUnsavedChanges } from '~/modules/unsavedchanges/actions';
import type { AppDispatch } from '~/store';

import { CLDR_PLURALS } from '../index';
import './PluralSelector.css';

type Props = {
  pluralForm: PluralFormType;
};

type WrapperProps = {
  resetEditor: () => void;
};

type InternalProps = Props &
  WrapperProps & {
    dispatch: AppDispatch;
    store: AppStore;
  };

/**
 * Plural form picker component.
 *
 * Shows a list of available plural forms for the current locale, and allows
 * to change selected plural form.
 */
export function PluralSelectorBase({
  dispatch,
  pluralForm: { pluralForm, setPluralForm },
  resetEditor,
  store,
}: InternalProps): React.ReactElement<'nav'> | null {
  const locale = useContext(Locale);
  const { cldrPlurals } = locale;
  const examples = usePluralExamples(locale);

  function selectPluralForm(nextPluralForm: number) {
    if (pluralForm !== nextPluralForm) {
      const state = store.getState();
      const { exist, ignored } = state[UNSAVEDCHANGES];

      dispatch(
        checkUnsavedChanges(exist, ignored, () => {
          resetEditor();
          setPluralForm(nextPluralForm);
        }),
      );
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

export default function PluralSelector(
  props: WrapperProps,
): React.ReactElement<typeof PluralSelectorBase> {
  return (
    <PluralSelectorBase
      {...props}
      dispatch={useAppDispatch()}
      pluralForm={usePluralForm(useSelectedEntity())}
      store={useAppStore()}
    />
  );
}
