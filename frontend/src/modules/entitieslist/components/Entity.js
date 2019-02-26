/* @flow */

import * as React from 'react';

import './Entity.css';

import { WithPlaceables } from 'core/placeable';

import type { Locale } from 'core/locales';
import type { DbEntity } from '../reducer';


type Props = {
    entity: DbEntity,
    locale: Locale,
    selected: boolean,
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
        const translation = this.props.entity.translation[0];

        if (translation.approved) {
            return 'approved';
        }
        if (translation.fuzzy) {
            return 'fuzzy';
        }
        return 'missing';
    }

    selectEntity = () => {
        this.props.selectEntity(this.props.entity);
    }

    render() {
        const { entity, locale, selected } = this.props;

        const classSelected = selected ? 'selected' : '';

        return (
            <li
                className={ `entity ${this.status} ${classSelected}` }
                onClick={ this.selectEntity }
            >
                <span className='status fa' />
                <div>
                    <p className='source-string'>
                        <WithPlaceables>
                            { entity.original }
                        </WithPlaceables>
                    </p>
                    <p
                        className='translation-string'
                        dir={ locale.direction }
                        lang={ locale.code }
                        data-script={ locale.script }
                    >
                        <WithPlaceables>
                            { entity.translation[0].string }
                        </WithPlaceables>
                    </p>
                </div>
            </li>
        );
    }
}
