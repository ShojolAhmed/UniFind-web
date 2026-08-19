import { useEffect, useState } from 'react'
import { NavLink, Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { notificationsApi } from '../api/client'

function navClass({ isActive }) {
  return isActive ? 'nav-link active' : 'nav-link'
}

function addClass({ isActive }) {
  return isActive ? 'nav-link primary active' : 'nav-link primary'
}

export default function Layout() {
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const [unread, setUnread] = useState(0)
  const location = useLocation()
  const navigate = useNavigate()

  // Close the mobile drawer on navigation.
  useEffect(() => {
    setOpen(false)
  }, [location.pathname])

  // Keep the notifications badge fresh.
  useEffect(() => {
    let active = true
    async function load() {
      if (!user) {
        setUnread(0)
        return
      }
      try {
        const res = await notificationsApi.unreadCount()
        if (active) setUnread(res.data.unread)
      } catch {
        /* ignore badge errors */
      }
    }
    load()
    return () => {
      active = false
    }
  }, [user, location.pathname])

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <div className="app-shell">
      <div className="topnav-mobile">
        <button
          className="hamburger"
          onClick={() => setOpen(true)}
          aria-label="Open menu"
        >
          ☰
        </button>
        <div className="brand-mini">
          <span className="brand-mark-mini">U</span> UniFind
        </div>
      </div>

      <div
        className={`sidebar-backdrop ${open ? 'visible' : ''}`}
        onClick={() => setOpen(false)}
      ></div>

      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <div className="brand">
          <div className="brand-mark">U</div>
          <div className="brand-text">
            <h1>UniFind</h1>
            <p>Lost &amp; Found</p>
          </div>
        </div>

        <nav className="nav-group">
          <NavLink to="/add" className={addClass}>
            + Add Item
          </NavLink>
          <NavLink to="/" end className={navClass}>
            Home
          </NavLink>

          {user && (
            <>
              <div className="nav-label">Account</div>
              <NavLink to="/notifications" className={navClass}>
                Notifications
                {unread > 0 && <span className="nav-badge">{unread}</span>}
              </NavLink>
              <NavLink to="/dashboard" className={navClass}>
                Dashboard
              </NavLink>
            </>
          )}
        </nav>

        <div className="sidebar-footer">
          {user ? (
            <button className="logout-btn" onClick={handleLogout}>
              Logout · {user.username}
            </button>
          ) : (
            <>
              <Link className="nav-link" to="/login">
                Login
              </Link>
              <Link className="nav-link primary" to="/signup">
                Sign Up
              </Link>
            </>
          )}
        </div>
      </aside>

      <div className="main">
        <Outlet />

        <footer className="site-footer">
          <p>UniFind: A University-Based Lost &amp; Found Management System</p>
          <p>&copy; 2026 UniFind. All Rights Reserved.</p>
        </footer>
      </div>
    </div>
  )
}
