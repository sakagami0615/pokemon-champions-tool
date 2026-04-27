import { recognize } from '../../infrastructure/api/recognitionApi'

export interface UseRecognitionReturn {
  recognizeImage: (file: File) => Promise<string[]>
}

export function useRecognition(): UseRecognitionReturn {
  const recognizeImage = async (file: File): Promise<string[]> => {
    const result = await recognize(file)
    return result.names.slice(0, 6)
  }

  return { recognizeImage }
}
