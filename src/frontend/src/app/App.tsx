import { Route, Routes } from 'react-router'
import { ChatPage } from '@/features/chat/ChatPage'

export function App() {
  return (
    <Routes>
      <Route path="/" element={<ChatPage />} />
    </Routes>
  )
}
