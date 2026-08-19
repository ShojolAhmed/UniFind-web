import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { authApi, tokenStore } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true

    async function bootstrap() {
      if (!tokenStore.access) {
        setLoading(false)
        return
      }
      try {
        const res = await authApi.me()
        if (active) setUser(res.data)
      } catch {
        tokenStore.clear()
      } finally {
        if (active) setLoading(false)
      }
    }

    bootstrap()
    return () => {
      active = false
    }
  }, [])

  const login = useCallback(async (credentials) => {
    const res = await authApi.login(credentials)
    tokenStore.set({ access: res.data.access, refresh: res.data.refresh })
    setUser(res.data.user)
    return res.data.user
  }, [])

  const register = useCallback(async (data) => {
    const res = await authApi.register(data)
    tokenStore.set({ access: res.data.access, refresh: res.data.refresh })
    setUser(res.data.user)
    return res.data.user
  }, [])

  const logout = useCallback(() => {
    tokenStore.clear()
    setUser(null)
  }, [])

  const value = { user, loading, login, register, logout, setUser }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
