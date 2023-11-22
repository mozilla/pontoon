import { createContext, useState } from 'react';

type EntitiesList = Readonly<{
  visible: boolean;
  toggleEntitiesList(): void;
}>;

const initEntitiesList: EntitiesList = {
  visible: false,
  toggleEntitiesList: () => {},
};

export const EntitiesList = createContext(initEntitiesList);

export function EntitiesListProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const [state, setState] = useState(() => ({
    ...initEntitiesList,
    toggleEntitiesList: () =>
      setState((prev) => ({ ...prev, visible: !prev.visible })),
  }));

  return (
    <EntitiesList.Provider value={state}>{children}</EntitiesList.Provider>
  );
}
