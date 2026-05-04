import React, { useContext } from 'react';

import type { MachineryTranslation } from '~/api/machinery';
import { Locale } from '~/context/Locale';
import { GenericTranslation } from '~/modules/translation';

import { TranslationMemory } from './source/TranslationMemory';

type Props = {
  sourceString: string;
  translation: MachineryTranslation;
};

type project = {
  name: string;
  slug: string;
};

function ProjectList({ projects }: { projects: project[] }) {
  if (projects.length === 0) {
    return <TranslationMemory />;
  }

  return (
    <>
      {projects.map((project) => (
        <li key={project.name}>
          <span className='translation-source'>
            <span>{project.name.toUpperCase()}</span>
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
  const { code, direction, script } = useContext(Locale);
  const projects = translation.projects;
  const entities = translation.entities;

  const title = projects?.map((project) => project.name).join(' • ');

  const projectListContainer = (
    <ul className='sources projects' title={title}>
      {projects && <ProjectList projects={projects} />}
    </ul>
  );

  return (
    <>
      <header>
        {entities && entities.length > 0 ? (
          <a
            href={`/${code}/all-projects/all-resources/?list=${entities.join(',')}`}
            onClick={(e) => e.stopPropagation()}
          >
            {projectListContainer}
          </a>
        ) : (
          <div>{projectListContainer}</div>
        )}
      </header>
      <p className='original'>
        <GenericTranslation
          content={translation.original}
          search={sourceString}
        />
      </p>
      <p
        className='suggestion'
        dir={direction}
        data-script={script}
        lang={code}
      >
        <GenericTranslation
          content={translation.translation}
          search={sourceString}
        />
      </p>
    </>
  );
}
