import { Localized } from '@fluent/react';
import React, { useContext } from 'react';
import { Tab, TabList, TabPanel, Tabs } from 'react-tabs';

import type { Entity } from '~/api/entity';
import { HelperSelection } from '~/context/HelperSelection';
import type { Location } from '~/context/Location';
import { useWindowWidth } from '~/hooks/useWindowWidth';
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
  const windowWidth = useWindowWidth();

  const isTerminologyProject = parameters.project === 'terminology';

  function MachineryTab() {
    return (
      <>
        <Localized id='entitydetails-Helpers--machinery'>
          {'MACHINERY'}
        </Localized>
        <MachineryCount />
      </>
    );
  }

  function OtherLocalesTab() {
    return (
      <>
        <Localized id='entitydetails-Helpers--locales'>{'LOCALES'}</Localized>
        <OtherLocalesCount otherlocales={otherlocales} />
      </>
    );
  }

  function TermsTab() {
    return (
      <>
        <Localized id='entitydetails-Helpers--terms'>{'TERMS'}</Localized>
        <TermCount terms={terms} />
      </>
    );
  }

  function CommentsTab() {
    return (
      <>
        <Localized id='entitydetails-Helpers--comments'>{'COMMENTS'}</Localized>
        <CommentCount teamComments={teamComments} />
      </>
    );
  }

  function MachineryPanel() {
    return (
      <>
        <Machinery />
      </>
    );
  }

  function OtherLocalesPanel() {
    return (
      <>
        <OtherLocales
          entity={entity}
          otherlocales={otherlocales}
          parameters={parameters}
        />
      </>
    );
  }

  function TermsPanel() {
    return (
      <>
        <Terms terms={terms} navigateToPath={navigateToPath} />
      </>
    );
  }

  if (windowWidth === 'narrow' || windowWidth === 'medium') {
    return (
      <>
        <div className='bottom' data-testid='helpers'>
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
              <Tab>
                <MachineryTab />
              </Tab>
              <Tab>
                <OtherLocalesTab />
              </Tab>
              {isTerminologyProject ? null : (
                <Tab>
                  <TermsTab />
                </Tab>
              )}
              <Tab ref={commentTabRef}>
                <CommentsTab />
              </Tab>
            </TabList>
            <TabPanel>
              <MachineryPanel />
            </TabPanel>
            <TabPanel>
              <OtherLocalesPanel />
            </TabPanel>
            {isTerminologyProject ? null : (
              <TabPanel>
                <TermsPanel />
              </TabPanel>
            )}
            <TabPanel>
              {/* HACK: Required inline due to https://github.com/mozilla/pontoon/issues/2300 */}
              <TeamComments
                contactPerson={contactPerson}
                initFocus={!isTerminologyProject}
                teamComments={teamComments}
                user={user}
                togglePinnedStatus={togglePinnedStatus}
                resetContactPerson={resetContactPerson}
              />
            </TabPanel>
          </Tabs>
        </div>
      </>
    );
  }

  return (
    <>
      <div className='top' data-testid='helpers'>
        <Tabs
          selectedIndex={commentTabIndex}
          onSelect={(tab) => setCommentTabIndex(tab)}
        >
          <TabList>
            {isTerminologyProject ? null : (
              <Tab>
                <TermsTab />
              </Tab>
            )}
            <Tab ref={commentTabRef}>
              <CommentsTab />
            </Tab>
          </TabList>
          {isTerminologyProject ? null : (
            <TabPanel>
              <TermsPanel />
            </TabPanel>
          )}
          <TabPanel>
            {/* HACK: Required inline due to https://github.com/mozilla/pontoon/issues/2300 */}
            <TeamComments
              contactPerson={contactPerson}
              initFocus={!isTerminologyProject}
              teamComments={teamComments}
              user={user}
              togglePinnedStatus={togglePinnedStatus}
              resetContactPerson={resetContactPerson}
            />
          </TabPanel>
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
            <Tab>
              <MachineryTab />
            </Tab>
            <Tab>
              <OtherLocalesTab />
            </Tab>
          </TabList>
          <TabPanel>
            <MachineryPanel />
          </TabPanel>
          <TabPanel>
            <OtherLocalesPanel />
          </TabPanel>
        </Tabs>
      </div>
    </>
  );
}
