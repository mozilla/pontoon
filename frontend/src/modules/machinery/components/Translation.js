/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './Translation.css';

import api from 'core/api';

import type { Locale } from 'core/locales';


type Props = {|
    locale: Locale,
    translation: api.types.MachineryTranslation,
|};


/**
 *
 */
 export default class Translation extends React.Component<Props> {
     render() {
         const { translation, locale } = this.props;

         return <Localized id="machinery-translation-copy" attrs={{ title: true }}>
             <li className="translation" title="Copy Into Translation (Tab)">
                 <header>
                     { !translation.quality ? null :
                     <span className="stress">{ translation.quality }</span>
                     }
                     <ul className="sources">
                         <li>
                             <a
                                className="translation-source"
                                href={ translation.url }
                                title={ translation.title }
                                target="_blank"
                                rel="noopener noreferrer"
                             >
                                 <span>{ translation.source }</span>
                                 { !translation.count ? null :
                                 <Localized id="machinery-translation-number-occurrences" attrs={{ title: true }}>
                                     <sup title="Number of translation occurrences">
                                        { translation.count }
                                    </sup>
                                </Localized>
                                 }
                             </a>
                         </li>
                     </ul>
                 </header>
                 <p className="original">
                     { translation.original }
                 </p>
                 <p
                    className="suggestion"
                    dir={ locale.direction }
                    data-script={ locale.script }
                    lang={ locale.code }
                 >
                     { translation.translation }
                 </p>
             </li>
         </Localized>;
     }
 }
