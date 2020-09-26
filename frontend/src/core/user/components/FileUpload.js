/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './FileUpload.css';

import type { NavigationParams } from 'core/navigation';

type Props = {|
    parameters: NavigationParams,
|};

/*
 * Render a File Upload button.
 */
export default class FileUpload extends React.Component<Props> {
    uploadForm: { current: ?HTMLFormElement };

    constructor(props: Props) {
        super(props);
        this.uploadForm = React.createRef();
    }

    submitForm = () => {
        const form = this.uploadForm.current;
        if (form) {
            form.submit();
        }
    };

    render() {
        const { parameters } = this.props;

        /* TODO: Refactor core.api.base and reuse getCSRFToken() here */
        let csrfToken = '';
        const rootElt = document.getElementById('root');
        if (rootElt) {
            csrfToken = rootElt.dataset.csrfToken;
        }

        return (
            <form
                action='/upload/'
                className='file-upload'
                encType='multipart/form-data'
                method='POST'
                ref={this.uploadForm}
            >
                <input
                    name='csrfmiddlewaretoken'
                    type='hidden'
                    value={csrfToken}
                />
                <input name='code' type='hidden' value={parameters.locale} />
                <input name='slug' type='hidden' value={parameters.project} />
                <input name='part' type='hidden' value={parameters.resource} />
                <label>
                    <Localized
                        id='user-UserMenu--upload-translations'
                        elems={{
                            glyph: (
                                <i className='fa fa-cloud-upload-alt fa-fw' />
                            ),
                        }}
                    >
                        <span>{'<glyph></glyph>Upload Translations'}</span>
                    </Localized>
                    <input
                        name='uploadfile'
                        type='file'
                        onChange={this.submitForm}
                    />
                </label>
            </form>
        );
    }
}
