import * as React from 'react';

export default function useOnDiscard(
    ref: { current: null | React.ElementRef<any> },
    onDiscard: (e: React.SyntheticEvent<any>) => void,
) {
    const handleClick = React.useCallback(
        (e: React.SyntheticEvent<any>) => {
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
