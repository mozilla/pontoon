import * as React from 'react';

import { useAppSelector } from '~/hooks';
import { GenericTranslation } from '~/core/translation';
import TranslationMemory from './source/TranslationMemory';

import type { MachineryTranslation } from '~/core/api';

type Props = {
  sourceString: string;
  translation: MachineryTranslation;
};

function ProjectList({ projects }: { projects: (string | null)[] }) {
  const notEmpty = projects.filter(Boolean) as string[];

  if (notEmpty.length === 0) {
    return <TranslationMemory />;
  }

  return (
    <>
      {notEmpty.map((project) => (
        <li key={project}>
          <span className='translation-source'>
            <span>{project.toUpperCase()}</span>
          </span>
        </li>
      ))}
    </>
  );
}

export function ConcordanceSearch({
  sourceString,
  translation,
}: Props): React.ReactElement {
  const locale = useAppSelector((state) => state.locale);
  const projects = translation.projectNames;
  const title = !projects ? undefined : projects.filter(Boolean).join(' • ');

  return (
    <>
      <header>
        <ul className='sources projects' title={title}>
          {projects && <ProjectList projects={projects} />}
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
