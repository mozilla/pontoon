import * as React from 'react';

type Props = {
    readonly title: string;
    readonly className: string;
    readonly children: React.ReactNode;
};

/**
 * Component to dislay a property of an entity in the Metadata component.
 */
export default function Property(props: Props): React.ReactElement<'div'> {
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
