import { Localized } from '@fluent/react';
import React, { useCallback, useRef, useState } from 'react';

import { useProject } from '~/modules/project';
import { useOnDiscard } from '~/utils';

import './ProjectInfo.css';

function ProjectInfoDialog({
  info,
  onDiscard,
}: {
  info: string;
  onDiscard: () => void;
}): React.ReactElement<'aside'> {
  const ref = useRef<HTMLElement>(null);
  useOnDiscard(ref, onDiscard);

  // We can safely use project.info because it is validated by bleach
  // before being saved into the database.
  return (
    <aside ref={ref} className='panel'>
      <Localized id='projectinfo-ProjectInfo--project-info-title'>
        <h2>PROJECT INFO</h2>
      </Localized>
      <p dangerouslySetInnerHTML={{ __html: info }} />
    </aside>
  );
}

/**
 * Show a panel with the information provided for the current project.
 */
export function ProjectInfo(): React.ReactElement<'div'> | null {
  const { fetching, info } = useProject();
  const [visible, setVisible] = useState(false);
  const toggleVisible = useCallback(() => setVisible((prev) => !prev), []);
  const handleDiscard = useCallback(() => setVisible(false), []);

  return fetching || !info ? null : (
    <div className='project-info'>
      <div className='button' onClick={toggleVisible}>
        <span className='fa fa-info'></span>
      </div>
      {visible && <ProjectInfoDialog info={info} onDiscard={handleDiscard} />}
    </div>
  );
}
