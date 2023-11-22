import { createContext, useState } from 'react';

type EntitiesList = Readonly<{
  visible: boolean;
  show(visible: boolean): void;
}>;

const initEntitiesList: EntitiesList = {
  visible: false,
  show: () => {},
};

export const EntitiesList = createContext(initEntitiesList);

export function EntitiesListProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const [state, setState] = useState(() => ({
    ...initEntitiesList,
    show: (visible: boolean) => setState((prev) => ({ ...prev, visible })),
  })) as [EntitiesList, React.Dispatch<React.SetStateAction<EntitiesList>>];
  return (
    <EntitiesList.Provider value={state}>{children}</EntitiesList.Provider>
  );
}
