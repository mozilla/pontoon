/* @flow */

import React from 'react';

import './Entity.css';


type Translation = {
    string: string,
    approved: boolean,
    fuzzy: boolean,
};

type Props = {
    entity: {
        original: string,
        translation: Array<Translation>,
    },
    selectEntity: Function,
};

export default class Entity extends React.Component<Props> {
    get status(): string {
        const { entity } = this.props;
        const translation = entity.translation[0];

        if (translation.approved) {
            return 'approved';
        }
        if (translation.fuzzy) {
            return 'fuzzy';
        }
        return 'missing';
    }

    render() {
        const { entity, selectEntity } = this.props;

        return (
            <li className={ `entity ${this.status}` } onClick={ selectEntity }>
                <span className='status fa' />
                <span className='source-string'>{ entity.original }</span>
                <span className='translation-string'>{ entity.translation[0].string }</span>
            </li>
        );
    }
}
