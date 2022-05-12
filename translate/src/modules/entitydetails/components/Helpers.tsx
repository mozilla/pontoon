import { Localized } from '@fluent/react';
import React from 'react';
import { Tab, TabList, TabPanel, Tabs } from 'react-tabs';

import type { Entity } from '~/api/entity';
import type { LocationType } from '~/context/location';
import * as editor from '~/core/editor';
import type { TermState } from '~/core/term';
import type { UserState } from '~/core/user';
import { useAppDispatch } from '~/hooks';
import type { MachineryState } from '~/modules/machinery';
import { Machinery, MachineryCount } from '~/modules/machinery';
import type { LocalesState } from '~/modules/otherlocales';
import { OtherLocales, OtherLocalesCount } from '~/modules/otherlocales';
import type { TeamCommentState } from '~/modules/teamcomments';
import { CommentCount, TeamComments } from '~/modules/teamcomments';
import { TermCount, Terms } from '~/modules/terms';

import './Helpers.css';

type Props = {
  entity: Entity;
  isReadOnlyEditor: boolean;
  machinery: MachineryState;
  otherlocales: LocalesState;
  teamComments: TeamCommentState;
  terms: TermState;
  parameters: LocationType;
  user: UserState;
  commentTabRef: any; // Used to access <Tab> _reactInternalFiber
  commentTabIndex: number;
  contactPerson: string;
  searchMachinery: (source: string) => void;
  addComment: (comment: string, id: number | null | undefined) => void;
  togglePinnedStatus: (status: boolean, id: number) => void;
  addTextToEditorTranslation: (text: string) => void;
  navigateToPath: (path: string) => void;
  setCommentTabIndex: (index: number) => void;
  resetContactPerson: () => void;
};

/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export default function Helpers(props: Props): React.ReactElement<any> {
  const {
    entity,
    isReadOnlyEditor,
    machinery,
    otherlocales,
    teamComments,
    terms,
    parameters,
    user,
    commentTabRef,
    commentTabIndex,
    contactPerson,
    searchMachinery,
    addComment,
    togglePinnedStatus,
    addTextToEditorTranslation,
    navigateToPath,
    setCommentTabIndex,
    resetContactPerson,
  } = props;
  const dispatch = useAppDispatch();

  return (
    <>
      <div className='top'>
        <Tabs
          selectedIndex={commentTabIndex}
          onSelect={(tab) => setCommentTabIndex(tab)}
        >
          <TabList>
            {parameters.project === 'terminology' ? null : (
              <Tab>
                <Localized id='entitydetails-Helpers--terms'>
                  {'TERMS'}
                </Localized>
                <TermCount terms={terms} />
              </Tab>
            )}
            <Tab ref={commentTabRef}>
              <Localized id='entitydetails-Helpers--comments'>
                {'COMMENTS'}
              </Localized>
              <CommentCount teamComments={teamComments} />
            </Tab>
          </TabList>
          {parameters.project === 'terminology' ? null : (
            <TabPanel>
              <Terms
                isReadOnlyEditor={isReadOnlyEditor}
                terms={terms}
                addTextToEditorTranslation={addTextToEditorTranslation}
                navigateToPath={navigateToPath}
              />
            </TabPanel>
          )}
          <TabPanel>
            <TeamComments
              parameters={parameters}
              teamComments={teamComments}
              user={user}
              addComment={addComment}
              togglePinnedStatus={togglePinnedStatus}
              contactPerson={contactPerson}
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
            }
            dispatch(editor.actions.selectHelperTabIndex(index));
            dispatch(editor.actions.resetHelperElementIndex());
          }}
        >
          <TabList>
            <Tab>
              <Localized id='entitydetails-Helpers--machinery'>
                {'MACHINERY'}
              </Localized>
              <MachineryCount machinery={machinery} />
            </Tab>
            <Tab>
              <Localized id='entitydetails-Helpers--locales'>
                {'LOCALES'}
              </Localized>
              <OtherLocalesCount otherlocales={otherlocales} />
            </Tab>
          </TabList>
          <TabPanel>
            <Machinery
              machinery={machinery}
              searchMachinery={searchMachinery}
            />
          </TabPanel>
          <TabPanel>
            <OtherLocales
              entity={entity}
              otherlocales={otherlocales}
              parameters={parameters}
            />
          </TabPanel>
        </Tabs>
      </div>
    </>
  );
}
