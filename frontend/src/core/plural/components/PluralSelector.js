/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './PluralSelector.css';

import { actions, selectors } from '..';
import * as locales from 'core/locales';

import type { Locale } from 'core/locales';


type Props = {|
    pluralForm: number,
    locale: Locale,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};


const CLDR_PLURALS: Array<string> = [
    'zero',
    'one',
    'two',
    'few',
    'many',
    'other',
];


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

        this.props.dispatch(actions.select(pluralForm));
    }

    render() {
        const { pluralForm, locale } = this.props;

        if (pluralForm === -1 || !locale || locale.cldrPlurals.length <= 1) {
            return null;
        }

        const nbPlurals = locale.cldrPlurals.length;
        const examples = {};

        if (nbPlurals === 2) {
            examples[locale.cldrPlurals[0]] = 1;
            examples[locale.cldrPlurals[1]] = 2;
        }
        else {
            // This variable is used in the pluralRule we eval in the while block.
            let n = 0;
            while (Object.keys(examples).length < nbPlurals) {
                // This `eval` is not so much evil. The pluralRule we parse
                // comes from our database and is not a user input.
                // eslint-disable-next-line
                const rule = eval(locale.pluralRule);
                if (!examples[locale.cldrPlurals[rule]]) {
                    examples[locale.cldrPlurals[rule]] = n;
                }
                n++;
            }
        }

        return <nav className="plural-selector">
            <ul>
                { locale.cldrPlurals.map((item, i) => {
                    return <li key={ item } className={ i === pluralForm ? 'active' : '' }>
                        <button onClick={ () => this.selectPluralForm(i) }>
                            <span>{ CLDR_PLURALS[item] }</span>
                            <sup>{ examples[item] }</sup>
                        </button>
                    </li>;
                }) }
            </ul>
        </nav>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        pluralForm: selectors.getPluralForm(state),
        locale: locales.selectors.getCurrentLocaleData(state),
    };
};

export default connect(mapStateToProps)(PluralSelectorBase);
