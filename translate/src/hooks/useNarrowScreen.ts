import { useEffect, useState } from 'react';

/**
 * Return true if the screen is narrower than 600 px. Useful in Responsive Web Design.
 */
export function useNarrowScreen(): boolean {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleWindowResize = () => setWidth(window.innerWidth);
    window.addEventListener('resize', handleWindowResize);
    return () => window.removeEventListener('resize', handleWindowResize);
  }, []);

  return width <= 600;
}
