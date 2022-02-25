import React, { useContext } from 'react';

import './PluralSelector.css';

import { Locale } from '~/context/locale';
import { AppStore, useAppDispatch, useAppSelector, useAppStore } from '~/hooks';
import { NAME as UNSAVEDCHANGES } from '~/modules/unsavedchanges';
import { check as checkUnsavedChanges } from '~/modules/unsavedchanges/actions';
import type { AppDispatch } from '~/store';

import { actions, CLDR_PLURALS, selectors } from '..';
import { usePluralExamples } from '~/hooks/usePluralExamples';

type Props = {
  pluralForm: number;
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
  pluralForm,
  resetEditor,
  store,
}: InternalProps): React.ReactElement<'nav'> | null {
  const { cldrPlurals } = useContext(Locale);
  const examples = usePluralExamples();

  function selectPluralForm(nextPluralForm: number) {
    if (pluralForm !== nextPluralForm) {
      const state = store.getState();
      const { exist, ignored } = state[UNSAVEDCHANGES];

      dispatch(
        checkUnsavedChanges(exist, ignored, () => {
          resetEditor();
          dispatch(actions.select(nextPluralForm));
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
      pluralForm={useAppSelector((state) => selectors.getPluralForm(state))}
      store={useAppStore()}
    />
  );
}
