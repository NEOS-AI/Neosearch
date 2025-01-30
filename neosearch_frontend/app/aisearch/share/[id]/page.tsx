import { notFound } from 'next/navigation'
import { Chat } from '@/search_components/chat'
import { getSharedChat } from '@/lib/actions/chat'
import { convertToUIMessages } from '@/lib/search_utils'


export async function generateMetadata(props: {
  params: Promise<{ id: string }>
}) {
  const { id } = await props.params
  const chat = await getSharedChat(id)

  if (!chat || !chat.sharePath) {
    return notFound()
  }

  return {
    title: chat?.title.toString().slice(0, 50) || 'Search'
  }
}

export default async function SharePage(props: {
  params: Promise<{ id: string }>
}) {
  const { id } = await props.params
  const chat = await getSharedChat(id)
  // convertToUIMessages for useChat hook
  const messages = convertToUIMessages(chat?.messages || [])

  if (!chat || !chat.sharePath) {
    notFound()
  }

  return <Chat id={id} savedMessages={messages} />
}
