'use client'

import { Search as Search_LR, Github } from "lucide-react"
import { Button } from "@/app/components/ui/search/button"
import { Input } from "@/app/components/ui/search/input"


export function Search() {
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-4">
      <header className="flex justify-between items-center mb-8">
        <nav>
          <ul className="flex space-x-4">
            <li>Search</li>
            <li>Explore</li>
          </ul>
        </nav>
        <h1 className="text-2xl font-bold text-blue-400">STRACT</h1>
        <nav>
          <ul className="flex space-x-4">
            <li>Settings</li>
            <li>About</li>
            <li><Github className="w-5 h-5" /></li>
          </ul>
        </nav>
      </header>
      <main>
        <div className="max-w-3xl mx-auto">
          <div className="flex mb-4">
            <Input
              type="text"
              placeholder="stract github"
              className="flex-grow bg-gray-800 border-gray-700"
            />
            <Button className="ml-2 bg-blue-600 hover:bg-blue-700">search</Button>
          </div>
          <div className="text-sm text-gray-400 mb-4">
            Found 171 results in 0.38s
          </div>
          <div className="space-y-8">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="border-b border-gray-700 pb-4">
                <h2 className="text-blue-400 mb-2">Search Result Title {i}</h2>
                <p className="text-gray-300 mb-2">
                  This is a brief description of the search result. It provides a summary of the content found at this link.
                </p>
                <div className="text-gray-500 text-sm">https://example.com/result-{i}</div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}