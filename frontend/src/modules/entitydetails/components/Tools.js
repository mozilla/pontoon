/* @flow */

import * as React from 'react';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';

import './Tools.css';

import { History } from 'modules/history';
import { Machinery } from 'modules/machinery';
import { Locales } from 'modules/otherlocales';

import type { HistoryState } from 'modules/history';
import type { MachineryState } from 'modules/machinery';


type Props = {|
    history: HistoryState,
    machinery: MachineryState,
    otherlocales: Object,
    parameters: Object,
|};


type CountProps = {|
    machinery: MachineryState,
|};


class MachineryCount extends React.Component<CountProps> {
    render() {
        const { machinery } = this.props;

        const machineryCount = machinery.translations.length;

        const preferredCount = machinery.translations.reduce((count, item) => {
            if (item.sources.find(source => source.type === 'Translation memory')) {
                return count + 1;
            }
            return count;
        }, 0);

        const remainingCount = machineryCount - preferredCount;

        const preferred = (
            !preferredCount ? null :
            <span className='preferred'>{ preferredCount }</span>
        );
        const remaining = (
            !remainingCount ? null :
            <span>{ remainingCount }</span>
        );
        const plus = (
            !remainingCount || !preferredCount ? null :
            <span>{ '+' }</span>
        );

        return <span className='count'>
            { preferred }
            { plus }
            { remaining }
        </span>;
    }
};


/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export default class Tools extends React.Component<Props> {
    render() {
        const { history, machinery, otherlocales, parameters } = this.props;

        const historyCount = history.translations.length;
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
                    <MachineryCount machinery={ machinery } />
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
