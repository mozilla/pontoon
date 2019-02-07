/* @flow */

import * as React from 'react';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';

import './Tools.css';

import { History } from 'modules/history';
import { Machinery } from 'modules/machinery';
import { Locales } from 'modules/otherlocales';

import MachineryCount from './MachineryCount';

import type { Locale } from 'core/locales';
import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import type { HistoryState } from 'modules/history';
import type { MachineryState } from 'modules/machinery';
import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    history: HistoryState,
    locale: Locale,
    machinery: MachineryState,
    otherlocales: LocalesState,
    parameters: NavigationParams,
    user: UserState,
    deleteTranslation: (number) => void,
    updateEditorTranslation: (string) => void,
    updateTranslationStatus: (number, string) => void,
|};


/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export default class Tools extends React.Component<Props> {
    render() {
        const {
            history,
            locale,
            machinery,
            otherlocales,
            parameters,
            user,
            deleteTranslation,
            updateEditorTranslation,
            updateTranslationStatus,
        } = this.props;

        const historyCount = history.translations.length;
        const machineryCount = machinery.translations.length;
        const otherlocalesCount = otherlocales.translations.length;

        return <Tabs>
            <TabList>
                <Tab>
                    History
                    { !historyCount ? null :
                    <span className={ 'count' }>{ historyCount }</span>
                    }
                </Tab>
                <Tab>
                    Machinery
                    { !machineryCount ? null :
                    <MachineryCount machinery={ machinery } />
                    }
                </Tab>
                <Tab>
                    Locales
                    { !otherlocalesCount ? null :
                    <span className={ 'count' }>{ otherlocalesCount }</span>
                    }
                </Tab>
            </TabList>

            <TabPanel>
                <History
                    history={ history }
                    locale={ locale }
                    parameters={ parameters }
                    user={ user }
                    deleteTranslation={ deleteTranslation }
                    updateTranslationStatus={ updateTranslationStatus }
                    updateEditorTranslation={ updateEditorTranslation }
                />
            </TabPanel>
            <TabPanel>
                <Machinery
                    machinery={ machinery }
                    locale={ locale }
                    updateEditorTranslation={ updateEditorTranslation }
                />
            </TabPanel>
            <TabPanel>
                <Locales
                    otherlocales={ otherlocales }
                    parameters={ parameters }
                    updateEditorTranslation={ updateEditorTranslation }
                />
            </TabPanel>
        </Tabs>;
    }
}
