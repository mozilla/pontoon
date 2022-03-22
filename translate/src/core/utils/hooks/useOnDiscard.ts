import { useEffect } from 'react';

export default function useOnDiscard(
  ref: React.RefObject<unknown>,
  onDiscard: () => void,
) {
  useEffect(() => {
    const handleClick = (ev: MouseEvent) => {
      const el = ref.current;
      if (
        el instanceof HTMLElement &&
        ev.target instanceof Element &&
        !el.contains(ev.target)
      ) {
        onDiscard();
      }
    };
    window.document.addEventListener('click', handleClick);
    return () => window.document.removeEventListener('click', handleClick);
  }, [ref, onDiscard]);
}
