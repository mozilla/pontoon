import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
} from 'react';
import { type MachineryTranslation, fetchGPTTransform } from '~/api/machinery';

type SelState = {
  loading: boolean;
  selectedOption: string;
  llmTranslation: string;
};

interface LLMTranslationContextType {
  getSelState(mt: MachineryTranslation): SelState;
  transformLLMTranslation: (
    mt: MachineryTranslation,
    characteristic: string,
    localeName: string,
  ) => Promise<void>;
}

const initSelState = () => ({
  loading: false,
  selectedOption: '',
  llmTranslation: '',
});

const LLMTranslationContext = createContext<LLMTranslationContextType>({
  getSelState: initSelState,
  transformLLMTranslation: async () => {},
});

export const LLMTranslationProvider: React.FC = ({ children }) => {
  const stateRef = useRef(new WeakMap<MachineryTranslation, SelState>());
  const [version, setVersion] = useState(0); // Counter to trigger re-renders

  const getSelState = useCallback(
    (mt: MachineryTranslation): SelState => {
      return stateRef.current.get(mt) ?? initSelState();
    },
    [version],
  );

  const transformLLMTranslation = async (
    mt: MachineryTranslation,
    characteristic: string,
    localeName: string,
  ) => {
    const currentState = getSelState(mt);
    stateRef.current.set(mt, {
      ...currentState,
      loading: true,
      selectedOption: currentState.selectedOption,
      llmTranslation: currentState.llmTranslation,
    });
    setVersion((v) => v + 1); // Trigger re-render

    const machineryTranslations = await fetchGPTTransform(
      mt.original,
      mt.translation,
      characteristic,
      localeName,
    );
    if (machineryTranslations.length > 0) {
      stateRef.current.set(mt, {
        loading: false,
        selectedOption: characteristic,
        llmTranslation: machineryTranslations[0].translation,
      });
    } else {
      stateRef.current.set(mt, {
        ...currentState,
        loading: false,
      });
    }
    setVersion((v) => v + 1);
  };

  return (
    <LLMTranslationContext.Provider
      value={{ getSelState, transformLLMTranslation }}
    >
      {children}
    </LLMTranslationContext.Provider>
  );
};

export const useLLMTranslation = (mt: MachineryTranslation) => {
  const { getSelState, transformLLMTranslation } = useContext(
    LLMTranslationContext,
  );
  return { ...getSelState(mt), transformLLMTranslation };
};
