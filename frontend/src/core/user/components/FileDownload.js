/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import type { NavigationParams } from 'core/navigation';


type Props = {|
    parameters: NavigationParams,
|};


/*
 * Render a Sign Out link.
 */
export default class SignOut extends React.Component<Props> {
    downloadTranslations = () => {
        document.getElementById('download-form').submit();
    }

    render() {
        const { parameters } = this.props;

        let csrfToken = '';
        const rootElt = document.getElementById('root');
        if (rootElt) {
            csrfToken = rootElt.dataset.csrfToken;
        }

        return <React.Fragment>
            <Localized
                id="user-UserMenu--download-translations"
                glyph={
                    <i className="fa fa-cloud-download-alt fa-fw"></i>
                }
            >
                <button onClick={ this.downloadTranslations }>
                    { '<glyph></glyph>Download Translations' }
                </button>
            </Localized>

            <form
                id="download-form"
                action="/download/"
                className="hidden"
                method="POST"
            >
                <input name="csrfmiddlewaretoken" type="hidden" value={ csrfToken } />
                <input name="code" type="hidden" value={ parameters.locale } />
                <input name="slug" type="hidden" value={ parameters.project } />
                <input name="part" type="hidden" value={ parameters.resource } />
            </form>
        </React.Fragment>;
    }
}
