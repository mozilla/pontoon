import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

import { EntityView, useActiveTranslation } from '~/context/EntityView';
import { Location } from '~/context/Location';
import { UnsavedActions } from '~/context/UnsavedChanges';
import { Editor } from '~/modules/editor/components/Editor';
import { TERM } from '~/modules/terms';
import { get as getTerms } from '~/modules/terms/actions';
import { USER } from '~/modules/user';
import { useAppDispatch, useAppSelector, useAppStore } from '~/hooks';
import { History } from '~/modules/history/components/History';
import { OTHERLOCALES } from '~/modules/otherlocales';
import { get as getOtherLocales } from '~/modules/otherlocales/actions';
import { TEAM_COMMENTS } from '~/modules/teamcomments';
import {
  get as getTeamComments,
  request as requestTeamComments,
  togglePinnedStatus as togglePinnedTeamCommentStatus,
} from '~/modules/teamcomments/actions';
import { getPlainMessage } from '~/utils/message';

import './EntityDetails.css';
import { EntityNavigation } from './EntityNavigation';
import { Helpers } from './Helpers';
import { Metadata } from './Metadata';

/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export function EntityDetails(): React.ReactElement<'section'> | null {
  const location = useContext(Location);
  const otherlocales = useAppSelector((state) => state[OTHERLOCALES]);
  const teamComments = useAppSelector((state) => state[TEAM_COMMENTS]);
  const terms = useAppSelector((state) => state[TERM]);
  const user = useAppSelector((state) => state[USER]);
  const dispatch = useAppDispatch();
  const store = useAppStore();

  const activeTranslation = useActiveTranslation();
  const { entity: selectedEntity } = useContext(EntityView);

  const commentTabRef = useRef<{ _reactInternalFiber: { index: number } }>(
    null,
  );
  const [commentTabIndex, setCommentTabIndex] = useState(0);
  const [contactPerson, setContactPerson] = useState('');
  const resetContactPerson = useCallback(() => setContactPerson(''), []);
  const { checkUnsavedChanges } = useContext(UnsavedActions);

  const { entity, locale: lc, project } = location;

  useEffect(() => {
    const { format, machinery_original, pk } = selectedEntity;
    const source = getPlainMessage(machinery_original, format);

    if (source !== terms.sourceString && project !== 'terminology') {
      dispatch(getTerms(source, lc));
    }

    if (pk !== otherlocales.entity) {
      dispatch(getOtherLocales(entity, lc));
    }

    if (pk !== teamComments.entity) {
      dispatch(requestTeamComments(entity));
      dispatch(getTeamComments(entity, lc));
    }
  }, [activeTranslation]);

  const navigateToPath = useCallback(
    (path: string) => checkUnsavedChanges(() => location.push(path)),
    [dispatch, location, store],
  );

  const togglePinnedStatus = useCallback(
    (pinned: boolean, commentId: number) =>
      dispatch(togglePinnedTeamCommentStatus(pinned, commentId)),
    [dispatch],
  );

  // No content while loading entity data
  return selectedEntity.pk === 0 ? null : (
    <section className='entity-details'>
      <section className='main-column'>
        <EntityNavigation />
        <Metadata
          entity={selectedEntity}
          terms={terms}
          navigateToPath={navigateToPath}
          teamComments={teamComments}
          user={user}
          commentTabRef={commentTabRef}
          setCommentTabIndex={setCommentTabIndex}
          setContactPerson={setContactPerson}
        />
        <Editor />
        <History />
      </section>
      <section className='third-column'>
        <Helpers
          entity={selectedEntity}
          otherlocales={otherlocales}
          teamComments={teamComments}
          terms={terms}
          togglePinnedStatus={togglePinnedStatus}
          parameters={location}
          user={user}
          navigateToPath={navigateToPath}
          commentTabRef={commentTabRef}
          commentTabIndex={commentTabIndex}
          setCommentTabIndex={setCommentTabIndex}
          contactPerson={contactPerson}
          resetContactPerson={resetContactPerson}
        />
      </section>
    </section>
  );
}
