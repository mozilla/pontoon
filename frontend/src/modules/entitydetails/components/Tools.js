/* @flow */

import * as React from 'react';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';

import './Tools.css';

import { History } from 'modules/history';
import { Locales } from 'modules/otherlocales';


type Props = {|
    historyCount: number,
    localesCount: number,
|};


/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export default class Tools extends React.Component<Props> {
    render() {
        const { historyCount, localesCount } = this.props;

        return <Tabs>
            <TabList>
                <Tab>
                    History
                    <span className={ 'count' }>{ historyCount }</span>
                </Tab>
                <Tab>
                    Locales
                    <span className={ 'count' }>{ localesCount }</span>
                </Tab>
            </TabList>

            <TabPanel>
                <History />
            </TabPanel>
            <TabPanel>
                <Locales />
            </TabPanel>
        </Tabs>;
    }
}
