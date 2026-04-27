const BASE = '/api'

export async function recognize(
  file: File,
): Promise<{ names: string[]; confidences: number[] }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/recognize`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
