import * as React from 'react';

import { useAppSelector } from 'hooks';
import { GenericTranslation } from 'core/translation';
import TranslationMemory from './source/TranslationMemory';

import type { MachineryTranslation } from 'core/api';

type Props = {
    sourceString: string;
    translation: MachineryTranslation;
};

export default function ConcordanceSearch(
    props: Props,
): React.ReactElement<any> {
    const locale = useAppSelector((state) => state.locale);
    const { sourceString, translation } = props;

    const createProjectList = () => {
        if (!translation.projectNames) {
            return null;
        }

        if (translation.projectNames.every((projectName) => !projectName)) {
            return <TranslationMemory />;
        }

        return (
            translation.projectNames &&
            translation.projectNames.map((project) => {
                return (
                    project && (
                        <li key={project}>
                            <span className='translation-source'>
                                <span>{project.toUpperCase()}</span>
                            </span>
                        </li>
                    )
                );
            })
        );
    };

    const getProjectNames = () => {
        if (!translation.projectNames) {
            return null;
        }

        return translation.projectNames
            .filter((projectName) => {
                return projectName !== null;
            })
            .join(' • ');
    };

    return (
        <>
            <header>
                <ul className='sources projects' title={getProjectNames()}>
                    {createProjectList()}
                </ul>
            </header>
            <p className='original'>
                <GenericTranslation
                    content={translation.original}
                    search={sourceString}
                />
            </p>
            <p
                className='suggestion'
                dir={locale.direction}
                data-script={locale.script}
                lang={locale.code}
            >
                <GenericTranslation
                    content={translation.translation}
                    search={sourceString}
                />
            </p>
        </>
    );
}
