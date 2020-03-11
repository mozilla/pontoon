/* @flow */

import * as React from 'react';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import { Localized } from '@fluent/react';

import './Helpers.css';

import { TeamComments, CommentCount } from 'modules/teamcomments';
import { Machinery, MachineryCount } from 'modules/machinery';
import { OtherLocales, OtherLocalesCount } from 'modules/otherlocales';

import type { Entity } from 'core/api';
import type { TeamCommentState } from 'modules/teamcomments';
import type { Locale } from 'core/locale';
import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import type { MachineryState } from 'modules/machinery';
import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    entity: Entity,
    isReadOnlyEditor: boolean,
    locale: Locale,
    machinery: MachineryState,
    otherlocales: LocalesState,
    teamComments: TeamCommentState,
    parameters: NavigationParams,
    user: UserState,
    updateEditorTranslation: (string, string) => void,
    searchMachinery: (string) => void,
    addComment: (string, ?number) => void,
|};


/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export default class Helpers extends React.Component<Props> {
    render() {
        const {
            entity,
            isReadOnlyEditor,
            locale,
            machinery,
            otherlocales,
            teamComments,
            parameters,
            user,
            updateEditorTranslation,
            searchMachinery,
            addComment,
        } = this.props;

        return <Tabs>
            <TabList>
                <Tab>
                    <Localized id='entitydetails-Helpers--machinery'>
                        { 'Machinery' }
                    </Localized>
                    <MachineryCount machinery={ machinery } />
                </Tab>
                <Tab>
                    <Localized id='entitydetails-Helpers--locales'>
                        { 'Locales' }
                    </Localized>
                    <OtherLocalesCount otherlocales={ otherlocales } />
                </Tab>
                <Tab>
                    <Localized id='entitydetails-Helpers--comments'>
                        { 'Comments' }
                    </Localized>
                    <CommentCount teamComments={ teamComments }/>
                </Tab>
            </TabList>

            <TabPanel>
                <Machinery
                    isReadOnlyEditor={ isReadOnlyEditor }
                    locale={ locale }
                    machinery={ machinery }
                    updateEditorTranslation={ updateEditorTranslation }
                    searchMachinery={ searchMachinery }
                />
            </TabPanel>
            <TabPanel>
                <OtherLocales
                    entity={ entity }
                    isReadOnlyEditor={ isReadOnlyEditor }
                    otherlocales={ otherlocales }
                    user={ user }
                    parameters={ parameters }
                    updateEditorTranslation={ updateEditorTranslation }
                />
            </TabPanel>
            <TabPanel>
                <TeamComments
                    teamComments={ teamComments }
                    user={ user }
                    addComment={ addComment }
                />
            </TabPanel>
        </Tabs>;
    }
}
