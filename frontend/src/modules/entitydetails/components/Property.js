/* @flow */

import * as React from 'react';

type Props = {|
    +title: string,
    +className: string,
    +children: React.Node,
|};

/**
 * Component to dislay a property of an entity in the Metadata component.
 */
export default function Property(props: Props) {
    const { children, className, title } = props;

    return (
        <div className={className}>
            <span className='title'>{title}</span>
            {/* Extra space between <span> elements prevents cross
                element selection on double click (bug 1228873) */}{' '}
            <span className='content'>{children}</span>
        </div>
    );
}
