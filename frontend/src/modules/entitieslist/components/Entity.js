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

/**
 * Displays a single Entity as a list element.
 *
 * The format of this element is: "[Status] Source (Translation)"
 *
 * "Status" is the current status of the translation. Can be:
 *   - "approved": there is an approved translation
 *   - "fuzzy": there is a fuzzy translation
 *   - "missing": there is no approved or fuzzy translations
 *
 * "Source" is the original string from the project. Usually it's the en-US string.
 *
 * "Translation" is the current "best" translation. It shows either the approved
 * translation, or the fuzzy translation, or the last suggested translation.
 */
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
