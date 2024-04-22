import React, {
  createContext,
  useContext,
  useState,
  Dispatch,
  SetStateAction,
} from 'react';
import { fetchGPTTransform } from '~/api/machinery';

interface LLMTranslationContextType {
  llmTranslation: string;
  setLlmTranslation: Dispatch<SetStateAction<string>>;

  selectedOption: string;
  setSelectedOption: Dispatch<SetStateAction<string>>;
  transformLLMTranslation: (
    original: string,
    current: string,
    characteristic: string,
    localeName: string,
  ) => Promise<void>;
}

const LLMTranslationContext = createContext<LLMTranslationContextType>({
  llmTranslation: '',
  setLlmTranslation: () => {},

  selectedOption: '',
  setSelectedOption: () => {},
  transformLLMTranslation: async () => {},
});

export const LLMTranslationProvider: React.FC = ({ children }) => {
  const [llmTranslation, setLlmTranslation] = useState<string>('');

  const [selectedOption, setSelectedOption] = useState<string>('');

  const handleSetSelectedOption = (option: string) => {
    let displayText = '';

    switch (option) {
      case 'alternative':
        displayText = 'REPHRASED';
        break;
      case 'formal':
        displayText = 'FORMAL';
        break;
      case 'informal':
        displayText = 'INFORMAL';
        break;
      case 'original':
        displayText = '';
        break;
    }

    setSelectedOption(displayText);
  };

  const transformLLMTranslation = async (
    original: string,
    current: string,
    characteristic: string,
    localeName: string,
  ) => {
    if (characteristic !== 'original') {
      const machineryTranslations = await fetchGPTTransform(
        original,
        current,
        characteristic,
        localeName,
      );
      if (machineryTranslations.length > 0) {
        setLlmTranslation(machineryTranslations[0].translation);
        handleSetSelectedOption(characteristic);
      }
    } else {
      setLlmTranslation('');
      handleSetSelectedOption('');
    }
  };

  return (
    <LLMTranslationContext.Provider
      value={{
        llmTranslation,
        setLlmTranslation,
        selectedOption,
        setSelectedOption,
        transformLLMTranslation,
      }}
    >
      {children}
    </LLMTranslationContext.Provider>
  );
};

export const useLLMTranslation = () => useContext(LLMTranslationContext);
