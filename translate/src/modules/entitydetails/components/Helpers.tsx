import { Localized } from '@fluent/react';
import React, { useContext } from 'react';
import { Tab, TabList, TabPanel, Tabs } from 'react-tabs';

import type { Entity } from '~/api/entity';
import { HelperSelection } from '~/context/HelperSelection';
import type { Location } from '~/context/Location';
import { useNarrowScreen } from '~/hooks/useNarrowScreen';
import type { TermState } from '~/modules/terms';
import type { UserState } from '~/modules/user';
import { Machinery, MachineryCount } from '~/modules/machinery';
import type { LocalesState } from '~/modules/otherlocales';
import { OtherLocales, OtherLocalesCount } from '~/modules/otherlocales';
import type { TeamCommentState } from '~/modules/teamcomments';
import { CommentCount, TeamComments } from '~/modules/teamcomments';
import { TermCount, Terms } from '~/modules/terms';

import './Helpers.css';

type Props = {
  entity: Entity;
  otherlocales: LocalesState;
  teamComments: TeamCommentState;
  terms: TermState;
  parameters: Location;
  user: UserState;
  commentTabRef: any; // Used to access <Tab> _reactInternalFiber
  commentTabIndex: number;
  contactPerson: string;
  togglePinnedStatus: (status: boolean, id: number) => void;
  navigateToPath: (path: string) => void;
  setCommentTabIndex: (index: number) => void;
  resetContactPerson: () => void;
};

/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export function Helpers({
  entity,
  otherlocales,
  teamComments,
  terms,
  parameters,
  user,
  commentTabRef,
  commentTabIndex,
  contactPerson,
  togglePinnedStatus,
  navigateToPath,
  setCommentTabIndex,
  resetContactPerson,
}: Props): React.ReactElement<any> {
  const { setTab } = useContext(HelperSelection);

  const isTerminologyProject = parameters.project === 'terminology';

  function MachineryTab() {
    return (
      <Tab>
        <Localized id='entitydetails-Helpers--machinery'>
          {'MACHINERY'}
        </Localized>
        <MachineryCount />
      </Tab>
    );
  }

  function OtherLocalesTab() {
    return (
      <Tab>
        <Localized id='entitydetails-Helpers--locales'>{'LOCALES'}</Localized>
        <OtherLocalesCount otherlocales={otherlocales} />
      </Tab>
    );
  }

  function TermsTab() {
    if (isTerminologyProject) {
      return null;
    }
    return (
      <Tab>
        <Localized id='entitydetails-Helpers--terms'>{'TERMS'}</Localized>
        <TermCount terms={terms} />
      </Tab>
    );
  }

  function CommentsTab() {
    return (
      <Tab ref={commentTabRef}>
        <Localized id='entitydetails-Helpers--comments'>{'COMMENTS'}</Localized>
        <CommentCount teamComments={teamComments} />
      </Tab>
    );
  }

  function MachineryPanel() {
    return (
      <TabPanel>
        <Machinery />
      </TabPanel>
    );
  }

  function OtherLocalesPanel() {
    return (
      <TabPanel>
        <OtherLocales
          entity={entity}
          otherlocales={otherlocales}
          parameters={parameters}
        />
      </TabPanel>
    );
  }

  function TermsPanel() {
    return isTerminologyProject ? null : (
      <TabPanel>
        <Terms terms={terms} navigateToPath={navigateToPath} />
      </TabPanel>
    );
  }

  function CommentsPanel() {
    return (
      <TabPanel>
        <TeamComments
          contactPerson={contactPerson}
          initFocus={!isTerminologyProject}
          teamComments={teamComments}
          user={user}
          togglePinnedStatus={togglePinnedStatus}
          resetContactPerson={resetContactPerson}
        />
      </TabPanel>
    );
  }

  if (useNarrowScreen()) {
    return (
      <>
        <div className='bottom'>
          <Tabs
            selectedIndex={commentTabIndex}
            onSelect={(index, lastIndex) => {
              if (index === lastIndex) {
                return false;
              } else {
                setTab(index);
              }
              setCommentTabIndex(index);
            }}
          >
            <TabList>
              <MachineryTab />
              <OtherLocalesTab />
              <TermsTab />
              <CommentsTab />
            </TabList>
            <MachineryPanel />
            <OtherLocalesPanel />
            <TermsPanel />
            <CommentsPanel />
          </Tabs>
        </div>
      </>
    );
  }

  return (
    <>
      <div className='top'>
        <Tabs
          selectedIndex={commentTabIndex}
          onSelect={(tab) => setCommentTabIndex(tab)}
        >
          <TabList>
            <TermsTab />
            <CommentsTab />
          </TabList>
          <TermsPanel />
          <CommentsPanel />
        </Tabs>
      </div>
      <div className='bottom'>
        <Tabs
          onSelect={(index, lastIndex) => {
            if (index === lastIndex) {
              return false;
            } else {
              setTab(index);
            }
          }}
        >
          <TabList>
            <MachineryTab />
            <OtherLocalesTab />
          </TabList>
          <MachineryPanel />
          <OtherLocalesPanel />
        </Tabs>
      </div>
    </>
  );
}
