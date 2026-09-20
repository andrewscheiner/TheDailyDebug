import './globals.css'

export const metadata = {
  title: 'The Daily Debug',
  description: 'Answer the daily warmup question and see what everyone else said.',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
