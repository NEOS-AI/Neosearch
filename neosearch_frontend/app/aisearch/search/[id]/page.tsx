import { notFound, redirect } from 'next/navigation'
import { Chat } from '@/search_components/chat'
import { getChat } from '@/lib/actions/chat'
import { convertToUIMessages } from '@/lib/search_utils'

export const maxDuration = 60

export async function generateMetadata(props: {
  params: Promise<{ id: string }>
}) {
  const { id } = await props.params
  const chat = await getChat(id, 'anonymous')
  return {
    title: chat?.title.toString().slice(0, 50) || 'Search'
  }
}

export default async function SearchPage(props: {
  params: Promise<{ id: string }>
}) {
  const userId = 'anonymous'
  const { id } = await props.params
  const chat = await getChat(id, userId)
  // convertToUIMessages for useChat hook
  const messages = convertToUIMessages(chat?.messages || [])

  if (!chat) {
    redirect('/aisearch')
  }

  if (chat?.userId !== userId) {
    notFound()
  }

  return <Chat id={id} savedMessages={messages} />
}
