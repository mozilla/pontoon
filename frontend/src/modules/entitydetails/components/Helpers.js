/* @flow */

import * as React from 'react';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import { Localized } from 'fluent-react';

import './Helpers.css';

import { History } from 'modules/history';
import { Machinery, MachineryCount } from 'modules/machinery';
import { OtherLocales, OtherLocalesCount } from 'modules/otherlocales';

import type { Entity, OtherLocaleTranslation } from 'core/api';
import type { Locale } from 'core/locales';
import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import type { ChangeOperation, HistoryState } from 'modules/history';
import type { MachineryState } from 'modules/machinery';
import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    entity: Entity,
    history: HistoryState,
    isReadOnlyEditor: boolean,
    isTranslator: boolean,
    locale: Locale,
    machinery: MachineryState,
    otherlocales: LocalesState,
    orderedOtherLocales: Array<OtherLocaleTranslation>,
    preferredLocalesCount: number,
    parameters: NavigationParams,
    user: UserState,
    deleteTranslation: (number) => void,
    updateEditorTranslation: (string) => void,
    updateTranslationStatus: (number, ChangeOperation) => void,
    searchMachinery: (string) => void,
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
            history,
            isReadOnlyEditor,
            isTranslator,
            locale,
            machinery,
            otherlocales,
            orderedOtherLocales,
            preferredLocalesCount,
            parameters,
            user,
            deleteTranslation,
            updateEditorTranslation,
            updateTranslationStatus,
            searchMachinery,
        } = this.props;

        const historyCount = history.translations.length;
        const machineryCount = machinery.translations.length;
        const otherlocalesCount = otherlocales.translations.length;

        return <Tabs>
            <TabList>
                <Tab>
                    <Localized id='entitydetails-Helpers--history'>
                        { 'History' }
                    </Localized>
                    { !historyCount ? null :
                    <span className={ 'count' }>{ historyCount }</span>
                    }
                </Tab>
                <Tab>
                    <Localized id='entitydetails-Helpers--machinery'>
                        { 'Machinery' }
                    </Localized>
                    { !machineryCount ? null :
                    <MachineryCount machinery={ machinery } />
                    }
                </Tab>
                <Tab>
                    <Localized id='entitydetails-Helpers--locales'>
                        { 'Locales' }
                    </Localized>
                    { !otherlocalesCount ? null :
                    <OtherLocalesCount
                        otherlocales={ otherlocales }
                        preferredLocalesCount={ preferredLocalesCount }
                    />
                    }
                </Tab>
            </TabList>

            <TabPanel>
                <History
                    entity={ entity }
                    history={ history }
                    isReadOnlyEditor={ isReadOnlyEditor }
                    isTranslator={ isTranslator }
                    locale={ locale }
                    user={ user }
                    deleteTranslation={ deleteTranslation }
                    updateTranslationStatus={ updateTranslationStatus }
                    updateEditorTranslation={ updateEditorTranslation }
                />
            </TabPanel>
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
                    orderedOtherLocales= { orderedOtherLocales }
                    preferredLocalesCount={ preferredLocalesCount }
                    user={ user }
                    parameters={ parameters }
                    updateEditorTranslation={ updateEditorTranslation }
                />
            </TabPanel>
        </Tabs>;
    }
}
