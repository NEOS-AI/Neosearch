import { Mails } from "lucide-react";


export default function FooterMailMe({
    mailHref,
    isLoading,
    reload,
    stop,
} : {
    mailHref: string;
    isLoading?: boolean;
    stop?: () => void;
    reload?: () => void;
}) {
    return (
        <div className="flex gap-2 justify-center">
        <div>
          <a
            className="text-blue-500 font-medium inline-flex gap-1 items-center flex-nowrap text-nowrap"
            href={mailHref}
          >
            <Mails size={8} />
            Talk to us
          </a>
        </div>
        <div>if you need a performant and scalable AI Search!</div>
      </div>
    );
}