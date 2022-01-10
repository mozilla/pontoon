import {
    TypedUseSelectorHook,
    useDispatch,
    useSelector,
    useStore,
} from 'react-redux';
import type { RootState, AppDispatch } from './store';

// Use throughout your app instead of plain `useDispatch` and `useSelector`
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
export const useAppStore = () => useStore<RootState>();
export type AppStore = ReturnType<typeof useAppStore>;
