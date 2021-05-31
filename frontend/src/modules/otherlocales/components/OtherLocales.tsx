import * as React from 'react';
import { Localized } from '@fluent/react';

import './OtherLocales.css';

import Translation from './Translation';

import type { Entity, OtherLocaleTranslation } from 'core/api';
import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import type { LocalesState } from '..';

type Props = {
    entity: Entity;
    otherlocales: LocalesState;
    parameters: NavigationParams;
    user: UserState;
};

/**
 * Shows all translations of an entity in locales other than the current one.
 */
export default class OtherLocales extends React.Component<Props> {
    renderNoResults(): React.ReactElement<'section'> {
        return (
            <section className='other-locales'>
                <Localized id='history-history-no-translations'>
                    <p>No translations available.</p>
                </Localized>
            </section>
        );
    }

    renderTranslations(
        translation: OtherLocaleTranslation,
        index: number,
    ): React.ReactElement<React.ElementType> {
        return (
            <Translation
                index={index}
                entity={this.props.entity}
                translation={translation}
                parameters={this.props.parameters}
                key={index}
            />
        );
    }

    render(): null | React.ReactElement<'section'> {
        const { otherlocales } = this.props;

        if (otherlocales.fetching) {
            return null;
        }

        const translations = otherlocales.translations;

        if (!translations.length) {
            return this.renderNoResults();
        }

        return (
            <section className='other-locales'>
                <ul className='preferred-list'>
                    {translations.map((translation, index) =>
                        translation.is_preferred
                            ? this.renderTranslations(translation, index)
                            : null,
                    )}
                </ul>

                <ul>
                    {translations.map((translation, index) =>
                        !translation.is_preferred
                            ? this.renderTranslations(translation, index)
                            : null,
                    )}
                </ul>
            </section>
        );
    }
}
