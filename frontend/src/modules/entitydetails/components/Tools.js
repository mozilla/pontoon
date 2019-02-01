/* @flow */

import * as React from 'react';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';

import './Tools.css';

import { History } from 'modules/history';
import { Machinery } from 'modules/machinery';
import { Locales } from 'modules/otherlocales';

import MachineryCount from './MachineryCount';

import type { NavigationParams } from 'core/navigation';
import type { HistoryState } from 'modules/history';
import type { MachineryState } from 'modules/machinery';
import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    history: HistoryState,
    machinery: MachineryState,
    otherlocales: LocalesState,
    parameters: NavigationParams,
|};


/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export default class Tools extends React.Component<Props> {
    render() {
        const { history, machinery, otherlocales, parameters } = this.props;

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
                <History />
            </TabPanel>
            <TabPanel>
                <Machinery />
            </TabPanel>
            <TabPanel>
                <Locales otherlocales={ otherlocales } parameters={ parameters } />
            </TabPanel>
        </Tabs>;
    }
}
