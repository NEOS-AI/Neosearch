import { Sidebar } from '@/search_components/sidebar'
import type { Metadata, Viewport } from 'next'
import { Inter as FontSans } from 'next/font/google'
import './globals.css'


const fontSans = FontSans({
  subsets: ['latin'],
  variable: '--font-sans'
})

const title = 'Neosearch - AI search'
const description =
  'A fully open-source AI-powered answer engine with a generative UI.'

export const metadata: Metadata = {
  metadataBase: new URL('https://github.com/NEOS-AI/Neosearch'),
  title,
  description,
  openGraph: {
    title,
    description
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  minimumScale: 1,
  maximumScale: 1
}


export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode
}>) {
  const enableSaveChatHistory =
    process.env.NEXT_PUBLIC_ENABLE_SAVE_CHAT_HISTORY === 'true'
  return (
    <>
      {children}
      {enableSaveChatHistory && <Sidebar />}
    </>
  )
}
