import { Localized } from '@fluent/react';
import React, { useCallback, useState } from 'react';

import { useOnDiscard } from '~/utils';

import './SearchPanel.css';

type SearchPanelProps = {
    onDiscard: () => void;
};

export function SearchPanelDialog({
    onDiscard,
}: SearchPanelProps): React.ReactElement<'div'> {
    const ref = React.useRef(null);
    useOnDiscard(ref, onDiscard);

    return (
        <div className='menu' ref={ref}>
            <ul>
                <li className='title'>SEARCH OPTIONS</li>
                <li className='check-box'>
                    <i className='fa fa-fw'></i>
                    <span className='label'>Search message identifiers</span>
                </li>
                <li className='check-box enabled'>
                    <i className='fa fa-fw'></i>
                    <span className='label'>Demonstrate checked state</span>
                </li>
            </ul>
        </div>
    );
}

export function SearchPanel(): React.ReactElement<'div'> | null {
    const [visible, setVisible] = useState(false);

    const toggleVisible = useCallback(() => {
        setVisible((prev) => !prev);
    }, []);

    const handleDiscard = useCallback(() => {
        setVisible(false);
    }, []);

    return (
        <div className='search-panel'>
            <div className='visibility-switch' onClick={toggleVisible}>
                <span className='fa fa-search'></span>
            </div>
            {visible ? <SearchPanelDialog onDiscard={handleDiscard} /> : null}
        </div>
    );
}