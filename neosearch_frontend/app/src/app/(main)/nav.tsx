'use client';

import { listChatEngines } from '@/api/chat-engines';
import { listLlms } from '@/api/llms';
import { useAuth } from '@/components/auth/AuthProvider';
import { ChatNewDialog } from '@/components/chat/chat-new-dialog';
import { ChatsHistory } from '@/components/chat/chats-history';
import { useKnowledgeBases } from '@/components/knowledge-base/hooks';
import { type NavGroup, SiteNav } from '@/components/site-nav';
import { SiteNavFooter } from '@/components/site-nav-footer';
import { useBootstrapStatus } from '@/components/system/BootstrapStatusProvider';
import { Button } from '@/components/ui/button';
import { Drawer, DrawerContent, DrawerTrigger } from '@/components/ui/drawer';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useHref } from '@/components/use-href';
import { ActivitySquareIcon, AlertTriangleIcon, BinaryIcon, BotMessageSquareIcon, BrainCircuitIcon, CogIcon, ComponentIcon, FilesIcon, HomeIcon, KeyRoundIcon, LibraryBigIcon, LibraryIcon, MenuIcon, MessageCircleQuestionIcon, MessagesSquareIcon, ShuffleIcon } from 'lucide-react';
import Link from 'next/link';
import type { ReactNode } from 'react';
import useSWR from 'swr';

export function Nav () {
  const { required } = useBootstrapStatus();
  const href = useHref();
  const auth = useAuth();
  const user = auth.me;
  const isLoggedIn = !!user; // TODO: wait for server

  const disableIfNotAuthenticated = !isLoggedIn ? <><Link className="font-semibold underline" href={`/auth/login?callbackUrl=${encodeURIComponent(href)}`}>Login</Link> to continue</> : false;

  const groups: NavGroup[] = [
    {
      items: [
        { custom: true, key: 'new-chat', children: <ChatNewDialog /> },
        { href: '/', title: 'Home', icon: HomeIcon, exact: true },
        { href: '/c', title: 'Conversations', exact: true, icon: MessagesSquareIcon, disabled: disableIfNotAuthenticated },
        { custom: true, key: 'history', children: <ChatsHistory /> },
      ],
    },
  ];

  if (user?.is_superuser) {
    groups.push({
      title: 'Admin',
      items: [
        { href: '/stats/trending', title: 'Dashboard', icon: ActivitySquareIcon },
        { href: '/knowledge-bases', title: 'Knowledge Bases', icon: LibraryBigIcon, details: !required.knowledge_base ? <NavWarningDetails>You need to configure at least one knowledge base.</NavWarningDetails> : <KnowledgeBaseNavDetails /> },
        { href: '/chat-engines', title: 'Chat Engines', icon: BotMessageSquareIcon, details: <ChatEnginesNavDetails /> },
        {
          parent: true,
          key: 'models',
          title: 'Models',
          icon: ComponentIcon,
          details: (!required.default_llm || !required.default_embedding_model) && <NavWarningDetails />,
          children: [
            { href: '/llms', title: 'LLMs', icon: BrainCircuitIcon, details: !required.default_llm ? <NavWarningDetails>You need to configure at least one Default LLM.</NavWarningDetails> : <LlmsNavDetails /> },
            { href: '/embedding-models', title: 'Embedding Models', icon: BinaryIcon, details: !required.default_embedding_model && <NavWarningDetails>You need to configure at least one Default Embedding Model.</NavWarningDetails> },
            { href: '/reranker-models', title: 'Reranker Models', icon: ShuffleIcon },
          ],
        },
        { href: '/feedbacks', title: 'Feedbacks', icon: MessageCircleQuestionIcon },
        { href: '/site-settings', title: 'Settings', icon: CogIcon },
      ],
      sectionProps: { className: 'mt-auto mb-0' },
    });

    groups.push({
      title: 'Legacy',
      items: [
        { href: '/documents', title: 'Documents', icon: FilesIcon },
        { href: '/datasources', title: 'Datasources', icon: LibraryIcon, details: !required.datasource && <NavWarningDetails>You need to configure at least one Datasource.</NavWarningDetails> },
      ],
      sectionProps: { className: 'mt-auto mb-0' },
    });
  }

  if (user?.is_superuser) {
    groups.push({
      title: 'Account',
      items: [
        { href: '/api-keys', title: 'API Keys', icon: KeyRoundIcon },
      ],
    });
  }

  return (
    <>
      <SiteNav groups={groups} />
    </>
  );
}

export function NavDrawer () {
  return (
    <Drawer>
      <DrawerTrigger className="flex md:hidden flex-shrink-0" asChild>
        <Button variant="ghost" size="icon">
          <MenuIcon className="w-4 h-4" />
        </Button>
      </DrawerTrigger>
      <DrawerContent className="px-2">
        <ScrollArea className="h-[50vh]">
          <Nav />
          <SiteNavFooter className="bg-background" />
        </ScrollArea>
      </DrawerContent>
    </Drawer>
  );
}

function NavWarningDetails ({ children }: { children?: ReactNode }) {
  if (!children) {
    return <AlertTriangleIcon className="text-yellow-600 dark:text-yellow-400 size-4" />;
  }
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>
          <AlertTriangleIcon className="text-yellow-600 dark:text-yellow-400 size-4" />
        </TooltipTrigger>
        <TooltipContent>
          {children}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

function CountSpan ({ children }: { children?: ReactNode }) {
  return <span className="text-xs opacity-50 font-normal inline-block mr-1">{children}</span>;
}

function KnowledgeBaseNavDetails () {
  const { knowledgeBases, isLoading } = useKnowledgeBases(0, 10);

  if (isLoading) {
    return <Skeleton className="flex-shrink-0 w-6 h-4" />;
  }

  return <CountSpan>{knowledgeBases?.total}</CountSpan>;
}

function ChatEnginesNavDetails () {
  const { data, isLoading } = useSWR('api.chat-engines.list-all', () => listChatEngines({ page: 1, size: 100 }));

  if (isLoading) {
    return <Skeleton className="flex-shrink-0 w-6 h-4" />;
  }

  return <CountSpan>{data?.total}</CountSpan>;
}

function LlmsNavDetails () {
  const { data, isLoading } = useSWR('api.chat-engines.list?page=0&size=10', () => listLlms({ page: 1, size: 10 }));

  if (isLoading) {
    return <Skeleton className="flex-shrink-0 w-6 h-4" />;
  }

  return <CountSpan>{data?.total}</CountSpan>;
}
