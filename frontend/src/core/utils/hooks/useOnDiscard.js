/* @flow */
import * as React from 'react';

export default function useOnDiscard(
    ref: { current: null | React.ElementRef<any> },
    onDiscard: (e: MouseEvent) => void,
) {
    const handleClick = React.useCallback(
        (e: MouseEvent) => {
            const el = ref.current;
            if (!el || el.contains(e.target)) {
                return;
            }

            onDiscard(e);
        },
        [ref, onDiscard],
    );

    React.useEffect(() => {
        window.document.addEventListener('click', handleClick);
        return () => {
            window.document.removeEventListener('click', handleClick);
        };
    }, [handleClick]);
}
