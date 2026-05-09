import { recognize } from '../../infrastructure/api/recognitionApi'

export interface RecognizedParties {
  opponentParty: string[]
  myParty: string[]
}

export interface UseRecognitionReturn {
  recognizeImage: (file: File) => Promise<RecognizedParties>
}

export function useRecognition(): UseRecognitionReturn {
  const recognizeImage = async (file: File): Promise<RecognizedParties> => {
    const result = await recognize(file)
    return {
      opponentParty: result.opponent_party.names.slice(0, 6),
      myParty: result.my_party.names.slice(0, 6),
    }
  }

  return { recognizeImage }
}
