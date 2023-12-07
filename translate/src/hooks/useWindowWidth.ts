import { useEffect, useState } from 'react';

const MAX_WIDTH = {
  narrow: 600,
  medium: 800,
};

/**
 * Return true if the screen is narrower than the given width.
 *
 * Useful in Responsive Web Design.
 */
export function useWindowWidth(width: 'narrow' | 'medium'): boolean {
  const [isWindowWidth, setIsWindowWidth] = useState(
    window.innerWidth <= MAX_WIDTH[width],
  );

  useEffect(() => {
    const handleWindowResize = () =>
      setIsWindowWidth(window.innerWidth <= MAX_WIDTH[width]);
    window.addEventListener('resize', handleWindowResize);
    return () => window.removeEventListener('resize', handleWindowResize);
  }, []);

  return isWindowWidth;
}
