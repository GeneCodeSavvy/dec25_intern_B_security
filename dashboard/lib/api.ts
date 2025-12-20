const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

// Cache configuration
const EMAILS_CACHE_KEY = "mailshield_emails_cache"
const CACHE_EXPIRY_MS = 5 * 60 * 1000 // 5 minutes

type CacheEntry<T> = {
  data: T
  timestamp: number
}

type FetchOptions = {
  token?: string
  headers?: Record<string, string>
  method?: "GET" | "POST" | "PUT" | "DELETE"
  body?: unknown
}

async function request<T>(path: string, { token, headers, method = "GET", body }: FetchOptions = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
    cache: "no-store",
  })

  if (!res.ok) {
    let errorMessage = `API request failed (${res.status})`
    if (process.env.NODE_ENV === "development") {
      try {
        const body = await res.text()
        errorMessage += `: ${body}`
      } catch {
        // Ignore parsing errors
      }
    }
    throw new Error(errorMessage)
  }

  return res.json() as Promise<T>
}

// Cache utilities
function getCachedEmails(): Email[] | null {
  if (typeof window === "undefined") return null
  
  try {
    const cached = localStorage.getItem(EMAILS_CACHE_KEY)
    if (!cached) return null
    
    const entry: CacheEntry<Email[]> = JSON.parse(cached)
    const isExpired = Date.now() - entry.timestamp > CACHE_EXPIRY_MS
    
    if (isExpired) {
      localStorage.removeItem(EMAILS_CACHE_KEY)
      return null
    }
    
    return entry.data
  } catch {
    return null
  }
}

function setCachedEmails(emails: Email[]): void {
  if (typeof window === "undefined") return
  
  try {
    const entry: CacheEntry<Email[]> = {
      data: emails,
      timestamp: Date.now(),
    }
    localStorage.setItem(EMAILS_CACHE_KEY, JSON.stringify(entry))
  } catch {
    // Ignore storage errors (quota exceeded, etc.)
  }
}

export function clearEmailsCache(): void {
  if (typeof window === "undefined") return
  localStorage.removeItem(EMAILS_CACHE_KEY)
}

export type Email = {
  id: string
  sender: string
  recipient: string
  subject: string
  body_preview?: string
  received_at?: string
  
  // Threat Intelligence
  threat_category?: "NONE" | "PHISHING" | "MALWARE" | "SPAM" | "BEC" | "SPOOFING" | "SUSPICIOUS"
  detection_reason?: string
  
  // Security Metadata
  spf_status?: string
  dkim_status?: string
  dmarc_status?: string
  sender_ip?: string
  attachment_info?: string
  
  // Processing
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED" | "SPAM"
  risk_score?: number
  risk_tier?: "SAFE" | "CAUTIOUS" | "THREAT"
  analysis_result?: Record<string, unknown>
}

export async function fetchEmails(token: string, options?: { skipCache?: boolean }): Promise<Email[]> {
  // Return cached data if available and not skipping cache
  if (!options?.skipCache) {
    const cached = getCachedEmails()
    if (cached) {
      return cached
    }
  }
  
  // Fetch from API (limit to 20 most recent)
  const emails = await request<Email[]>("/api/emails?limit=20", { token })
  
  // Cache the result
  setCachedEmails(emails)
  
  return emails
}

export async function fetchEmailsWithRefresh(token: string): Promise<Email[]> {
  // Always fetch fresh data and update cache
  const emails = await request<Email[]>("/api/emails?limit=20", { token })
  setCachedEmails(emails)
  return emails
}

export async function syncEmails(token: string, googleToken: string): Promise<{ status: string, new_messages: number }> {
  return request("/api/emails/sync", {
    token,
    headers: { "X-Google-Token": googleToken },
    method: "POST"
    // Fetch defaults to GET, so we might need to change request util or pass method?
    // Wait, the request util only does GET? Let's check.
  })
}
