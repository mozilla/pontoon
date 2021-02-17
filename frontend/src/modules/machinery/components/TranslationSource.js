/* @flow */

import React from 'react';

import type { MachineryTranslation } from 'core/api';
import type { Locale } from 'core/locale';

import ConcordanceSearch from './source/ConcordanceSearch';
import GoogleTranslation from './source/GoogleTranslation';
import MicrosoftTranslation from './source/MicrosoftTranslation';
import SystranTranslation from './source/SystranTranslation';
import MicrosoftTerminology from './source/MicrosoftTerminology';
import CaighdeanTranslation from './source/CaighdeanTranslation';
import TranslationMemory from './source/TranslationMemory';

type Props = {|
    translation: MachineryTranslation,
    locale: Locale,
|};

/**
 * Shows a list of translation sources.
 */
export default function TranslationSource({ translation, locale }: Props) {
    const translationSource = translation.sources.map((source, index) => {
        switch (source) {
            case 'concordance-search':
                return !translation.projectNames ||
                    translation.projectNames.every(
                        (projectName) => !projectName,
                    ) ? (
                    <ConcordanceSearch key={index} emptyList={true} />
                ) : (
                    translation.projectNames.map((project) => {
                        return (
                            <ConcordanceSearch
                                projectName={project}
                                key={project}
                            />
                        );
                    })
                );
            case 'translation-memory':
                return (
                    <TranslationMemory
                        itemCount={translation.itemCount}
                        key={index}
                    />
                );
            case 'google-translate':
                return <GoogleTranslation key={index} />;
            case 'microsoft-translator':
                return <MicrosoftTranslation key={index} />;
            case 'systran-translate':
                return <SystranTranslation key={index} />;
            case 'microsoft-terminology':
                return (
                    <MicrosoftTerminology
                        original={translation.original}
                        locale={locale}
                        key={index}
                    />
                );
            case 'caighdean':
                return <CaighdeanTranslation key={index} />;
            default:
                return null;
        }
    });

    const isConcordanceSearch = 'projectNames' in translation;
    const getProjectNames = () => {
        if (!translation.projectNames) {
            return;
        }
        if (translation.projectNames.every((projectName) => !projectName)) {
            return 'Translation Memory';
        }

        return (
            translation.projectNames &&
            translation.projectNames
                .filter((projectName) => {
                    return projectName !== null;
                })
                .join(' • ')
        );
    };

    return (
        <ul
            className={isConcordanceSearch ? 'sources projects' : 'sources'}
            title={isConcordanceSearch && getProjectNames()}
        >
            {translationSource}
        </ul>
    );
}
