import { useEffect, useState } from 'react';

/**
 * Return true if the screen is narrower than MAX_WIDTH. Useful in Responsive Web Design.
 */
export function isNarrowerThan(MAX_WIDTH: number): boolean {
  const [isNarrower, setIsNarrower] = useState(window.innerWidth <= MAX_WIDTH);

  useEffect(() => {
    const handleWindowResize = () =>
      setIsNarrower(window.innerWidth <= MAX_WIDTH);
    window.addEventListener('resize', handleWindowResize);
    return () => window.removeEventListener('resize', handleWindowResize);
  }, []);

  return isNarrower;
}
