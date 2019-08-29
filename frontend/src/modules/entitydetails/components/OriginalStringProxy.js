/* @flow */

import * as React from 'react';

import { FluentOriginalString } from 'modules/fluentoriginal';

import OriginalString from './OriginalString';

import type { Entity } from 'core/api';
import type { Locale } from 'core/locales';


type Props = {|
    +entity: Entity,
    +locale: Locale,
    +pluralForm: number,
    +handleClickOnPlaceable: (SyntheticMouseEvent<HTMLParagraphElement>) => void,
|};


export default class OriginalStringProxy extends React.Component<Props> {
    render() {
        const props = this.props;

        if (props.entity.format === 'ftl') {
            return <FluentOriginalString
                entity={ props.entity }
                handleClickOnPlaceable={ props.handleClickOnPlaceable }
            />;
        }

        return <OriginalString
            entity={ props.entity }
            locale={ props.locale }
            pluralForm={ props.pluralForm }
            handleClickOnPlaceable={ props.handleClickOnPlaceable }
        />;
    }
}
