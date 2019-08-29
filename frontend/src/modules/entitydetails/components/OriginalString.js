/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import { WithPlaceables } from 'core/placeable';

import type { Entity } from 'core/api';
import type { Locale } from 'core/locales';


type Props = {|
    +entity: Entity,
    +locale: Locale,
    +pluralForm: number,
    +handleClickOnPlaceable: (SyntheticMouseEvent<HTMLParagraphElement>) => void,
|};


export default class OriginalString extends React.Component<Props> {
    getOriginalContent() {
        const { entity, locale, pluralForm } = this.props;

        if (pluralForm === -1) {
            return {
                title: null,
                original: entity.original,
            };
        }

        if (locale.cldrPlurals[pluralForm] === 1) {
            return {
                title: <Localized id='entitydetails-OriginalString--singular'>
                    <h2>Singular</h2>
                </Localized>,
                original: entity.original,
            };
        }

        return {
            title: <Localized id='entitydetails-OriginalString--plural'>
                <h2>Plural</h2>
            </Localized>,
            original: entity.original_plural,
        };
    }

    render() {
        const { title, original } = this.getOriginalContent();

        return <>
            { title }
            <p className="original" onClick={ this.props.handleClickOnPlaceable }>
                <WithPlaceables>
                    { original }
                </WithPlaceables>
            </p>
        </>;
    }
}
