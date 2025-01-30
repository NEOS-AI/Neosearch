import { Chat } from '@/search_components/chat'
import { generateId } from 'ai'


export default function Page() {
  const id = generateId();

  return <Chat id={id} />;
}
