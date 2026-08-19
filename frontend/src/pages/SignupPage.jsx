import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { apiError } from '../api/client'

export default function SignupPage() {
  const { register } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
  })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function update(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await register(form)
      navigate('/')
    } catch (err) {
      setError(apiError(err, 'Could not create your account.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-card">
        <div className="auth-stub">
          <div className="brand">
            <div className="brand-mark">U</div>
            <span className="name">UniFind</span>
          </div>
          <h1>Create Account</h1>
          <p>Join your campus lost &amp; found network</p>
        </div>

        <div className="auth-perforation"></div>

        <div className="auth-body">
          {error && <div className="form-error">{error}</div>}
          <form onSubmit={onSubmit}>
            <div className="field">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                name="username"
                value={form.username}
                onChange={update}
                autoComplete="username"
                required
              />
            </div>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                name="email"
                type="email"
                value={form.email}
                onChange={update}
                autoComplete="email"
                required
              />
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                value={form.password}
                onChange={update}
                autoComplete="new-password"
                required
              />
            </div>
            <div className="field">
              <label htmlFor="password2">Confirm password</label>
              <input
                id="password2"
                name="password2"
                type="password"
                value={form.password2}
                onChange={update}
                autoComplete="new-password"
                required
              />
            </div>
            <button
              type="submit"
              className="btn btn-success btn-block"
              disabled={submitting}
            >
              {submitting ? 'Creating…' : 'Register'}
            </button>
          </form>
        </div>

        <div className="auth-footer-note">
          <p>
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
