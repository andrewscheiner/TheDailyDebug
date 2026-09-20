import { defineCloudflareConfig } from '@opennextjs/cloudflare'

// Minimal config: the Daily Warmup app is fully dynamic (no ISR/caching needed),
// so no incremental cache override is required.
export default defineCloudflareConfig({})
