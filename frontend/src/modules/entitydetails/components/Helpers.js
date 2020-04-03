/* @flow */

import * as React from 'react';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import { Localized } from '@fluent/react';

import './Helpers.css';

import { TeamComments, CommentCount } from 'modules/teamcomments';
import { Terms, TermCount } from 'modules/terms';
import { Machinery, MachineryCount } from 'modules/machinery';
import { OtherLocales, OtherLocalesCount } from 'modules/otherlocales';

import type { Entity } from 'core/api';
import type { TermState } from 'core/term';
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
    terms: TermState,
    parameters: NavigationParams,
    user: UserState,
    updateEditorTranslation: (string, string) => void,
    searchMachinery: (string) => void,
    addComment: (string, ?number) => void,
    addTextToEditorTranslation: (string) => void,
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
            terms,
            parameters,
            user,
            updateEditorTranslation,
            searchMachinery,
            addComment,
            addTextToEditorTranslation,
        } = this.props;

        return <>
            <div className="top">
                <Tabs>
                    <TabList>
                        <Tab>
                            <Localized id='entitydetails-Helpers--terms'>
                                { 'Terms' }
                            </Localized>
                            <TermCount terms={ terms }/>
                        </Tab>
                        <Tab>
                            <Localized id='entitydetails-Helpers--comments'>
                                { 'Comments' }
                            </Localized>
                            <CommentCount teamComments={ teamComments }/>
                        </Tab>
                    </TabList>
                    <TabPanel>
                        <Terms
                            isReadOnlyEditor={ isReadOnlyEditor }
                            terms={ terms }
                            addTextToEditorTranslation={ addTextToEditorTranslation }
                        />
                    </TabPanel>
                    <TabPanel>
                        <TeamComments
                            teamComments={ teamComments }
                            user={ user }
                            addComment={ addComment }
                        />
                    </TabPanel>
                </Tabs>
            </div>
            <div className="bottom">
                <Tabs>
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
                </Tabs>
            </div>
        </>;
    }
}
