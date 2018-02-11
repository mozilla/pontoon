
import React from 'react';


export default class LatestActivityTooltipTranslation extends React.PureComponent {

    render () {
        return (
            <span>
              <span className="quote fa fa-2x fa-quote-right"></span>
              <p className="translation">{this.props.translation}</p>
            </span>);
    }
}
