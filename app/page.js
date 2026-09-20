'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Sparkles, Send, Users, ExternalLink, Loader2, RefreshCw } from 'lucide-react'

// App base path (must match next.config.js basePath). Client fetches include it.
const BASE_PATH = '/daily-debug'

// ---- Configure your post-submit redirect links here ---------------------
const REDIRECT_LINKS = [
  { url: 'https://google.com', label: 'Continue to Google \u2192' },
]
// -------------------------------------------------------------------------

function initials(name) {
  const n = (name || 'A').trim()
  const parts = n.split(/\s+/).slice(0, 2)
  return parts.map((p) => p[0]?.toUpperCase() || '').join('') || 'A'
}

function timeAgo(iso) {
  const d = new Date(iso).getTime()
  const s = Math.max(1, Math.floor((Date.now() - d) / 1000))
  if (s < 60) return `${s}s ago`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

const AVATAR_COLORS = [
  'bg-rose-500','bg-orange-500','bg-amber-500','bg-emerald-500',
  'bg-teal-500','bg-sky-500','bg-indigo-500','bg-violet-500','bg-fuchsia-500',
]
function colorFor(str) {
  let h = 0
  for (let i = 0; i < (str || '').length; i++) h = (h * 31 + str.charCodeAt(i)) % AVATAR_COLORS.length
  return AVATAR_COLORS[Math.abs(h) % AVATAR_COLORS.length]
}

export default function App() {
  const [daily, setDaily] = useState(null)
  const [answers, setAnswers] = useState([])
  const [text, setText] = useState('')
  const [name, setName] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [needsSetup, setNeedsSetup] = useState(false)
  const [loading, setLoading] = useState(true)
  const [showDialog, setShowDialog] = useState(false)
  const feedRef = useRef(null)

  const loadDaily = useCallback(async () => {
    try {
      const r = await fetch(`${BASE_PATH}/api/daily-question`, { cache: 'no-store' })
      const b = await r.json()
      if (b.needsSetup) { setNeedsSetup(true); return }
      setDaily(b.dailyQuestion || null)
    } catch (e) {
      /* ignore transient */
    }
  }, [])

  const loadFeed = useCallback(async () => {
    try {
      const r = await fetch(`${BASE_PATH}/api/feed?limit=200`, { cache: 'no-store' })
      const b = await r.json()
      if (b.needsSetup) { setNeedsSetup(true); return }
      setAnswers(b.answers || [])
    } catch (e) {
      /* ignore transient */
    }
  }, [])

  useEffect(() => {
    ;(async () => {
      await Promise.all([loadDaily(), loadFeed()])
      setLoading(false)
    })()
    const t = setInterval(loadFeed, 6000)
    return () => clearInterval(t)
  }, [loadDaily, loadFeed])

  async function submit(e) {
    e.preventDefault()
    setError('')
    if (!text.trim()) { setError('Please write an answer first.'); return }
    setBusy(true)
    try {
      const r = await fetch(`${BASE_PATH}/api/answers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          questionId: daily?.question_id,
          answer: text,
          displayName: name,
        }),
      })
      const b = await r.json()
      if (!r.ok) { setError(b.error || 'Something went wrong. Please try again.'); return }
      setText('')
      await loadFeed()
      setShowDialog(true)
    } catch (e) {
      setError('Network error. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  const prompt = daily?.questions?.prompt

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50 via-white to-white">
      {/* Header */}
      <header className="border-b bg-white/70 backdrop-blur sticky top-0 z-10">
        <div className="container flex items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white">
              <Sparkles className="h-5 w-5" />
            </div>
            <span className="text-lg font-semibold tracking-tight">Daily Warmup</span>
          </div>
          <Badge variant="secondary" className="gap-1">
            <Users className="h-3.5 w-3.5" /> {answers.length} answered today
          </Badge>
        </div>
      </header>

      <main className="container max-w-3xl py-8 md:py-12 space-y-8">
        {needsSetup && (
          <Card className="border-amber-300 bg-amber-50">
            <CardHeader>
              <CardTitle className="text-amber-900">Almost there — finish the database setup</CardTitle>
            </CardHeader>
            <CardContent className="text-amber-900/90 text-sm">
              Your Supabase tables haven’t been created yet. Run the setup SQL provided
              in the Supabase SQL Editor, then refresh this page.
            </CardContent>
          </Card>
        )}

        {/* Question card */}
        <Card className="overflow-hidden border-0 shadow-lg shadow-indigo-100">
          <div className="bg-gradient-to-r from-indigo-600 to-violet-600 px-6 py-2">
            <span className="text-xs font-medium uppercase tracking-wider text-indigo-100">
              Today’s Question
            </span>
          </div>
          <CardContent className="pt-6">
            {loading ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" /> Loading today’s question…
              </div>
            ) : (
              <h1 className="text-2xl md:text-3xl font-bold leading-snug text-slate-900">
                {prompt || 'No question available yet.'}
              </h1>
            )}

            <form onSubmit={submit} className="mt-6 space-y-3">
              {/* honeypot */}
              <input type="text" name="website" className="hidden" tabIndex={-1} autoComplete="off" />
              <Input
                value={name}
                maxLength={80}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name or nickname (optional)"
              />
              <Textarea
                value={text}
                maxLength={2000}
                onChange={(e) => setText(e.target.value)}
                placeholder="Type your answer here…"
                rows={3}
              />
              {error && <p className="text-sm text-rose-600">{error}</p>}
              <Button type="submit" disabled={busy || !daily} className="w-full sm:w-auto">
                {busy ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Posting…</>
                ) : (
                  <><Send className="mr-2 h-4 w-4" /> Post my answer</>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Live feed */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Everyone’s answers</h2>
            <button
              onClick={loadFeed}
              className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-slate-900"
            >
              <RefreshCw className="h-3.5 w-3.5" /> Refresh
            </button>
          </div>

          <div ref={feedRef} className="space-y-3">
            {answers.length === 0 && !loading && (
              <Card className="border-dashed">
                <CardContent className="py-10 text-center text-muted-foreground">
                  No answers yet — be the first to share yours! 🌟
                </CardContent>
              </Card>
            )}
            {answers.map((a) => (
              <Card key={a.id} className="transition hover:shadow-md">
                <CardContent className="flex gap-3 py-4">
                  <div
                    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-semibold text-white ${colorFor(a.display_name)}`}
                  >
                    {initials(a.display_name)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-900">{a.display_name}</span>
                      <span className="text-xs text-muted-foreground">{timeAgo(a.created_at)}</span>
                    </div>
                    <p className="mt-1 whitespace-pre-wrap break-words text-slate-700">{a.answer}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </main>

      {/* Post-submit redirect dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-indigo-600" /> Thanks for your answer!
            </DialogTitle>
            <DialogDescription>
              Your response has been posted to the wall. Here’s where to go next:
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2 py-2">
            {REDIRECT_LINKS.map((link) => (
              <a key={link.url} href={link.url} target="_blank" rel="noopener noreferrer">
                <Button variant="outline" className="w-full justify-between">
                  {link.label}
                  <ExternalLink className="h-4 w-4" />
                </Button>
              </a>
            ))}
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setShowDialog(false)}>
              Stay here
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
