import * as React from 'react';

import './PluralSelector.css';

import { getPluralExamples, Locale, NAME as LOCALE } from '~/core/locale';
import { AppStore, useAppDispatch, useAppSelector, useAppStore } from '~/hooks';
import { NAME as UNSAVEDCHANGES } from '~/modules/unsavedchanges';
import { check as checkUnsavedChanges } from '~/modules/unsavedchanges/actions';
import type { AppDispatch } from '~/store';

import { actions, CLDR_PLURALS, selectors } from '..';

type Props = {
  locale: Locale;
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
  locale,
  pluralForm,
  resetEditor,
  store,
}: InternalProps): React.ReactElement<'nav'> | null {
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

  if (pluralForm === -1 || !locale || locale.cldrPlurals.length <= 1) {
    return null;
  }

  const examples = getPluralExamples(locale);

  return (
    <nav className='plural-selector'>
      <ul>
        {locale.cldrPlurals.map((item, i) => {
          return (
            <li key={item} className={i === pluralForm ? 'active' : ''}>
              <button onClick={() => selectPluralForm(i)}>
                <span>{CLDR_PLURALS[item]}</span>
                <sup>{examples[item]}</sup>
              </button>
            </li>
          );
        })}
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
      locale={useAppSelector((state) => state[LOCALE])}
      pluralForm={useAppSelector((state) => selectors.getPluralForm(state))}
      store={useAppStore()}
    />
  );
}
