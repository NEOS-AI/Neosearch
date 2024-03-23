import Header from "@/app/components/header";
import ChatSection from "./components/chat-section";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center gap-10 p-24 background-gradient">
      <Header />
      <ChatSection />
    </main>
  );
}


// "use client";
// import { Footer } from "@/app/components/footer";
// import { Logo } from "@/app/components/logo";
// import { PresetQuery } from "@/app/components/preset-query";
// import { Search } from "@/app/components/search";
// import React from "react";

// export default function Home() {
//   return (
//     <div className="absolute inset-0 min-h-[500px] flex items-center justify-center">
//       <div className="relative flex flex-col gap-8 px-4 -mt-24">
//         <Logo></Logo>
//         <Search></Search>
//         <div className="flex gap-2 flex-wrap justify-center">
//           <PresetQuery query="Who said live long and prosper?"></PresetQuery>
//           <PresetQuery query="Why do we only see one side of the moon?"></PresetQuery>
//         </div>
//         <Footer></Footer>
//       </div>
//     </div>
//   );
// }