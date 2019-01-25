/* @flow */

import React from 'react';
import { connect } from 'react-redux';
import { Localized } from 'fluent-react';

import './Machinery.css';

import * as locales from 'core/locales';

import { NAME } from '..';
import Translation from './Translation';

import type { Locale } from 'core/locales';
import type { MachineryState } from '../reducer';


type Props = {|
    locale: ?Locale,
    machinery: MachineryState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};


/**
 *
 */
export class MachineryBase extends React.Component<InternalProps> {
    render() {
        const { locale, machinery } = this.props;

        if (!locale) {
            return null;
        }

        return <section className="machinery">
            <div className="search-wrapper clearfix">
                <div className="icon fa fa-search"></div>
                <Localized id="machinery-machinery-search-placeholder" attrs={{ placeholder: true }}>
                    <input type="search" autoComplete="off" placeholder="Type to search machinery" />
                </Localized>
            </div>
            <ul>
                { machinery.translations.map((item, i) => {
                    return <Translation
                        translation={ item }
                        locale={ locale }
                        key={ i }
                    />;
                }) }
            </ul>
        </section>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        locale: locales.selectors.getCurrentLocaleData(state),
        machinery: state[NAME],
    };
};

export default connect(mapStateToProps)(MachineryBase);
