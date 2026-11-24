import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MapPin, AlertCircle, ArrowRight, ShieldCheck, UserCheck } from 'lucide-react';
import { authApi } from '../services/api';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('asha@demo.in');
  const [password, setPassword] = useState('DemoPass123!');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Quick Demo Accounts from Part H & README
  const demoAccounts = [
    { name: 'Asha Reddy', role: 'safety_analyst', roleLabel: 'Road Safety Analyst', email: 'asha@demo.in' },
    { name: 'Ravi Kumar', role: 'police_officer', roleLabel: 'Traffic Police Officer', email: 'ravi@demo.in' },
    { name: 'Sana Fatima', role: 'authority_official', roleLabel: 'Road Authority Official', email: 'sana@demo.in' },
    { name: 'Dr. Kiran Rao', role: 'admin', roleLabel: 'Administrator', email: 'admin@demo.in' },
  ];

  const handleQuickDemoLogin = (account: typeof demoAccounts[0]) => {
    setEmail(account.email);
    setPassword('DemoPass123!');
    localStorage.setItem(
      'rah_user',
      JSON.stringify({
        fullName: account.name,
        email: account.email,
        role: account.role,
        roleLabel: account.roleLabel,
        organisation: 'Telangana Transport & Police',
        status: 'active',
      })
    );
    localStorage.setItem('rah_token', 'demo-jwt-token-active-session');
    navigate('/dashboard');
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await authApi.login(email, password);
      localStorage.setItem('rah_token', res.access_token);
      localStorage.setItem('rah_user', JSON.stringify(res.user));
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-card">
      {/* Left Brand Panel - Asphalt */}
      <div className="md:w-5/12 bg-asphalt text-white p-8 md:p-14 flex flex-col justify-between relative overflow-hidden">
        {/* Ambient Road Graphic */}
        <div className="absolute inset-0 pointer-events-none opacity-20 flex items-center justify-center">
          <svg className="w-[600px] h-[600px]" viewBox="0 0 400 400">
            <circle cx="200" cy="200" r="160" fill="none" stroke="#C62F2A" strokeWidth="2" strokeDasharray="6 6" />
            <circle cx="200" cy="200" r="120" fill="none" stroke="#E2762B" strokeWidth="2" />
            <circle cx="200" cy="200" r="80" fill="none" stroke="#E7B416" strokeWidth="2" />
            <circle cx="200" cy="200" r="40" fill="none" stroke="#3E8E62" strokeWidth="2" />
            <line x1="200" y1="0" x2="200" y2="400" stroke="#F5B800" strokeWidth="3" strokeDasharray="12 12" />
          </svg>
        </div>

        <div className="relative z-10">
          <div
            onClick={() => navigate('/')}
            className="flex items-center gap-3 cursor-pointer mb-12"
          >
            <div className="w-9 h-9 rounded-lg bg-lane flex items-center justify-center text-asphalt shadow-md">
              <MapPin className="w-5 h-5 text-asphalt fill-asphalt" />
            </div>
            <span className="text-[17px] font-semibold tracking-tight">
              Hotspot Mapping
            </span>
          </div>

          <h1 className="text-3xl md:text-4xl font-semibold leading-tight mb-4">
            Find where crashes cluster. Fix those places first.
          </h1>
          <p className="text-[15px] text-[#C4C9CF] leading-relaxed max-w-md">
            Hotspot Mapping brings police accident logs and road authority work orders into one shared, evidence-backed workspace.
          </p>
        </div>

        <div className="relative z-10 pt-12 text-xs text-[#8E959C]">
          Team 12 · Anurag University · Decision-Support Platform BRD-RAH-001
        </div>
      </div>

      {/* Right Form Panel - Paper / Card */}
      <div className="md:w-7/12 flex items-center justify-center p-6 md:p-14 bg-paper">
        <div className="w-full max-w-md bg-card border border-line rounded-card p-8 md:p-10 shadow-sm">
          <h2 className="text-2xl font-semibold text-ink mb-1">
            Sign in
          </h2>
          <p className="text-[13px] text-muted mb-6">
            Use your department account to continue.
          </p>

          {error && (
            <div
              className={`mb-5 p-3 rounded-btn text-[13px] flex items-start gap-2.5 ${
                error.toLowerCase().includes('waiting for approval')
                  ? 'bg-warn-bg text-warn-text border border-[#FDE68A]'
                  : 'bg-[#FEE2E2] text-[#991B1B] border border-[#FCA5A5]'
              }`}
            >
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-[12.5px] font-medium text-muted mb-1.5">
                Email
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@department.gov.in"
                className="w-full px-3.5 py-2.5 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:outline-none focus:ring-2 focus:ring-lane focus:border-lane"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-[12.5px] font-medium text-muted">
                  Password
                </label>
                <a
                  href="#forgot"
                  onClick={(e) => {
                    e.preventDefault();
                    alert('Please contact your department administrator to reset your password.');
                  }}
                  className="text-[12px] text-muted hover:text-ink hover:underline"
                >
                  Forgot password?
                </a>
              </div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••"
                className="w-full px-3.5 py-2.5 rounded-btn border border-line bg-card text-ink text-[13.5px] focus:outline-none focus:ring-2 focus:ring-lane focus:border-lane"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 rounded-btn bg-lane text-ink font-semibold text-[14px] hover:brightness-105 active:scale-[0.99] transition-all shadow-sm disabled:opacity-50"
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>
          </form>

          {/* Divider */}
          <div className="relative my-5">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-line" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-3 bg-card text-muted">or</span>
            </div>
          </div>

          {/* Public Map Link Button */}
          <button
            onClick={() => navigate('/public')}
            className="w-full py-2.5 rounded-btn border border-line bg-card text-ink font-medium text-[13.5px] hover:bg-paper transition-colors"
          >
            View public hotspot map
          </button>
          <p className="text-[11.5px] text-muted text-center mt-1.5">
            The public map shows combined, anonymized figures only.
          </p>

          {/* Demo Account Switcher */}
          <div className="mt-6 pt-5 border-t border-line">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-muted uppercase tracking-wider mb-2.5">
              <UserCheck className="w-3.5 h-3.5 text-lane" />
              <span>Quick Demo Sign In</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {demoAccounts.map((acc) => (
                <button
                  key={acc.email}
                  type="button"
                  onClick={() => handleQuickDemoLogin(acc)}
                  className="p-2 rounded-btn border border-line text-left bg-paper hover:bg-[#E9EBE4] hover:border-lane transition-colors"
                >
                  <div className="text-[12px] font-semibold text-ink truncate">
                    {acc.name}
                  </div>
                  <div className="text-[10.5px] text-muted truncate">
                    {acc.roleLabel}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-5 text-center text-[13px] text-muted">
            New to the team?{' '}
            <Link to="/signup" className="font-semibold text-[#8A6A00] hover:underline">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
