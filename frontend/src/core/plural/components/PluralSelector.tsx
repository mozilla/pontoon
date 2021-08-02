import * as React from 'react';
import { useDispatch, useStore } from 'react-redux';

import './PluralSelector.css';

import { useAppSelector } from 'hooks';
import * as locale from 'core/locale';
import * as unsavedchanges from 'modules/unsavedchanges';

import { actions, CLDR_PLURALS, selectors } from '..';

import type { Locale } from 'core/locale';

type Props = {
    locale: Locale;
    pluralForm: number;
};

type WrapperProps = {
    resetEditor: (...args: Array<any>) => any;
};

type InternalProps = Props &
    WrapperProps & {
        dispatch: (...args: Array<any>) => any;
        store: Record<string, any>;
    };

/**
 * Plural form picker component.
 *
 * Shows a list of available plural forms for the current locale, and allows
 * to change selected plural form.
 */
export class PluralSelectorBase extends React.Component<InternalProps> {
    selectPluralForm(pluralForm: number) {
        if (this.props.pluralForm === pluralForm) {
            return;
        }

        const { dispatch } = this.props;

        const state = this.props.store.getState();
        const unsavedChangesExist = state[unsavedchanges.NAME].exist;
        const unsavedChangesIgnored = state[unsavedchanges.NAME].ignored;

        dispatch(
            unsavedchanges.actions.check(
                unsavedChangesExist,
                unsavedChangesIgnored,
                () => {
                    this.props.resetEditor();
                    dispatch(actions.select(pluralForm));
                },
            ),
        );
    }

    render(): null | React.ReactElement<'nav'> {
        const props = this.props;
        const { pluralForm } = props;

        if (
            pluralForm === -1 ||
            !props.locale ||
            props.locale.cldrPlurals.length <= 1
        ) {
            return null;
        }

        const examples = locale.getPluralExamples(props.locale);

        return (
            <nav className='plural-selector'>
                <ul>
                    {props.locale.cldrPlurals.map((item, i) => {
                        return (
                            <li
                                key={item}
                                className={i === pluralForm ? 'active' : ''}
                            >
                                <button
                                    onClick={() => this.selectPluralForm(i)}
                                >
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
}

export default function PluralSelector(
    props: WrapperProps,
): React.ReactElement<typeof PluralSelectorBase> {
    const state = {
        locale: useAppSelector((state) => state[locale.NAME]),
        pluralForm: useAppSelector((state) => selectors.getPluralForm(state)),
    };

    return (
        <PluralSelectorBase
            {...props}
            {...state}
            dispatch={useDispatch()}
            store={useStore()}
        />
    );
}
