import { useEffect, useState } from 'react';

const NARROW_SCREEN_MAX_WIDTH = 600;

/**
 * Return true if the screen is narrower than 600px. Useful in Responsive Web Design.
 */
export function useNarrowScreen(): boolean {
  const [isNarrow, setIsNarrow] = useState(
    window.innerWidth <= NARROW_SCREEN_MAX_WIDTH,
  );

  useEffect(() => {
    const handleWindowResize = () =>
      setIsNarrow(window.innerWidth <= NARROW_SCREEN_MAX_WIDTH);
    window.addEventListener('resize', handleWindowResize);
    return () => window.removeEventListener('resize', handleWindowResize);
  }, []);

  return isNarrow;
}
