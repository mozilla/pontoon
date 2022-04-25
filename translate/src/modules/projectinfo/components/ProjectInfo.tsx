import { Localized } from '@fluent/react';
import React, { useCallback, useRef, useState } from 'react';

import type { ProjectState } from '~/core/project';
import { useOnDiscard } from '~/core/utils';

import './ProjectInfo.css';

type Props = {
  project: ProjectState;
};

/**
 * Show a panel with the information provided for the current project.
 */
export function ProjectInfo({
  project: { fetching, info },
}: Props): React.ReactElement<'div'> | null {
  const [visible, setVisible] = useState(false);
  const toggleVisible = useCallback(() => setVisible((prev) => !prev), []);
  const handleDiscard = useCallback(() => setVisible(false), []);

  return fetching || !info ? null : (
    <div className='project-info'>
      <div className='button' onClick={toggleVisible}>
        <span className='fa fa-info'></span>
      </div>
      {visible && <ProjectInfoPanel info={info} onDiscard={handleDiscard} />}
    </div>
  );
}

function ProjectInfoPanel({
  info,
  onDiscard,
}: {
  info: string;
  onDiscard: () => void;
}) {
  const ref = useRef<HTMLElement>(null);
  useOnDiscard(ref, onDiscard);

  return (
    <aside ref={ref} className='panel'>
      <Localized id='projectinfo-ProjectInfo--project-info-title'>
        <h2>PROJECT INFO</h2>
      </Localized>
      {/* We can safely use project.info because it is validated
          by bleach before being saved into the database. */}
      <p dangerouslySetInnerHTML={{ __html: info }} />
    </aside>
  );
}
