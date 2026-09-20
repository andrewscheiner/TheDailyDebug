# Daily Warmup - Self-Hosting Guide (GitHub + Cloudflare + Supabase)

This app is a **Next.js 15 (App Router)** project. The Daily Warmup feature uses
**only Supabase** for data - the MongoDB pieces from the original template are
not used and can be ignored when self-hosting.

**What you'll set up:** GitHub (code) -> Cloudflare Workers (hosting, via the
OpenNext adapter) -> Supabase (database) -> your Cloudflare domain (one click).

---

## 1) Supabase: create the database

1. Create a project at https://database.new
2. Open **SQL Editor -> New query**, paste the contents of
   [`supabase/schema.sql`](./supabase/schema.sql), and click **Run**.
3. Go to **Settings -> API Keys** and copy three values:
   - **Project URL** -> `NEXT_PUBLIC_SUPABASE_URL`
   - **publishable key** (`sb_publishable_...`) -> `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
   - **secret key** (`sb_secret_...`) -> `SUPABASE_SECRET_KEY`  (keep this private!)

> The backend automatically loads 100 sample questions on first visit and locks
> in one random question per day (UTC). To use your own questions, insert them
> into the `questions` table *before* the first visit, or edit the `QUESTIONS`
> array in `app/api/[[...path]]/route.js`.

---

## 2) Run locally (optional, to verify)

```bash
cp .env.example .env.local     # then fill in your 3 Supabase values
npm install                    # or: yarn install
npm run dev                    # http://localhost:3000
```

---

## 3) Push the code to GitHub

Create a new GitHub repo and push this project to it.

```bash
git init
git add .
git commit -m "Daily Warmup app"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

> `.env` and `.env.local` are gitignored, so your secret key is **not** pushed.
> You'll set secrets in Cloudflare instead (next step).

---

## 4) Deploy to Cloudflare Workers (via GitHub)

This project already includes `wrangler.jsonc` and `open-next.config.ts`, and the
`@opennextjs/cloudflare` adapter is in `devDependencies`.

1. Cloudflare Dashboard -> **Workers & Pages -> Create -> Workers -> Import a repository**.
2. Select your GitHub repo. In the build settings:
   - **Build command:** `npx opennextjs-cloudflare build`
   - **Deploy command:** `npx wrangler deploy`
3. **Add your environment variables** (this is the important part). Add all three
   in the build/deploy **Variables and Secrets** section:
   | Name | Type | Value |
   |------|------|-------|
   | `NEXT_PUBLIC_SUPABASE_URL` | Text | your project URL |
   | `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | Text | your publishable key |
   | `SUPABASE_SECRET_KEY` | **Secret** | your secret key |
   Also add the **same three** under the deployed Worker's
   **Settings -> Variables and Secrets** so they're available at runtime (the API
   routes read them at request time). Do **not** encrypt/pre-encode the values.
4. Save & deploy. Cloudflare builds and gives you a URL like
   `https://daily-warmup.<your-subdomain>.workers.dev`. Open it to confirm the
   question loads and you can post an answer.

> CLI alternative: `npx wrangler login` then `npm run deploy`.

---

## 5) Connect your Cloudflare domain (one click)

Because your domain is already on Cloudflare, this is trivial - no manual DNS/CNAME:

1. Open your deployed Worker -> **Settings -> Domains & Routes -> Add -> Custom Domain**.
2. Enter the hostname you want, e.g. `warmup.yourdomain.com` (or the apex
   `yourdomain.com`).
3. Click **Add domain**. Cloudflare automatically creates the DNS record and
   provisions the SSL certificate. Within a minute or two your warmup page is
   live on your own domain. ✅

---

## Customizing

- **Redirect popup links:** edit the `REDIRECT_LINKS` array at the top of
  `app/page.js` (currently a `google.com` placeholder). Add as many links/labels
  as you like.
- **Questions:** edit the `QUESTIONS` array in
  `app/api/[[...path]]/route.js`, or manage them directly in the Supabase
  `questions` table.
- **"Day" boundary:** the daily question rotates at **UTC midnight**. If you need
  a local-time boundary, adjust the date logic in the route handler.

## Notes / gotchas

- Do **not** add `export const runtime = 'edge'` to the route file - the OpenNext
  adapter runs the full Node runtime (`nodejs_compat`).
- Keep `SUPABASE_SECRET_KEY` server-side only (it's never prefixed with
  `NEXT_PUBLIC_`). All Supabase access happens in the API routes.
- The `mongodb` dependency and `MONGO_URL` are unused by this feature.
