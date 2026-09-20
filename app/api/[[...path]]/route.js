import { NextResponse } from 'next/server'
import { supabaseAdmin } from '@/lib/supabase/server'

export const dynamic = 'force-dynamic'

const json = (body, status = 200) =>
  NextResponse.json(body, { status, headers: { 'Cache-Control': 'no-store' } })

// Extract the API sub-path regardless of any basePath prefix (e.g. /daily-debug).
function getApiPath(request) {
  const p = new URL(request.url).pathname
  const i = p.indexOf('/api')
  return (i >= 0 ? p.slice(i + 4) : p).replace(/^\/+/, '').replace(/\/+$/, '')
}

// ---- 100 sample "do now" warmup questions -------------------------------
const QUESTIONS = [
  'What is your favorite ice cream flavor?',
  'What is your favorite animal?',
  'If you could have any superpower, what would it be?',
  'What is your favorite season and why?',
  'What is the best movie you have ever seen?',
  'What is your favorite food?',
  'If you could travel anywhere in the world, where would you go?',
  'What is your favorite color?',
  'What is your favorite hobby?',
  'What is one thing that always makes you smile?',
  'What is your favorite sport to play or watch?',
  'If you had three wishes, what would they be?',
  'What is your favorite subject in school?',
  'What is the best gift you have ever received?',
  'What is your favorite thing to do on the weekend?',
  'If you could meet any famous person, who would it be?',
  'What is your favorite type of music?',
  'What is your dream job?',
  'What is your favorite holiday?',
  'What is one thing you are really good at?',
  'What is your favorite book?',
  'If you could be any age, what age would you choose?',
  'What is your favorite thing about yourself?',
  'What is the funniest thing that happened to you this week?',
  'What is your favorite kind of weather?',
  'If you could have any pet, what would it be?',
  'What is your favorite dessert?',
  'What is one place you would love to visit someday?',
  'What is your favorite way to relax?',
  'What is your favorite video game or board game?',
  'If you could invent something, what would it be?',
  'What is your favorite thing to eat for breakfast?',
  'What is a skill you would like to learn?',
  'What is your favorite time of day?',
  'What makes a good friend?',
  'What is your favorite thing about school?',
  'If you won a million dollars, what would you do first?',
  'What is your favorite type of weather activity (snow, rain, sun)?',
  'What is the coolest fact you know?',
  'What is your favorite thing to draw or create?',
  'If you could speak any language, which would you choose?',
  'What is your favorite childhood memory?',
  'What is your favorite candy?',
  'What is one goal you have for this year?',
  'What is your favorite thing to do outside?',
  'If you could live in any time period, when would it be?',
  'What is your favorite kind of pizza?',
  'Who is someone you look up to and why?',
  'What is your favorite app or website?',
  'What is something new you tried recently?',
  'What is your favorite thing about your hometown?',
  'If you could design your own school, what would it have?',
  'What is your favorite smell?',
  'What is a movie you could watch over and over?',
  'What is your favorite thing to do with your family?',
  'If you could be an expert at one thing, what would it be?',
  'What is your favorite drink?',
  'What is the best advice anyone has given you?',
  'What is your favorite kind of shoes?',
  'What is one thing on your bucket list?',
  'What is your favorite way to spend a rainy day?',
  'If animals could talk, which would be the funniest?',
  'What is your favorite emoji and why?',
  'What is a food you could never give up?',
  'What is your favorite thing to do after school?',
  'If you could switch lives with anyone for a day, who would it be?',
  'What is your favorite type of weather to sleep in?',
  'What is the most beautiful place you have ever seen?',
  'What is your favorite kind of cookie?',
  'What is something that made you laugh today?',
  'If you could add one new holiday, what would it celebrate?',
  'What is your favorite thing about summer?',
  'What is a talent you wish you had?',
  'What is your favorite ride at an amusement park?',
  'What is your favorite thing to cook or bake?',
  'If you could be any fictional character, who would you be?',
  'What is your favorite kind of sandwich?',
  'What is a place that feels like home to you?',
  'What is your favorite way to stay active?',
  'What is one word that describes you best?',
  'What is your favorite thing to collect?',
  'If you could have dinner with anyone from history, who would it be?',
  'What is your favorite kind of weather sound (thunder, rain, wind)?',
  'What is your favorite thing about the weekend?',
  'What is a song you know all the words to?',
  'If you could visit outer space, where would you go?',
  'What is your favorite thing to do when you are bored?',
  'What is your favorite kind of fruit?',
  'What is something you are proud of?',
  'What is your favorite thing about your best friend?',
  'If you could change one thing about the world, what would it be?',
  'What is your favorite thing to watch on TV?',
  'What is your favorite kind of vegetable?',
  'What is a dream you had that you still remember?',
  'What is your favorite thing to do in the morning?',
  'If you could be really tall or really tiny, which would you pick?',
  'What is your favorite thing about nature?',
  'What is a random act of kindness you could do today?',
  'What is your favorite way to end the day?'
]

// ---- Basic profanity / inappropriate name filter ------------------------
const BAD_WORDS = [
  'fuck','shit','bitch','asshole','bastard','dick','pussy','cunt','slut','whore',
  'nigger','nigga','faggot','fag','retard','cock','damn','crap','piss','wanker',
  'douche','twat','prick','jerkoff','motherfucker','bullshit','dumbass','jackass',
  'nazi','rape','porn','sex','xxx'
]
function isNameInappropriate(name) {
  const lower = ' ' + name.toLowerCase().replace(/[^a-z0-9]+/g, ' ') + ' '
  return BAD_WORDS.some((w) => lower.includes(' ' + w + ' ') || name.toLowerCase().includes(w))
}

function isSetupError(error) {
  const msg = (error?.message || '').toLowerCase()
  return (
    error?.code === '42P01' ||
    msg.includes('does not exist') ||
    msg.includes('could not find the table') ||
    msg.includes('schema cache')
  )
}

async function ensureSeeded(db) {
  const { count, error } = await db.from('questions').select('id', { count: 'exact', head: true })
  if (error) throw error
  if ((count || 0) === 0) {
    const rows = QUESTIONS.map((prompt) => ({ prompt }))
    const { error: insErr } = await db.from('questions').insert(rows)
    if (insErr) throw insErr
  }
}

async function getOrCreateDaily(db) {
  const today = new Date().toISOString().slice(0, 10)
  let { data, error } = await db
    .from('daily_questions')
    .select('selected_on,question_id,questions(id,prompt)')
    .eq('selected_on', today)
    .maybeSingle()
  if (error) throw error
  if (data) return data

  const { data: qs, error: qErr } = await db.from('questions').select('id')
  if (qErr) throw qErr
  if (!qs || qs.length === 0) return null
  const pick = qs[Math.floor(Math.random() * qs.length)].id

  // Insert today's selection; ignore duplicate if another request beat us to it.
  await db.from('daily_questions').insert({ selected_on: today, question_id: pick })

  const { data: d2, error: e2 } = await db
    .from('daily_questions')
    .select('selected_on,question_id,questions(id,prompt)')
    .eq('selected_on', today)
    .maybeSingle()
  if (e2) throw e2
  return d2
}

export async function GET(request) {
  const path = getApiPath(request)
  let db
  try {
    db = supabaseAdmin()
  } catch (e) {
    return json({ error: e.message, needsSetup: true }, 500)
  }

  try {
    if (path === 'daily-question') {
      await ensureSeeded(db)
      const daily = await getOrCreateDaily(db)
      return json({ dailyQuestion: daily })
    }

    if (path === 'feed') {
      const limit = Math.min(
        Math.max(Number(new URL(request.url).searchParams.get('limit')) || 100, 1),
        200
      )
      const { data, error } = await db
        .from('answers')
        .select('id,question_id,answer,display_name,created_at')
        .order('created_at', { ascending: false })
        .limit(limit)
      if (error) throw error
      return json({ answers: data || [] })
    }

    if (path === 'health' || path === '') {
      const { error } = await db.from('questions').select('id', { head: true, count: 'exact' })
      if (error && isSetupError(error)) return json({ ok: false, needsSetup: true }, 200)
      if (error) throw error
      return json({ ok: true })
    }

    return json({ error: 'Not found' }, 404)
  } catch (error) {
    if (isSetupError(error)) return json({ error: error.message, needsSetup: true }, 200)
    return json({ error: error.message }, 500)
  }
}

export async function POST(request) {
  const path = getApiPath(request)
  let db
  try {
    db = supabaseAdmin()
  } catch (e) {
    return json({ error: e.message, needsSetup: true }, 500)
  }

  if (path !== 'answers') return json({ error: 'Not found' }, 404)

  const body = await request.json().catch(() => null)
  const answer = typeof body?.answer === 'string' ? body.answer.trim() : ''
  let displayName = typeof body?.displayName === 'string' ? body.displayName.trim() : ''
  if (!displayName) displayName = 'Anonymous'
  const questionId = Number(body?.questionId)

  // Honeypot: bots fill hidden fields.
  if (body?.website) return json({ ok: true })

  if (!Number.isInteger(questionId)) return json({ error: 'Invalid question.' }, 400)
  if (!answer) return json({ error: 'Please write an answer before submitting.' }, 400)
  if (answer.length > 2000) return json({ error: 'Answer is too long (max 2000 characters).' }, 400)
  if (displayName.length > 80) return json({ error: 'Name is too long (max 80 characters).' }, 400)
  if (isNameInappropriate(displayName))
    return json({ error: 'Please choose an appropriate display name.', field: 'name' }, 400)

  try {
    // Confirm this is actually today's question before accepting the answer.
    const today = new Date().toISOString().slice(0, 10)
    const { data: selected, error: selErr } = await db
      .from('daily_questions')
      .select('question_id')
      .eq('selected_on', today)
      .maybeSingle()
    if (selErr) throw selErr
    if (!selected || selected.question_id !== questionId)
      return json({ error: "That is not today's question. Please refresh the page." }, 400)

    const { data, error } = await db
      .from('answers')
      .insert({ question_id: questionId, answer, display_name: displayName })
      .select('id,question_id,answer,display_name,created_at')
      .single()
    if (error) throw error
    return json({ answer: data }, 201)
  } catch (error) {
    if (isSetupError(error)) return json({ error: error.message, needsSetup: true }, 200)
    return json({ error: error.message }, 500)
  }
}
