
import React from 'react';

import DOMPurify from 'dompurify';


export class SanitizedHTML extends React.PureComponent {

    get HTML () {
        return {__html: DOMPurify.sanitize(this.props.html)};
    }

    render () {
        return <div className={this.props.className} dangerouslySetInnerHTML={this.HTML} />
    }
}
