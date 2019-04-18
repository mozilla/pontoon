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
 *   - "errors": one of the plural forms has errors and is approved or fuzzy
 *   - "warnings": one of the plural forms has warnings and is approved or fuzzy
 *   - "approved": all plural forms are approved and don't have errors or warnings
 *   - "fuzzy": all plural forms are fuzzy and don't have errors or warnings
 *   - "partial": some plural forms have either approved or fuzzy translations, but not all
 *   - "missing": none of the plural forms have an approved or fuzzy translation
 *
 * "Source" is the original string from the project. Usually it's the en-US string.
 *
 * "Translation" is the current "best" translation. It shows either the approved
 * translation, or the fuzzy translation, or the last suggested translation.
 */
export default class Entity extends React.Component<Props> {
    get status(): string {
        const translations = this.props.entity.translation;
        let approved = 0;
        let fuzzy = 0;
        let errors = 0;
        let warnings = 0;

        translations.forEach(function (translation) {
            if (
                translation.errors.length &&
                (translation.approved || translation.fuzzy)
            ) {
                errors++;
            }
            else if (
                translation.warnings.length &&
                (translation.approved || translation.fuzzy)
            ) {
                warnings++;
            }
            else if (translation.approved) {
                approved++;
            }
            else if (translation.fuzzy) {
                fuzzy++;
            }
        });

        if (errors > 0) {
            return 'errors';
        }
        else if (warnings > 0) {
            return 'warnings';
        }
        else if (approved === translations.length) {
            return 'approved';
        }
        else if (fuzzy === translations.length) {
            return 'fuzzy';
        }
        else if (approved > 0 || fuzzy > 0) {
            return 'partial';
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
