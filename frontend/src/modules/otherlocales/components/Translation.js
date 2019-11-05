/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';
import { Link } from 'react-router-dom';

import './Translation.css';

import { TranslationProxy } from 'core/translation';

import type { Entity } from 'core/api';
import type { NavigationParams } from 'core/navigation';


type Props = {|
    entity: Entity,
    isReadOnlyEditor: boolean,
    translation: Object,
    parameters: NavigationParams,
    updateEditorTranslation: (string, string) => void,
|};


/**
 * Render a Translation in the Locales tab.
 *
 * Show the translation of a given entity in a different locale, as well as the
 * locale and its code.
 */
export default class Translation extends React.Component<Props> {
    copyTranslationIntoEditor = () => {
        if (this.props.isReadOnlyEditor) {
            return;
        }

        // Ignore if selecting text
        if (window.getSelection().toString()) {
            return;
        }

        this.props.updateEditorTranslation(this.props.translation.translation, 'otherlocales');
    }

    render() {
<<<<<<< HEAD
        const { entity, translation, parameters, isReadOnlyEditor } = this.props;

        let className = 'translation';
=======
        const { entity, translation, parameters, lastPreferred, isReadOnlyEditor } = this.props;

        let className = lastPreferred ? 'translation last-preferred' : 'translation';
>>>>>>> Fix bug 1545964 - Confusing Copy Into Translate tooltip (#1417)

        if (isReadOnlyEditor) {
            // Copying into the editor is not allowed
            className += ' cannot-copy'
        }

        return <Localized id='otherlocales-Translation--copy' attrs={{ title: true }}>
            <li
                className={ className }
                title='Copy Into Translation'
                onClick={ this.copyTranslationIntoEditor }
            >
                <header>
<<<<<<< HEAD
                    { translation.locale.code === 'en-US' ?
                        <Localized
                            id='otherlocales-Translation--header-link'
                            $locale={ translation.locale.name }
                            $code={ translation.locale.code }
                        >
                            <div>
                                { translation.locale.name }
                                <span>{ translation.locale.code }</span>
                            </div>
                        </Localized>
                    :
                        <Localized
                            id='otherlocales-Translation--header-link'
                            attrs={{ title: true }}
                            $locale={ translation.locale.name }
                            $code={ translation.locale.code }
                        >
                            <Link
                                to={ `/${translation.locale.code}/${parameters.project}/${parameters.resource}/?string=${parameters.entity}` }
                                target='_blank'
                                rel='noopener noreferrer'
                                title='Open string in { $locale } ({ $code })'
                                onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                            >
                                { translation.locale.name }
                                <span>{ translation.locale.code }</span>
                            </Link>
                        </Localized>
                    }
=======
                    <Localized
                        id='otherlocales-Translation--header-link'
                        attrs={{ title: true }}
                        $locale={ translation.locale }
                        $code={ translation.code }
                    >
                        <Link
                            to={ `/${translation.code}/${parameters.project}/${parameters.resource}/?string=${parameters.entity}` }
                            target='_blank'
                            rel='noopener noreferrer'
                            title='Open string in { $locale } ({ $code })'
                            onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                        >
                            { translation.locale }
                            <span>{ translation.code }</span>
                        </Link>
                    </Localized>
>>>>>>> Fix bug 1545964 - Confusing Copy Into Translate tooltip (#1417)
                </header>
                <p
                    lang={ translation.locale.code }
                    dir={ translation.locale.direction }
                    script={ translation.locale.script }
                >
                    <TranslationProxy
                        content={ translation.translation }
                        format={ entity.format }
                    />
                </p>
            </li>
        </Localized>;
    }
}
